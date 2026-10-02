from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ToneMode(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    ACADEMIC = "academic"
    ANTI_AI = "anti_ai"


class Strength(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"


class HumanizeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    provider: str = Field(default="groq")
    model: str = Field(default="groq/llama-3.3-70b-versatile")
    mode: ToneMode = Field(default=ToneMode.ANTI_AI)
    strength: Strength = Field(default=Strength.MEDIUM)
    use_rules: bool = Field(default=True, description="Apply rule-based preprocessing")


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000)
    provider: str = Field(default="auto")


class DetectResponse(BaseModel):
    provider: str
    ai_score_percent: float
    human_score_percent: float
    details: Optional[dict] = None


class TextStats(BaseModel):
    word_count: int
    sentence_count: int
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    burstiness_cv: float


class ModelsResponse(BaseModel):
    providers: List[dict]
