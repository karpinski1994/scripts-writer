import json
import logging
import time
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.icp_agent import ICPAgent
from app.db.models import PipelineStep, Project
from app.llm.cache import LLMCache
from app.llm.provider_factory import ProviderFactory
from app.pipeline.errors import AgentExecutionError
from app.pipeline.state import StepStatus, StepType, validate_step_ready, validate_transition
from app.schemas.icp import ICPAgentInput

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_step(self, project_id: str, step_type: StepType) -> PipelineStep:
        project = await self.db.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        step = await self._get_or_create_step(project_id, step_type)

        completed_types = await self._get_completed_step_types(project_id)
        validate_step_ready(step_type, completed_types)

        validate_transition(step.step_type, StepStatus(step.status), StepStatus.running)
        step.status = StepStatus.running.value
        from datetime import UTC, datetime

        step.started_at = datetime.now(UTC).replace(tzinfo=None)
        step.llm_provider = "default"
        await self.db.commit()

        start_ms = time.time()
        try:
            agent, input_data = self._build_agent_inputs(project, step_type)
            from app.config import get_settings

            factory = ProviderFactory(get_settings())
            cache = LLMCache(max_size=get_settings().cache_max_size, ttl_seconds=get_settings().cache_ttl_seconds)
            result = await agent.execute(input_data, cache, factory)

            step.output_data = json.dumps(result.model_dump())
            step.status = StepStatus.completed.value
            step.completed_at = datetime.now(UTC).replace(tzinfo=None)
            step.duration_ms = int((time.time() - start_ms) * 1000)

            if step_type == StepType.icp:
                await self._save_icp_profile(project_id, result)

        except Exception as e:
            step.status = StepStatus.failed.value
            step.error_message = str(e)
            step.duration_ms = int((time.time() - start_ms) * 1000)
            logger.error(f"Step {step_type} failed for project {project_id}: {e}")
            raise AgentExecutionError(step_type.value, str(e)) from e
        finally:
            await self.db.commit()
            await self.db.refresh(step)

        return step

    def _build_agent_inputs(self, project: Project, step_type: StepType) -> tuple:
        if step_type == StepType.icp:
            agent = ICPAgent()
            input_data = ICPAgentInput(
                raw_notes=project.raw_notes,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
            )
            return agent, input_data
        raise ValueError(f"No agent configured for step type: {step_type}")

    async def _get_or_create_step(self, project_id: str, step_type: StepType) -> PipelineStep:
        result = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.step_type == step_type.value,
            )
        )
        step = result.scalar_one_or_none()
        if step is None:
            step = PipelineStep(
                id=str(uuid4()),
                project_id=project_id,
                step_type=step_type.value,
                step_order=[s for s in StepType].index(step_type),
                status=StepStatus.pending.value,
            )
            self.db.add(step)
            await self.db.commit()
            await self.db.refresh(step)
        return step

    async def _get_completed_step_types(self, project_id: str) -> set[StepType]:
        result = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.status == StepStatus.completed.value,
            )
        )
        steps = result.scalars().all()
        return {StepType(s.step_type) for s in steps}

    async def _save_icp_profile(self, project_id: str, result) -> None:
        from app.db.models import ICPProfile

        existing = await self.db.execute(select(ICPProfile).where(ICPProfile.project_id == project_id))
        profile = existing.scalar_one_or_none()
        icp_data = result.icp

        if profile is None:
            profile = ICPProfile(
                id=str(uuid4()),
                project_id=project_id,
                demographics=json.dumps(icp_data.demographics.model_dump()),
                psychographics=json.dumps(icp_data.psychographics.model_dump()),
                pain_points=json.dumps(icp_data.pain_points),
                desires=json.dumps(icp_data.desires),
                objections=json.dumps(icp_data.objections),
                language_style=icp_data.language_style,
                source="generated",
                approved=False,
            )
            self.db.add(profile)
        else:
            profile.demographics = json.dumps(icp_data.demographics.model_dump())
            profile.psychographics = json.dumps(icp_data.psychographics.model_dump())
            profile.pain_points = json.dumps(icp_data.pain_points)
            profile.desires = json.dumps(icp_data.desires)
            profile.objections = json.dumps(icp_data.objections)
            profile.language_style = icp_data.language_style
            profile.source = "generated"
            profile.approved = False

        await self.db.commit()
