"""
Optical Design Chat Backend
FastAPI server that receives optical design requests and uses Claude API to generate designs.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union
import anthropic
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Optical Design Chat API")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# Request model
class OpticalDesignRequest(BaseModel):
    """Request model for optical design generation"""
    user_message: str = Field(..., description="User's optical design requirement")
    conversation_history: Optional[List[dict]] = Field(
        default=None,
        description="Optional conversation history for context"
    )


# Response models matching your schema
class InfinityField(BaseModel):
    deg: float


class PointField(BaseModel):
    x_mm: float
    y_mm: float


class Source(BaseModel):
    type: Literal["point", "infinity"]
    fields: List[Union[InfinityField, PointField]]
    wavelengths_nm: List[float]


class Surface(BaseModel):
    type: Literal["planar", "spherical", "aspherical"]
    roc_mm: Optional[float] = None
    conic: Optional[float] = None
    asphere: Optional[List[float]] = None


class Lens(BaseModel):
    diameter_mm: float
    thickness_mm: float
    distance_from_previous_mm: float
    material: str
    refractiveIndex: Optional[float] = None
    front: Surface
    back: Surface
    label: Optional[str] = None


class OpticalDesign(BaseModel):
    source: Source
    lenses: List[Lens]
    image_plane_x_mm: float


class OpticalDesignResponse(BaseModel):
    """Response model containing the optical design"""
    design: OpticalDesign
    explanation: Optional[str] = None


# System prompt for Claude
SYSTEM_PROMPT = """You are an expert optical engineer specializing in lens design. Users will describe their optical design requirements, and you must generate complete, valid optical designs.

Your response MUST be a valid JSON object following this exact schema:

{
  "source": {
    "type": "point" | "infinity",
    "fields": [
      // For infinity sources: { "deg": number }
      // For point sources: { "x_mm": number, "y_mm": number }
    ],
    "wavelengths_nm": [number, ...]
  },
  "lenses": [
    {
      "diameter_mm": number,
      "thickness_mm": number,
      "distance_from_previous_mm": number,
      "material": string,
      "refractiveIndex": number,
      "front": {
        "type": "planar" | "spherical" | "aspherical",
        "roc_mm": number,  // optional for planar
        "conic": number,   // optional, for aspherical
        "asphere": [A4, A6, A8, A10]  // optional, 4-element array
      },
      "back": {
        "type": "planar" | "spherical" | "aspherical",
        "roc_mm": number,
        "conic": number,
        "asphere": [A4, A6, A8, A10]
      },
      "label": string
    }
  ],
  "image_plane_x_mm": number
}

IMPORTANT DESIGN RULES:
1. All distances and dimensions must be positive unless specified otherwise
2. ROC (radius of curvature) sign convention:
   - Positive: center of curvature at larger X (convex when light travels +X)
   - Negative: center of curvature at smaller X (concave when light travels +X)
3. Common materials: BK7 (n≈1.517), SF11 (n≈1.785), Fused Silica (n≈1.458), N-BK7, SF5, etc.
4. Standard wavelengths (nm): d-line (587.6), F-line (486.1), C-line (656.3)
5. For infinity sources, use field angles in degrees (0 for on-axis)
6. For point sources, use x_mm and y_mm coordinates
7. distance_from_previous_mm for first lens is distance from source
8. Planar surfaces don't require roc_mm
9. Aspherical surfaces need both conic and optionally asphere coefficients

Respond ONLY with the JSON object, no markdown code blocks, no explanations outside the JSON.
If you want to provide an explanation, include it as a top-level "explanation" field in the JSON."""


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Optical Design Chat API is running"}


@app.post("/api/design", response_model=OpticalDesignResponse)
async def generate_optical_design(request: OpticalDesignRequest):
    """
    Generate an optical design based on user requirements.

    Args:
        request: OpticalDesignRequest containing user message and optional history

    Returns:
        OpticalDesignResponse containing the generated optical design
    """
    try:
        # Prepare messages for Claude
        messages = []

        # Add conversation history if provided
        if request.conversation_history:
            messages.extend(request.conversation_history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": request.user_message
        })

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Use latest Claude model
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        # Extract response text
        response_text = response.content[0].text.strip()

        # Parse JSON response
        try:
            design_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to extract JSON if Claude wrapped it in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
                design_data = json.loads(response_text)
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse Claude response as JSON: {str(e)}\nResponse: {response_text}"
                )

        # Extract explanation if present
        explanation = design_data.pop("explanation", None)

        # Validate and construct response
        design = OpticalDesign(**design_data)

        return OpticalDesignResponse(
            design=design,
            explanation=explanation
        )

    except anthropic.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anthropic API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating optical design: {str(e)}"
        )


@app.post("/api/chat")
async def chat_endpoint(request: OpticalDesignRequest):
    """
    Alternative endpoint that returns raw Claude response for more flexible chat.
    """
    try:
        messages = []
        if request.conversation_history:
            messages.extend(request.conversation_history)

        messages.append({
            "role": "user",
            "content": request.user_message
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        response_text = response.content[0].text.strip()

        # Try to parse as JSON
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            design_data = json.loads(response_text)
            return {
                "type": "design",
                "data": design_data,
                "raw_response": response_text
            }
        except json.JSONDecodeError:
            # Return as text if not JSON
            return {
                "type": "text",
                "message": response_text,
                "raw_response": response_text
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in chat: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
