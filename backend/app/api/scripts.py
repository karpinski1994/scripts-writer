import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.selection_rewrite_agent import rewrite_selection
from app.config import get_settings
from app.db.database import get_db
from app.db.models import ICPProfile, ScriptVersion
from app.llm.provider_factory import ProviderFactory
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.state import StepType
from app.schemas.script import RewriteSelectionRequest, ScriptUpdateRequest, ScriptVersionResponse

router = APIRouter(prefix="/projects", tags=["scripts"])


@router.get("/{project_id}/scripts", response_model=list[ScriptVersionResponse])
async def list_scripts(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScriptVersion)
        .where(ScriptVersion.project_id == project_id)
        .order_by(ScriptVersion.version_number.desc())
    )
    versions = result.scalars().all()
    return [ScriptVersionResponse.model_validate(v) for v in versions]


@router.get("/scripts/{version_id}", response_model=ScriptVersionResponse)
async def get_script(version_id: str, db: AsyncSession = Depends(get_db)):
    version = await db.get(ScriptVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Script version not found")
    return ScriptVersionResponse.model_validate(version)


@router.post("/{project_id}/scripts/generate", response_model=ScriptVersionResponse, status_code=201)
async def generate_script(project_id: str, db: AsyncSession = Depends(get_db)):
    orchestrator = PipelineOrchestrator(db)
    step = await orchestrator.run_step(project_id, StepType.writer)
    if step.status != "completed" or step.output_data is None:
        raise HTTPException(status_code=500, detail="Script generation failed")

    script_data = json.loads(step.output_data)
    script_content = script_data.get("script", {}).get("content", "")

    result = await db.execute(
        select(ScriptVersion)
        .where(ScriptVersion.project_id == project_id)
        .order_by(ScriptVersion.version_number.desc())
    )
    latest = result.scalars().first()
    next_version = (latest.version_number + 1) if latest else 1

    step_map = await orchestrator._get_step_map(project_id)
    hook_text = None
    narrative_pattern = None
    cta_text = None
    hook_step = step_map.get(StepType.hook)
    if hook_step and hook_step.selected_option:
        hook_sel = json.loads(hook_step.selected_option)
        hook_text = hook_sel.get("text")
    narrative_step = step_map.get(StepType.narrative)
    if narrative_step and narrative_step.selected_option:
        narrative_sel = json.loads(narrative_step.selected_option)
        narrative_pattern = narrative_sel.get("pattern_name")
    cta_step = step_map.get(StepType.cta)
    if cta_step and cta_step.selected_option:
        cta_sel = json.loads(cta_step.selected_option)
        cta_text = cta_sel.get("text")

    version = ScriptVersion(
        id=str(uuid4()),
        project_id=project_id,
        version_number=next_version,
        content=script_content,
        format=step_map.get(StepType.writer, step).step_type if StepType.writer in step_map else "unknown",
        hook_text=hook_text,
        narrative_pattern=narrative_pattern,
        cta_text=cta_text,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return ScriptVersionResponse.model_validate(version)


@router.patch("/scripts/{version_id}", response_model=ScriptVersionResponse)
async def update_script(version_id: str, body: ScriptUpdateRequest, db: AsyncSession = Depends(get_db)):
    version = await db.get(ScriptVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Script version not found")
    version.content = body.content
    await db.commit()
    await db.refresh(version)
    return ScriptVersionResponse.model_validate(version)


@router.post("/{project_id}/scripts/rewrite-selection")
async def rewrite_selection_endpoint(
    project_id: str,
    body: RewriteSelectionRequest,
    db: AsyncSession = Depends(get_db),
):
    icp_summary = None
    result = await db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
    icp = result.scalars().first()
    if icp:
        # Parse JSON fields stored as Text in SQLite
        demographics = json.loads(icp.demographics) if isinstance(icp.demographics, str) else icp.demographics
        pain_points = json.loads(icp.pain_points) if isinstance(icp.pain_points, str) else icp.pain_points
        desires = json.loads(icp.desires) if isinstance(icp.desires, str) else icp.desires

        icp_summary = (
            f"Age range: {demographics.get('age_range', 'N/A')}, "
            f"Occupation: {', '.join(demographics.get('occupation', []))}, "
            f"Pain points: {', '.join(pain_points[:3])}, "
            f"Desires: {', '.join(desires[:3])}, "
            f"Language style: {icp.language_style}"
        )

    factory = ProviderFactory(get_settings())
    rewritten = await rewrite_selection(
        factory=factory,
        full_content=body.full_content,
        selected_text=body.selected_text,
        instruction=body.instruction,
        icp_summary=icp_summary,
    )
    return {"rewritten_text": rewritten}
