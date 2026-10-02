from fastapi import APIRouter
from pydantic import BaseModel
from app.services.detector_service import DetectorService
from typing import Optional

router = APIRouter()


class DetectRequest(BaseModel):
    text: str
    provider: Optional[str] = "auto"


class DetectResponse(BaseModel):
    provider: str
    ai_score_percent: Optional[float] = None
    human_score_percent: Optional[float] = None
    error: Optional[str] = None


@router.post("/detect", response_model=DetectResponse)
async def detect_text(request: DetectRequest):
    result = await DetectorService.preview_score(request.text, request.provider)
    return DetectResponse(**result)
