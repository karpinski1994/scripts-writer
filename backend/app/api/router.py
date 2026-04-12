from fastapi import APIRouter

from app.api.projects import router as projects_router
from app.api.settings import router as settings_router

router = APIRouter(prefix="/api/v1")
router.include_router(projects_router)
router.include_router(settings_router)
