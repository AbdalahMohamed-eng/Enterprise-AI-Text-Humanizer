from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AI Text Humanizer"
    DEBUG: bool = False

    # Server-wide fallback API keys (optional)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    SAPLING_API_KEY: Optional[str] = None

    # Default model settings
    DEFAULT_PROVIDER: str = "groq"
    DEFAULT_MODEL: str = "groq/llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
