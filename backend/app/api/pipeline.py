from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.pipeline.state import StepType
from app.schemas.pipeline import PipelineResponse, PipelineStepResponse, StepUpdateRequest
from app.services.pipeline_service import PipelineService
from app.ws.connection import connection_manager

router = APIRouter(prefix="/projects/{project_id}/pipeline", tags=["pipeline"])


@router.get("", response_model=PipelineResponse)
async def get_pipeline(project_id: str, db: AsyncSession = Depends(get_db)):
    service = PipelineService(db)
    return await service.get_pipeline(project_id)


@router.post("/run/{step_type}", response_model=PipelineStepResponse)
async def run_step(project_id: str, step_type: StepType, db: AsyncSession = Depends(get_db)):
    service = PipelineService(db, ws_manager=connection_manager)
    return await service.run_step(project_id, step_type)


@router.patch("/{step_id}", response_model=PipelineStepResponse)
async def update_step(
    project_id: str,
    step_id: str,
    body: StepUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = PipelineService(db, ws_manager=connection_manager)
    return await service.update_step(project_id, step_id, body)
