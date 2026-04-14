import logging
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PipelineStep, Project
from app.pipeline.state import STEP_ORDER, StepStatus, StepType
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest, SubjectUpdateRequest

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProjectCreateRequest) -> Project:
        logger.info(f"[PROJECT-SERVICE] Creating project with name: {data.name}")
        project = Project(
            id=str(uuid4()),
            name=data.name,
        )
        logger.debug(f"[PROJECT-SERVICE] Generated project ID: {project.id}")
        self.db.add(project)
        await self.db.flush()
        logger.debug(f"[PROJECT-SERVICE] Project flushed, creating {len(STEP_ORDER)} pipeline steps")

        for order, step_type in enumerate(STEP_ORDER):
            step = PipelineStep(
                id=str(uuid4()),
                project_id=project.id,
                step_type=step_type.value,
                step_order=order,
                status=StepStatus.pending.value,
            )
            logger.debug(f"[PROJECT-SERVICE] Creating step: {step_type.value} (order: {order})")
            self.db.add(step)

        await self.db.commit()
        await self.db.refresh(project)
        logger.info(f"[PROJECT-SERVICE] Project created successfully: {project.id}")
        return project

    async def update_subject(self, project_id: str, data: SubjectUpdateRequest) -> Project:
        logger.info(f"[PROJECT-SERVICE] Updating subject for project: {project_id}")
        logger.debug(
            f"[PROJECT-SERVICE] Subject update data: topic={data.topic[:50]}..., target_format={data.target_format}, content_goal={data.content_goal}"
        )

        project = await self.get_by_id(project_id)
        project.topic = data.topic
        project.target_format = data.target_format
        project.content_goal = data.content_goal
        project.raw_notes = data.raw_notes
        logger.debug(f"[PROJECT-SERVICE] Project fields updated")

        subject_step = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.step_type == StepType.subject.value,
            )
        )
        step = subject_step.scalar_one_or_none()
        if step:
            step.status = StepStatus.completed.value
            step.completed_at = datetime.now(UTC).replace(tzinfo=None)
            logger.debug(f"[PROJECT-SERVICE] Subject step marked as completed")

        await self.db.commit()
        await self.db.refresh(project)
        logger.info(f"[PROJECT-SERVICE] Subject updated successfully for project: {project_id}")
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

    async def branch_project(self, project_id: str, branch_from_step: str, name: str) -> Project:
        project = await self.get_by_id(project_id)

        new_project = Project(
            id=str(uuid4()),
            name=name,
            topic=project.topic,
            target_format=project.target_format,
            content_goal=project.content_goal,
            raw_notes=project.raw_notes,
        )
        self.db.add(new_project)
        await self.db.flush()

        from app.pipeline.state import STEP_ORDER, StepStatus

        branch_idx = None
        for i, st in enumerate(STEP_ORDER):
            if st.value == branch_from_step:
                branch_idx = i
                break
        if branch_idx is None:
            raise HTTPException(status_code=400, detail=f"Invalid step type: {branch_from_step}")

        result = await self.db.execute(
            select(PipelineStep).where(PipelineStep.project_id == project_id).order_by(PipelineStep.step_order)
        )
        original_steps = list(result.scalars().all())

        for order, step_type in enumerate(STEP_ORDER):
            original = next((s for s in original_steps if s.step_type == step_type.value), None)
            if order <= branch_idx and original and original.status == StepStatus.completed.value:
                step = PipelineStep(
                    id=str(uuid4()),
                    project_id=new_project.id,
                    step_type=step_type.value,
                    step_order=order,
                    status=StepStatus.completed.value,
                    output_data=original.output_data,
                    selected_option=original.selected_option,
                    llm_provider=original.llm_provider,
                    token_count=original.token_count,
                    duration_ms=original.duration_ms,
                    started_at=original.started_at,
                    completed_at=original.completed_at,
                )
            else:
                step = PipelineStep(
                    id=str(uuid4()),
                    project_id=new_project.id,
                    step_type=step_type.value,
                    step_order=order,
                    status=StepStatus.pending.value,
                )
            self.db.add(step)

        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project
