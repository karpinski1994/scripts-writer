from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProjectCreateRequest) -> Project:
        project = Project(
            id=str(uuid4()),
            name=data.name,
            topic=data.topic,
            target_format=data.target_format.value,
            content_goal=data.content_goal.value if data.content_goal else None,
            raw_notes=data.raw_notes,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Project]:
        result = await self.db.execute(select(Project).offset(skip).limit(limit).order_by(Project.updated_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, project_id: str) -> Project:
        project = await self.db.get(Project, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def update(self, project_id: str, data: ProjectUpdateRequest) -> Project:
        project = await self.get_by_id(project_id)
        update_data = data.model_dump(exclude_unset=True)
        if "target_format" in update_data and update_data["target_format"] is not None:
            update_data["target_format"] = update_data["target_format"].value
        if "content_goal" in update_data:
            update_data["content_goal"] = update_data["content_goal"].value if update_data["content_goal"] else None
        for field, value in update_data.items():
            setattr(project, field, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: str) -> None:
        project = await self.get_by_id(project_id)
        await self.db.delete(project)
        await self.db.commit()
