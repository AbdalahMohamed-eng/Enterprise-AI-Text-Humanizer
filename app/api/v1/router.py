"""API v1 router: Aggregates all endpoint routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import humanize, detect, models

router = APIRouter()
router.include_router(humanize.router, tags=["humanize"])
router.include_router(detect.router, tags=["detect"])
router.include_router(models.router, tags=["models"])
