"""
Humanize endpoint: Accepts text, applies rule-based preprocessing,
then streams LLM-polished output via Server-Sent Events.
"""

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

from app.schemas.humanize import HumanizeRequest
from app.services.llm_service import LLMService
from app.services.rule_engine.pipeline import HumanizerPipeline
from app.core.dependencies import resolve_api_key

router = APIRouter()

# Initialize rule engine pipeline (singleton)
_pipeline: Optional[HumanizerPipeline] = None


def get_pipeline() -> HumanizerPipeline:
    """Lazy-initialize the rule engine pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = HumanizerPipeline()
    return _pipeline


@router.post("/humanize")
async def humanize_text(
    request: HumanizeRequest,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"),
    x_groq_key: Optional[str] = Header(None, alias="X-Groq-Key"),
):
    """
    Humanize AI-generated text using rule-based preprocessing + LLM polishing.

    Streams the result as Server-Sent Events (SSE).
    """
    # Resolve API key from headers or .env fallback
    api_key = resolve_api_key(
        provider=request.provider,
        x_openai_key=x_openai_key,
        x_gemini_key=x_gemini_key,
        x_groq_key=x_groq_key,
    )

    # Apply rule-based preprocessing if enabled
    text_to_process = request.text
    if request.use_rules:
        try:
            pipeline = get_pipeline()
            text_to_process = pipeline.preprocess(
                text_to_process, strength=request.strength.value
            )
        except Exception:
            # If rule engine fails, proceed with original text
            text_to_process = request.text

    return StreamingResponse(
        LLMService.stream_humanize(
            text=text_to_process,
            mode=request.mode.value,
            strength=request.strength.value,
            model=request.model,
            api_key=api_key,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
