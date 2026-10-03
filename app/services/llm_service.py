import asyncio
from typing import AsyncGenerator, Optional
import litellm
from litellm import acompletion
from app.services.prompt_service import build_humanizer_prompt

litellm.suppress_debug_info = True


class LLMService:
    SUPPORTED_MODELS = {
        "local": [
            {
                "id": "local/rules-engine",
                "name": "6-Stage Linguistic Engine (Free • No Key Needed)",
            }
        ],
        "groq": [
            {"id": "groq/llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Recommended)"},
            {"id": "groq/llama-3.1-8b-instant", "name": "Llama 3.1 8B (Fast)"},
        ],
        "openai": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ],
        "gemini": [
            {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
            {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
        ],
    }

    @staticmethod
    async def stream_humanize(
        text: str,
        mode: str,
        strength: str,
        model: str,
        api_key: Optional[str] = None,
        fallback_text: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        # Handle local rule engine mode
        if not model or model.startswith("local") or not api_key:
            output = fallback_text or text
            words = output.split(" ")
            chunk_size = 4
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i : i + chunk_size])
                if i + chunk_size < len(words):
                    chunk += " "
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.015)
            yield "data: [DONE]\n\n"
            return

        system_prompt, user_prompt = build_humanizer_prompt(text, mode, strength)
        try:
            response = await acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                api_key=api_key,
                stream=True,
                num_retries=1,
                temperature=(
                    0.85 if strength == "aggressive" else 0.75 if strength == "medium" else 0.65
                ),
            )
            has_yielded = False
            async for chunk in response:
                if chunk and chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        has_yielded = True
                        # Format lines for SSE compliance
                        for line in content.split("\n"):
                            yield f"data: {line}\n"
                        yield "\n"
            if has_yielded:
                yield "data: [DONE]\n\n"
                return

        except Exception as e:
            error_msg = str(e)
            # If we have fallback rule-preprocessed text, deliver it gracefully!
            if fallback_text:
                clean_err = error_msg.replace("\n", " ").strip()[:180]
                yield f"event: warning\ndata: {clean_err}\n\n"
                words = fallback_text.split(" ")
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i : i + chunk_size])
                    if i + chunk_size < len(words):
                        chunk += " "
                    yield f"data: {chunk}\n\n"
                    await asyncio.sleep(0.015)
                yield "data: [DONE]\n\n"
                return
            else:
                clean_err = error_msg.replace("\n", " ").strip()[:180]
                yield f"event: error\ndata: {clean_err}\n\n"
                return

    @classmethod
    def get_models(cls) -> dict:
        return cls.SUPPORTED_MODELS
