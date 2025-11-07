"""LLM-based image analysis utilities."""
import json
from typing import Dict, Optional
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


LLM_JSON_PROMPT = """You are a remote-sensing analyst. Use the location context and the image to produce STRICT JSON.

Location context:
{location_context}

Return JSON with keys:
- "location_guess": string (country/state/city if known, else "unknown")
- "land_cover": string (concise)
- "urban_structure": string (road patterns, density, CBD/industrial/coastal notes)
- "notable_features": string (bridges/ports/airports/rivers/parks/etc)
- "summary": string (2-3 sentences)

Do NOT include any text outside the JSON."""


def image_to_base64(image_path: str) -> str:
    """
    Convert image file to base64 string.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_image_with_llm(
    llm: ChatOpenAI,
    jpeg_path: str,
    location_context: str
) -> Dict:
    """
    Analyze image using vision language model.
    
    Args:
        llm: ChatOpenAI instance
        jpeg_path: Path to JPEG image
        location_context: Location context string
        
    Returns:
        Dictionary with analysis results
    """
    mime = "image/jpeg"
    img_b64 = image_to_base64(jpeg_path)
    prompt = LLM_JSON_PROMPT.format(location_context=location_context)
    
    msg = HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}}
    ])
    
    resp = llm.invoke([msg])
    text = resp.content.strip()
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception:
        return {"raw_response": text, "error": "Failed to parse JSON"}

