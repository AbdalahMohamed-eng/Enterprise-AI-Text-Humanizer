"""
AI Text Humanizer — FastAPI Application Factory.

Serves the web UI and API endpoints for humanizing AI-generated text.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.api.v1.router import router as api_v1_router

# Resolve paths relative to this file's location
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title=settings.APP_NAME,
    description="Humanize AI-generated text using rule-based NLP + LLM polishing",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and Jinja2 templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API v1 router
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
async def root(request: Request):
    """Serve the main frontend application."""
    return templates.TemplateResponse(
        request=request, name="index.html", context={"app_name": settings.APP_NAME}
    )


@app.on_event("startup")
async def startup_event():
    """Download required NLTK data on first startup."""
    try:
        pass
        # nltk.download("wordnet", quiet=True)
        # nltk.download("omw-1.4", quiet=True)
    except Exception:
        pass
