import os
from typing import Dict, Any, Optional
import httpx

_hf_pipeline = None


class DetectorService:
    @staticmethod
    def check_local(text: str) -> Dict[str, Any]:
        """Uses HuggingFace transformers with AICodexLab/answerdotai-ModernBERT-base-ai-detector."""
        global _hf_pipeline
        try:
            if _hf_pipeline is None:
                from transformers import pipeline

                _hf_pipeline = pipeline(
                    "text-classification",
                    model="AICodexLab/answerdotai-ModernBERT-base-ai-detector",
                )

            result = _hf_pipeline(text, truncation=True, max_length=512)

            ai_score = 0.0
            for label_score in result:
                label = label_score["label"].upper()
                if label in ["AI", "LABEL_1"]:
                    ai_score = label_score["score"]
                    break
                elif label in ["HUMAN", "LABEL_0"]:
                    ai_score = 1.0 - label_score["score"]

            return {
                "provider": "local",
                "ai_score_percent": round(ai_score * 100, 2),
                "human_score_percent": round((1 - ai_score) * 100, 2),
            }
        except Exception as e:
            return {"provider": "local", "error": str(e)}

    @staticmethod
    async def check_sapling(text: str) -> Dict[str, Any]:
        """Calls Sapling AI detect API."""
        api_key = os.getenv("SAPLING_API_KEY")
        if not api_key:
            return {"provider": "sapling", "error": "API key not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sapling.ai/api/v1/aidetect",
                    json={"key": api_key, "text": text},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                score = data.get("score", 0.0)
                return {
                    "provider": "sapling",
                    "ai_score_percent": round(score * 100, 2),
                    "human_score_percent": round((1 - score) * 100, 2),
                }
        except Exception as e:
            return {"provider": "sapling", "error": str(e)}

    @staticmethod
    async def preview_score(text: str, provider: str = "auto") -> Dict[str, Any]:
        """Auto-cascades: preferred -> sapling -> local"""
        if provider in ("sapling", "auto"):
            result = await DetectorService.check_sapling(text)
            if "error" not in result:
                return result

        if provider in ("local", "auto"):
            return DetectorService.check_local(text)

        return {"error": "Failed to run detection with any provider"}
