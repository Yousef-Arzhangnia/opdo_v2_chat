# System Prompt Management API

This document describes the system prompt management endpoints added to the FastAPI backend.

## Overview

The system prompt consists of two parts:

1. **Base System Prompt (Hardcoded)**: Contains the optical design schema, JSON structure requirements, and design rules. This is always included and cannot be modified to ensure valid optical designs are generated.

2. **Custom Instructions (File-based)**: Additional instructions that are appended to the base prompt. These can be dynamically managed through API endpoints without requiring backend deployments.

The final system prompt sent to Claude is: `BASE_PROMPT + CUSTOM_INSTRUCTIONS + PER_REQUEST_INSTRUCTIONS`

## Endpoints

### GET /api/system-prompt

Retrieve the current custom instructions (not the full prompt, just the custom part).

**Response:**
```json
{
  "content": "Your custom instructions here..."
}
```

Returns an empty string if no custom instructions are set.

**Example:**
```bash
curl https://opdo-v2-chat.onrender.com/api/system-prompt
```

**Python example:**
```python
import requests

response = requests.get("https://opdo-v2-chat.onrender.com/api/system-prompt")
data = response.json()
print(data["content"])
```

---

### POST /api/system-prompt

Save custom instructions to append to the base system prompt.

**Request Body:**
```json
{
  "content": "Custom instructions to append..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Custom instructions saved successfully"
}
```

**Notes:**
- The custom instructions will be appended to the hardcoded base prompt
- You can send an empty string to clear custom instructions
- The base prompt (schema + rules) is always included and cannot be modified

**Example:**
```bash
curl -X POST https://opdo-v2-chat.onrender.com/api/system-prompt \
  -H "Content-Type: application/json" \
  -d '{"content": "You are an expert optical engineer..."}'
```

**Python example:**
```python
import requests

custom_instructions = """Focus on compact lens designs.
Prefer standard materials like BK7 when possible.
Provide detailed explanations for material choices."""

response = requests.post(
    "https://opdo-v2-chat.onrender.com/api/system-prompt",
    json={"content": custom_instructions}
)
data = response.json()
print(data["message"])
```

---

### DELETE /api/system-prompt

Clear all custom instructions and revert to using only the base system prompt.

**Response:**
```json
{
  "success": true,
  "message": "Custom instructions cleared successfully"
}
```

**Example:**
```bash
curl -X DELETE https://opdo-v2-chat.onrender.com/api/system-prompt
```

**Python example:**
```python
import requests

response = requests.delete("https://opdo-v2-chat.onrender.com/api/system-prompt")
data = response.json()
print(data["message"])
```

---

## Storage

- Custom instructions are stored in `prompts/system_prompt.txt`
- The file is created automatically when instructions are saved
- If no custom instructions exist, only the base prompt is used
- The `prompts/*.txt` files are ignored by git (see `.gitignore`)

## How It Works

**System Prompt Structure:**
```
[ALWAYS INCLUDED] Base System Prompt (hardcoded in app.py)
  ↓ Contains: JSON schema, design rules, material info

[OPTIONAL] + Custom Instructions (from prompts/system_prompt.txt)
  ↓ Contains: User preferences, additional constraints

[OPTIONAL] + Per-Request Instructions (from request.system_message)
  ↓ Contains: Specific instructions for this request only
```

**Example Final Prompt:**
```
You are an expert optical engineer... [full base prompt with schema]

CUSTOM INSTRUCTIONS:
Focus on compact designs. Prefer BK7 material.

ADDITIONAL INSTRUCTIONS:
Make this design suitable for mobile phone cameras.
```

## Integration with Existing Endpoints

The following endpoints use this prompt system:

- **POST /api/design** - Generates optical designs using base + custom + per-request instructions
- **POST /api/chat** - Chat interface using the same prompt hierarchy

Both endpoints automatically combine:
1. Base system prompt (always)
2. Custom instructions from file (if exists)
3. Per-request `system_message` field (if provided)

## CORS Configuration

The API supports CORS and accepts requests from any origin by default. Configure the `ALLOWED_ORIGINS` environment variable to restrict access:

```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Error Handling

### 400 Bad Request
- Empty or whitespace-only prompt content

### 500 Internal Server Error
- File system errors
- Permission issues
- Unexpected errors during save/load

## Testing

A test script is provided in `test_system_prompt.py`:

```bash
# Start the server
python app.py

# In another terminal, run the tests
python test_system_prompt.py
```

## Frontend Integration Example

```typescript
// Load current system prompt
async function loadSystemPrompt() {
  const response = await fetch('https://opdo-v2-chat.onrender.com/api/system-prompt');
  const data = await response.json();
  return data.content;
}

// Save new system prompt
async function saveSystemPrompt(content: string) {
  const response = await fetch('https://opdo-v2-chat.onrender.com/api/system-prompt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  });
  const data = await response.json();
  return data;
}
```

## Deployment Notes

### Render.com Persistent Storage

When deployed on Render.com, ensure you have persistent storage configured if you want prompts to survive deployments:

1. Go to your Render dashboard
2. Navigate to your service settings
3. Add a persistent disk mount at `/opt/render/project/src/prompts`

Without persistent storage, prompts will reset to default on each deployment.

### Alternative: Database Storage

For production use with high availability requirements, consider storing prompts in a database instead of files. The current implementation uses file storage for simplicity.

## Security Considerations

1. **Input Validation**: The API validates that prompt content is not empty
2. **File Permissions**: Ensure the `prompts/` directory has appropriate write permissions
3. **Access Control**: Consider adding authentication if you want to restrict who can modify the system prompt
4. **Content Filtering**: You may want to add validation to ensure prompts don't contain malicious content

## Default Prompt

The default system prompt is defined in `app.py` as the `SYSTEM_PROMPT` constant. It includes:

- Optical design expertise instructions
- JSON schema specification
- Design rules and conventions
- Material and wavelength guidelines

This default is used when no custom prompt has been saved.
