import litellm
from litellm import acompletion
from typing import AsyncGenerator
from app.services.prompt_service import build_humanizer_prompt

litellm.suppress_debug_info = True


class LLMService:
    SUPPORTED_MODELS = {
        "openai": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ],
        "gemini": [
            {"id": "gemini/gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
            {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
        ],
        "groq": [
            {"id": "groq/llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
            {"id": "groq/llama-3.1-8b-instant", "name": "Llama 3.1 8B"},
        ],
    }

    @staticmethod
    async def stream_humanize(
        text, mode, strength, model, api_key
    ) -> AsyncGenerator[str, None]:
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
                temperature=0.85
                if strength == "aggressive"
                else 0.75
                if strength == "medium"
                else 0.65,
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    @classmethod
    def get_models(cls) -> dict:
        return cls.SUPPORTED_MODELS
