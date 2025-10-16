# Optical Design Chat Backend

Python backend service that generates optical designs using Claude API based on natural language descriptions.

## Features

- REST API endpoint that accepts optical design requests via HTTP POST
- Integrates with Claude API (Anthropic) for intelligent optical design generation
- Schema validation ensuring output matches your frontend requirements
- CORS enabled for frontend integration
- Conversation history support for multi-turn interactions

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/settings/keys

### 3. Run the Server

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Endpoints

### POST `/api/design`

Generate an optical design from a natural language description.

**Request Body:**
```json
{
  "user_message": "Design a simple achromatic doublet lens for visible light",
  "system_message": "Focus on minimizing chromatic aberration",  // Optional
  "previous_design": { /* previous optical design object */ },    // Optional
  "added_data": { "priority": "image_quality" }                  // Optional
}
```

**Request Parameters:**
- `user_message` (required): User's optical design requirement or question
- `system_message` (optional): Custom instructions to guide the design generation
- `previous_design` (optional): Previous design object for iteration/memory
- `added_data` (optional): Any additional context data for future use

**Response:**
```json
{
  "design": {
    "source": {
      "type": "infinity",
      "fields": [{"deg": 0}, {"deg": 5}],
      "wavelengths_nm": [587.6, 486.1, 656.3]
    },
    "lenses": [
      {
        "diameter_mm": 25.4,
        "thickness_mm": 5.0,
        "distance_from_previous_mm": 0,
        "material": "BK7",
        "refractiveIndex": 1.517,
        "front": {"type": "spherical", "roc_mm": 50.0},
        "back": {"type": "spherical", "roc_mm": -45.0},
        "label": "L1"
      }
    ],
    "image_plane_x_mm": 100.0
  },
  "explanation": "This design provides..."
}
```

### POST `/api/chat`

Alternative endpoint for more flexible chat interactions.

**Request Body:** Same as `/api/design`

**Response:**
```json
{
  "type": "design" | "text",
  "data": { /* optical design */ },  // if type is "design"
  "message": "text response",        // if type is "text"
  "raw_response": "..."
}
```

### GET `/`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Optical Design Chat API is running"
}
```

## Integration with Your Frontend

Update your frontend to make POST requests to this backend:

```typescript
async function generateOpticalDesign(
  userMessage: string,
  systemMessage?: string,
  previousDesign?: any,
  addedData?: any
) {
  const response = await fetch('http://localhost:8000/api/design', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_message: userMessage,
      system_message: systemMessage || null,
      previous_design: previousDesign || null,
      added_data: addedData || null
    })
  });

  const result = await response.json();
  return result.design;  // This matches your schema
}
```

### Example Usage with Memory

```typescript
// First design
const design1 = await generateOpticalDesign(
  "Design a simple lens",
  "Keep it compact",
  null,
  { application: "camera" }
);

// Iterate on the design (with memory)
const design2 = await generateOpticalDesign(
  "Make the focal length shorter",
  "Maintain the same diameter",
  design1,  // Pass previous design for memory
  { iteration: 2 }
);
```

## Example Requests

### Simple Lens
```bash
curl -X POST http://localhost:8000/api/design \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Design a simple plano-convex lens with 50mm focal length",
    "system_message": null,
    "previous_design": null,
    "added_data": null
  }'
```

### Achromatic Doublet with Custom Instructions
```bash
curl -X POST http://localhost:8000/api/design \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Create an achromatic doublet for telescope objective, 100mm diameter",
    "system_message": "Optimize for minimal chromatic aberration across visible spectrum",
    "previous_design": null,
    "added_data": {"application": "astronomy", "budget": "mid-range"}
  }'
```

### Iterate on Previous Design
```bash
curl -X POST http://localhost:8000/api/design \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Make the focal length shorter and improve edge performance",
    "system_message": "Keep the same materials if possible",
    "previous_design": {
      "source": {...},
      "lenses": [...],
      "image_plane_x_mm": 100.0
    },
    "added_data": {"iteration": 2, "priority": "edge_sharpness"}
  }'
