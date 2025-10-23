# System Prompt Management API

This document describes the system prompt management endpoints added to the FastAPI backend.

## Overview

The system prompt can now be dynamically managed through API endpoints instead of being hardcoded. This allows frontend applications to customize the AI's behavior without requiring backend deployments.

## Endpoints

### GET /api/system-prompt

Retrieve the current system prompt.

**Response:**
```json
{
  "content": "Your system prompt text here..."
}
```

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

Save a new system prompt.

**Request Body:**
```json
{
  "content": "New system prompt text..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "System prompt saved successfully"
}
```

**Example:**
```bash
curl -X POST https://opdo-v2-chat.onrender.com/api/system-prompt \
  -H "Content-Type: application/json" \
  -d '{"content": "You are an expert optical engineer..."}'
```

**Python example:**
```python
import requests

new_prompt = """You are an expert optical engineer specializing in lens design.
Your task is to generate optical designs based on user requirements."""

response = requests.post(
    "https://opdo-v2-chat.onrender.com/api/system-prompt",
    json={"content": new_prompt}
)
data = response.json()
print(data["message"])
```

---

## Storage

- System prompts are stored in `prompts/system_prompt.txt`
- The file is created automatically when the first prompt is saved
- If no custom prompt is saved, the default hardcoded prompt is used
- The `prompts/*.txt` files are ignored by git (see `.gitignore`)

## Integration with Existing Endpoints

The following endpoints now use the stored system prompt:

- **POST /api/design** - Uses stored prompt for optical design generation
- **POST /api/chat** - Uses stored prompt for chat responses

Both endpoints will use the custom system prompt if one has been saved, otherwise they fall back to the default prompt.

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
