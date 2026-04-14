import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import PipelineStep, ScriptVersion
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.state import StepStatus, StepType
from app.schemas.analysis import AnalysisResultResponse
from app.services.analysis_service import AnalysisService
from app.ws.connection import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/analysis", tags=["analysis"])

VALID_AGENT_TYPES = {"factcheck", "readability", "copyright", "policy"}


async def _verify_writer_completed(project_id: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(PipelineStep).where(
            PipelineStep.project_id == project_id,
            PipelineStep.step_type == StepType.writer.value,
        )
    )
    writer_step = result.scalar_one_or_none()
    if writer_step is None or writer_step.status != StepStatus.completed.value:
        raise HTTPException(status_code=409, detail="Writer step must be completed before running analysis")


async def _get_latest_script_version_id(project_id: str, db: AsyncSession) -> str:
    result = await db.execute(
        select(ScriptVersion)
        .where(ScriptVersion.project_id == project_id)
        .order_by(ScriptVersion.version_number.desc())
        .limit(1)
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail="No script version found")
    return version.id


@router.post("/{agent_type}", response_model=AnalysisResultResponse)
async def run_analysis(
    project_id: str,
    agent_type: str,
    db: AsyncSession = Depends(get_db),
):
    logger.error(f"DEBUG: run_analysis called with agent_type='{agent_type}'")
    if agent_type not in VALID_AGENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    await _verify_writer_completed(project_id, db)

    step_type = StepType(agent_type)
    orchestrator = PipelineOrchestrator(db, ws_manager=connection_manager)
    step = await orchestrator.run_step(project_id, step_type)

    from app.schemas.analysis import Finding

    findings_data = []
    if step.output_data:
        import json

        output = json.loads(step.output_data)
        findings_data = output.get("findings", [])
    findings = [Finding.model_validate(f) for f in findings_data]

    overall_score = None
    if agent_type == "readability":
        output = json.loads(step.output_data) if step.output_data else {}
        fk = output.get("flesch_kincaid_score")
        gf = output.get("gunning_fog_score")
        if fk is not None and gf is not None:
            overall_score = round((fk + gf) / 2, 2)

    script_version_id = await _get_latest_script_version_id(project_id, db)
    service = AnalysisService(db)
    return await service.save_result(
        project_id=project_id,
        script_version_id=script_version_id,
        agent_type=agent_type,
        findings=findings,
        overall_score=overall_score,
    )


@router.post("/all", response_model=list[AnalysisResultResponse])
async def run_all_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    await _verify_writer_completed(project_id, db)

    orchestrator = PipelineOrchestrator(db, ws_manager=connection_manager)
    await orchestrator.run_analysis_parallel(project_id)

    service = AnalysisService(db)
    results = []
    for agent_type in VALID_AGENT_TYPES:
        result = await service.get_result_by_type(project_id, agent_type)
        if result:
            results.append(result)
    return results


@router.get("", response_model=list[AnalysisResultResponse])
async def get_analysis_results(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = AnalysisService(db)
    return await service.get_results(project_id)
