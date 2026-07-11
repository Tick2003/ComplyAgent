"""LLM client abstraction — wraps Google Gemini API."""
import json
import logging
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Lazy-initialize the Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


async def generate_json(prompt: str, system_instruction: str = "", temperature: float = 0.2) -> dict | list:
    """Send a prompt to Gemini and parse JSON from the response."""
    client = get_client()
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction or "You are a regulatory compliance expert. Always respond with valid JSON.",
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from LLM: {e}\nRaw: {text[:500]}")
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


async def generate_text(prompt: str, system_instruction: str = "", temperature: float = 0.3) -> str:
    """Send a prompt to Gemini and return plain text."""
    client = get_client()
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction or "You are a regulatory compliance expert for SEBI-regulated stockbrokers in India.",
                temperature=temperature,
            ),
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"LLM text call failed: {e}")
        raise
