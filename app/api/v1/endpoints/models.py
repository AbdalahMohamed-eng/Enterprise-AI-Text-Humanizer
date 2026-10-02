from fastapi import APIRouter
from app.services.llm_service import LLMService

router = APIRouter()


@router.get("/models")
async def get_models():
    return LLMService.get_models()