```

## Output Schema

The API returns optical designs in the exact format your frontend expects:

- **source**: Light source configuration (point or infinity type)
- **fields**: Field angles (for infinity) or positions (for point sources)
- **wavelengths_nm**: Array of wavelengths in nanometers
- **lenses**: Array of lens elements with:
  - Physical dimensions (diameter, thickness, spacing)
  - Material and refractive index
  - Front and back surface definitions (planar/spherical/aspherical)
  - Radius of curvature, conic constants, asphere coefficients
- **image_plane_x_mm**: Image plane position

## Development

### Running in Development Mode

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Testing

You can test the API using:
- `curl` commands (see examples above)
- Postman or similar API testing tools
- Python requests library
- Your frontend application

## Production Deployment

### Deploy to Render.com (Recommended)

Render.com offers free hosting for web services, perfect for this API.

#### Step 1: Prepare Your Repository

Make sure all files are committed to your Git repository:

```bash
git add .
git commit -m "Add optical design chat API"
git push origin main
```

#### Step 2: Create Render Account

1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub/GitLab account

#### Step 3: Deploy

1. Click **"New +"** → **"Web Service"**
2. Connect your repository
3. Render will auto-detect the `render.yaml` configuration
4. Configure environment variables:
   - Click **"Environment"** tab
   - Add `ANTHROPIC_API_KEY` with your API key
   - (Optional) Add `ALLOWED_ORIGINS` with your frontend URL (e.g., `https://yourdomain.com`)
5. Click **"Create Web Service"**

Render will automatically:
- Install dependencies from `requirements.txt`
- Start the server with uvicorn
- Provide you with a URL like `https://optical-design-api.onrender.com`

#### Step 4: Update Your Frontend

Update your frontend to use the deployed URL:

```typescript
const API_URL = 'https://your-app-name.onrender.com';

const response = await fetch(`${API_URL}/api/design`, {
  method: 'POST',
  // ... rest of your request
});
```

#### Render Configuration Files

This repository includes:
- `render.yaml` - Render deployment configuration
- `runtime.txt` - Python version specification

#### Environment Variables on Render

Set these in the Render dashboard:
- `ANTHROPIC_API_KEY` (required) - Your Claude API key
- `ALLOWED_ORIGINS` (optional) - Comma-separated list of allowed frontend URLs
  - Example: `https://myapp.com,https://www.myapp.com`
  - Default: `*` (allow all origins)

### Alternative: Deploy Manually

For other platforms (Railway, Fly.io, etc.):

1. Use a production ASGI server:
   ```bash
   pip install gunicorn
   gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```
2. Set environment variables securely
3. Configure CORS via `ALLOWED_ORIGINS` environment variable
4. Enable HTTPS/TLS encryption

### Free Tier Limitations

**Render Free Tier:**
- Service spins down after 15 minutes of inactivity
- First request after inactivity takes ~30-60 seconds (cold start)
- 750 hours/month free
- Good for development and low-traffic production

**Solutions for Cold Starts:**
- Upgrade to paid tier ($7/month) for always-on service
- Use a service like [cron-job.org](https://cron-job.org) to ping your API every 10 minutes
- Show a loading message to users on first request

## Troubleshooting

**API Key Issues:**
- Ensure `.env` file exists and contains valid `ANTHROPIC_API_KEY`
- Check that the key has sufficient credits/permissions

**CORS Errors:**
- Update `allow_origins` in `app.py` to include your frontend URL
- Ensure your frontend is making requests to the correct backend URL

**JSON Parsing Errors:**
- Claude should return valid JSON, but if issues occur, the API will attempt to extract JSON from markdown code blocks
- Check the error message for details about what went wrong

**Port Already in Use:**
- Change the port in `app.py` or when running uvicorn: `uvicorn app:app --port 8001`

## License

MIT
