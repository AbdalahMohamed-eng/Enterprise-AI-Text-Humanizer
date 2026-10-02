from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.config import settings


def resolve_api_key(
    provider: str,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"),
    x_groq_key: Optional[str] = Header(None, alias="X-Groq-Key"),
) -> str:
    provider = provider.lower()
    key = None
    if provider == "openai":
        key = x_openai_key or settings.OPENAI_API_KEY
    elif provider in ("gemini", "google"):
        key = x_gemini_key or settings.GEMINI_API_KEY
    elif provider == "groq":
        key = x_groq_key or settings.GROQ_API_KEY
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No API key provided for {provider.title()}. Enter your key in Settings.",
        )
    return key
