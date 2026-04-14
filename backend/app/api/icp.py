import json
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import ICPProfile, PipelineStep
from app.pipeline.state import StepType
from app.schemas.icp import ICPProfileResponse, ICPUpdateRequest
from app.services.pipeline_service import PipelineService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects/{project_id}/icp", tags=["icp"])


def _icp_profile_to_response(profile: ICPProfile) -> ICPProfileResponse:
    return ICPProfileResponse(
        id=profile.id,
        project_id=profile.project_id,
        demographics=json.loads(profile.demographics)
        if isinstance(profile.demographics, str)
        else profile.demographics,
        psychographics=json.loads(profile.psychographics)
        if isinstance(profile.psychographics, str)
        else profile.psychographics,
        pain_points=json.loads(profile.pain_points) if isinstance(profile.pain_points, str) else profile.pain_points,
        desires=json.loads(profile.desires) if isinstance(profile.desires, str) else profile.desires,
        objections=json.loads(profile.objections) if isinstance(profile.objections, str) else profile.objections,
        language_style=profile.language_style,
        source=profile.source,
        approved=profile.approved,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.post("/generate", response_model=ICPProfileResponse)
async def generate_icp(project_id: str, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)

    pipeline_service = PipelineService(db)
    await pipeline_service.run_step(project_id, StepType.icp)

    result = await select(ICPProfile).where(ICPProfile.project_id == project_id)
    result = await db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=500, detail="ICP generation failed")
    return _icp_profile_to_response(profile)


@router.get("", response_model=ICPProfileResponse)
async def get_icp(project_id: str, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)

    result = await db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="ICP profile not found")
    return _icp_profile_to_response(profile)


@router.patch("", response_model=ICPProfileResponse)
async def update_icp(project_id: str, body: ICPUpdateRequest, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)

    result = await db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="ICP profile not found")

    update_data = body.model_dump(exclude_unset=True)
    if "demographics" in update_data and update_data["demographics"] is not None:
        from app.schemas.icp import ICPDemographics

        demo = ICPDemographics(**update_data["demographics"])
        profile.demographics = json.dumps(demo.model_dump())
    if "psychographics" in update_data and update_data["psychographics"] is not None:
        from app.schemas.icp import ICPPsychographics

        psycho = ICPPsychographics(**update_data["psychographics"])
        profile.psychographics = json.dumps(psycho.model_dump())
    if "pain_points" in update_data and update_data["pain_points"] is not None:
        profile.pain_points = json.dumps(update_data["pain_points"])
    if "desires" in update_data and update_data["desires"] is not None:
        profile.desires = json.dumps(update_data["desires"])
    if "objections" in update_data and update_data["objections"] is not None:
        profile.objections = json.dumps(update_data["objections"])
    if "language_style" in update_data and update_data["language_style"] is not None:
        profile.language_style = update_data["language_style"]
    if "approved" in update_data and update_data["approved"] is not None:
        profile.approved = update_data["approved"]
        if update_data["approved"]:
            step_result = await db.execute(
                select(PipelineStep).where(
                    PipelineStep.project_id == project_id,
                    PipelineStep.step_type == StepType.icp.value,
                )
            )
            step = step_result.scalar_one_or_none()
            if step:
                step.selected_option = profile.demographics

    await db.commit()
    await db.refresh(profile)
    return _icp_profile_to_response(profile)


DOCUMENTS_DIR = Path("/Users/karpinski94/projects/scripts-writer/documents/icp")


@router.post("/upload", response_model=ICPProfileResponse)
async def upload_icp(project_id: str, file: UploadFile, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)

    content = await file.read()

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DOCUMENTS_DIR / file.filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    demographics = {}
    psychographics = {}
    pain_points = []
    desires = []
    objections = []
    language_style = "professional"

    if file.filename and file.filename.endswith(".json"):
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        demographics = parsed.get("demographics", {})
        psychographics = parsed.get("psychographics", {})
        pain_points = parsed.get("pain_points", [])
        desires = parsed.get("desires", [])
        objections = parsed.get("objections", [])
        language_style = parsed.get("language_style", "professional")
    else:
        raw_text = content.decode("utf-8", errors="replace")
        demographics = {"raw_text": raw_text[:500]}

    result = await db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.demographics = json.dumps(demographics)
        existing.psychographics = json.dumps(psychographics)
        existing.pain_points = json.dumps(pain_points)
        existing.desires = json.dumps(desires)
        existing.objections = json.dumps(objections)
        existing.language_style = language_style
        existing.source = "uploaded"
        existing.approved = False
    else:
        profile = ICPProfile(
            project_id=project_id,
            demographics=json.dumps(demographics),
            psychographics=json.dumps(psychographics),
            pain_points=json.dumps(pain_points),
            desires=json.dumps(desires),
            objections=json.dumps(objections),
            language_style=language_style,
            source="uploaded",
            approved=False,
        )
        db.add(profile)

    await db.commit()
    if existing:
        await db.refresh(existing)
        return _icp_profile_to_response(existing)
    else:
        await db.refresh(profile)
        return _icp_profile_to_response(profile)
