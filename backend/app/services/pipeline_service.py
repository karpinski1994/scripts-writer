import json
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PipelineStep, Project
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.state import StepStatus, StepType, has_retention
from app.schemas.pipeline import PipelineResponse, PipelineStepResponse, StepUpdateRequest
from app.ws.handlers import ConnectionManager

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, db: AsyncSession, ws_manager: ConnectionManager | None = None):
        self.db = db
        self.ws_manager = ws_manager

    async def get_pipeline(self, project_id: str) -> PipelineResponse:
        project = await self.db.get(Project, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        result = await self.db.execute(
            select(PipelineStep).where(PipelineStep.project_id == project_id).order_by(PipelineStep.step_order)
        )
        steps = result.scalars().all()

        show_retention = has_retention(project.target_format)
        if not show_retention:
            steps = [s for s in steps if s.step_type != StepType.retention.value]

        step_responses = [PipelineStepResponse.model_validate(s) for s in steps]
        current_step = 0
        for s in steps:
            if s.status == StepStatus.completed.value:
                current_step = s.step_order + 1
        return PipelineResponse(project_id=project_id, current_step=current_step, steps=step_responses)

    async def run_step(self, project_id: str, step_type: StepType) -> PipelineStepResponse:
        orchestrator = PipelineOrchestrator(self.db, ws_manager=self.ws_manager)
        step = await orchestrator.run_step(project_id, step_type)
        return PipelineStepResponse.model_validate(step)

    async def update_step(self, project_id: str, step_id: str, data: StepUpdateRequest) -> PipelineStepResponse:
        step = await self.db.get(PipelineStep, step_id)
        if step is None or step.project_id != project_id:
            raise HTTPException(status_code=404, detail="Pipeline step not found")
        if data.selected_option is not None:
            step.selected_option = json.dumps(data.selected_option)
            if step.status == StepStatus.completed.value:
                orchestrator = PipelineOrchestrator(self.db, ws_manager=self.ws_manager)
                await orchestrator.invalidate_downstream(project_id, StepType(step.step_type))
        await self.db.commit()
        await self.db.refresh(step)
        return PipelineStepResponse.model_validate(step)

    async def cancel_all_steps(self, project_id: str) -> None:
        result = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.status == StepStatus.running.value,
            )
        )
        steps = result.scalars().all()
        for step in steps:
            step.status = StepStatus.failed.value
            step.error_message = None
            logger.info(f"Cancelled step {step.step_type} for project {project_id}")
        await self.db.commit()
        if self.ws_manager:
            await self.ws_manager.broadcast(
                project_id,
                {"event": "pipeline_cancelled", "project_id": project_id},
            )

    async def reset_failed_steps(self, project_id: str) -> None:
        result = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.status == StepStatus.failed.value,
            )
        )
        steps = result.scalars().all()
        for step in steps:
            step.status = StepStatus.pending.value
            step.error_message = None
            logger.info(f"Reset step {step.step_type} for project {project_id}")
        await self.db.commit()
        if self.ws_manager:
            await self.ws_manager.broadcast(
                project_id,
                {"event": "pipeline_reset", "project_id": project_id},
            )
