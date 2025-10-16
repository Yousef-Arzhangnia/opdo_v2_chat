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

For production:

1. Update CORS settings in `app.py` to only allow your frontend domain
2. Use a production ASGI server like gunicorn with uvicorn workers:
   ```bash
   pip install gunicorn
   gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
3. Set up environment variables securely (not in .env file)
4. Use HTTPS/TLS encryption
5. Consider rate limiting and authentication

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
