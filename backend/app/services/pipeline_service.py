from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PipelineStep
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.state import StepStatus, StepType
from app.schemas.pipeline import PipelineResponse, PipelineStepResponse, StepUpdateRequest


class PipelineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pipeline(self, project_id: str) -> PipelineResponse:
        result = await self.db.execute(
            select(PipelineStep).where(PipelineStep.project_id == project_id).order_by(PipelineStep.step_order)
        )
        steps = result.scalars().all()
        step_responses = [PipelineStepResponse.model_validate(s) for s in steps]
        current_step = 0
        for s in steps:
            if s.status == StepStatus.completed.value:
                current_step = s.step_order + 1
        return PipelineResponse(project_id=project_id, current_step=current_step, steps=step_responses)

    async def run_step(self, project_id: str, step_type: StepType) -> PipelineStepResponse:
        orchestrator = PipelineOrchestrator(self.db)
        step = await orchestrator.run_step(project_id, step_type)
        return PipelineStepResponse.model_validate(step)

    async def update_step(self, project_id: str, step_id: str, data: StepUpdateRequest) -> PipelineStepResponse:
        step = await self.db.get(PipelineStep, step_id)
        if step is None or step.project_id != project_id:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Pipeline step not found")
        if data.selected_option is not None:
            import json

            step.selected_option = json.dumps(data.selected_option)
        await self.db.commit()
        await self.db.refresh(step)
        return PipelineStepResponse.model_validate(step)
