from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectSummaryResponse,
    ProjectUpdateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(body: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.create(body)


@router.get("", response_model=list[ProjectSummaryResponse])
async def list_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.list_all(skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.get_by_id(project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, body: ProjectUpdateRequest, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    return await service.update(project_id, body)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    await service.delete(project_id)
