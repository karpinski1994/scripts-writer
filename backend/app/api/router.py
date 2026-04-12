from fastapi import APIRouter

from app.api.projects import router as projects_router

router = APIRouter(prefix="/api/v1")
router.include_router(projects_router)
