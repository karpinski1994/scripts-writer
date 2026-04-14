import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.pipeline.state import StepType
from app.schemas.pipeline import PipelineResponse, PipelineStepResponse, StepUpdateRequest
from app.services.pipeline_service import PipelineService
from app.ws.connection import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/pipeline", tags=["pipeline"])


@router.get("", response_model=PipelineResponse)
async def get_pipeline(project_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"[PIPELINE-API] GET pipeline for project: {project_id}")
    service = PipelineService(db)
    return await service.get_pipeline(project_id)


@router.post("/run/{step_type}", response_model=PipelineStepResponse)
async def run_step(project_id: str, step_type: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"[PIPELINE-API] POST run step - project: {project_id}, step_type: {step_type}")
    service = PipelineService(db, ws_manager=connection_manager)
    try:
        step_type_enum = StepType(step_type)
    except ValueError:
        logger.error(f"[PIPELINE-API] Invalid step type: {step_type}")
        raise HTTPException(status_code=422, detail=f"Invalid step type: {step_type}")
    result = await service.run_step(project_id, step_type_enum)
    logger.info(f"[PIPELINE-API] Step {step_type} completed for project: {project_id}")
    return result


@router.patch("/{step_id}", response_model=PipelineStepResponse)
async def update_step(
    project_id: str,
    step_id: str,
    body: StepUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        f"[PIPELINE-API] PATCH step - project: {project_id}, step_id: {step_id}, selected_option: {body.selected_option is not None}"
    )
    service = PipelineService(db, ws_manager=connection_manager)
    result = await service.update_step(project_id, step_id, body)
    logger.info(f"[PIPELINE-API] Step {step_id} updated for project: {project_id}")
    return result


@router.post("/cancel", status_code=204)
async def cancel_pipeline(project_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"[PIPELINE-API] POST cancel pipeline for project: {project_id}")
    service = PipelineService(db, ws_manager=connection_manager)
    await service.cancel_all_steps(project_id)
    logger.info(f"[PIPELINE-API] Pipeline cancelled for project: {project_id}")


@router.post("/reset-errors", status_code=204)
async def reset_errors(project_id: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"[PIPELINE-API] POST reset errors for project: {project_id}")
    service = PipelineService(db, ws_manager=connection_manager)
    await service.reset_failed_steps(project_id)
    logger.info(f"[PIPELINE-API] Errors reset for project: {project_id}")
