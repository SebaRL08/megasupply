from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from google import genai
from google.genai import errors
import os
import json

router = APIRouter(prefix="/api/ai", tags=["AI Inventory Assistant"])

class AIQueryRequest(BaseModel):
    user_query: str = Field(..., description="Natural language query regarding inventory status.")

class AIQueryResponse(BaseModel):
    product: str
    stock_status: str
    reorder_suggested: bool
    reasoning: str

@router.post("/analyze", response_model=AIQueryResponse, summary="Analyze inventory via LLM")
def analyze_inventory_ai(payload: AIQueryRequest):
    """Processes user text with Google Gemini applying structured JSON output."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key is not configured on the server."
        )

    client = genai.Client(api_key=api_key)

    # Prompt con Role Prompting y Output Formatting
    system_prompt = (
        "You are a Senior Logistics & Supply Chain Manager at MegaSupply, an import and wholesale company in Colombia. "
        "Analyze the user's inventory request using professional supply chain terminology. "
        "Respond STRICTLY in JSON format using the keys: 'product', 'stock_status', 'reorder_suggested', and 'reasoning'."
    )
    
    full_prompt = f"{system_prompt}\n\nUser Request: {payload.user_query}"

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=full_prompt,
        )
        
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        response_json = json.loads(clean_text)
        return response_json

    except errors.ServerError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service is experiencing high demand: {e.message}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The AI model response could not be parsed into a valid JSON structure."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )