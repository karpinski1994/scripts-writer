from fastapi import APIRouter

from app.api.analysis import router as analysis_router
from app.api.export import router as export_router
from app.api.icp import router as icp_router
from app.api.notebooklm import router as notebooklm_router
from app.api.pipeline import router as pipeline_router
from app.api.piragi import router as rag_router
from app.api.projects import router as projects_router
from app.api.scripts import router as scripts_router
from app.api.settings import router as settings_router

router = APIRouter(prefix="/api/v1")
router.include_router(projects_router)
router.include_router(pipeline_router)
router.include_router(icp_router)
router.include_router(settings_router)
router.include_router(scripts_router)
router.include_router(export_router)
router.include_router(notebooklm_router)
router.include_router(rag_router)
router.include_router(analysis_router)
