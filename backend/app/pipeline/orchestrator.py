import json
import logging
import time
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.cta_agent import CTAAgent
from app.agents.hook_agent import HookAgent
from app.agents.icp_agent import ICPAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.retention_agent import RetentionAgent
from app.agents.writer_agent import WriterAgent
from app.db.models import PipelineStep, Project
from app.llm.cache import LLMCache
from app.llm.provider_factory import ProviderFactory
from app.pipeline.errors import AgentExecutionError
from app.pipeline.state import STEP_ORDER, StepStatus, StepType, validate_step_ready, validate_transition
from app.schemas.agents import (
    CTAAgentInput,
    HookAgentInput,
    HookSuggestion,
    NarrativeAgentInput,
    NarrativePattern,
    RetentionAgentInput,
    RetentionTechnique,
    WriterAgentInput,
)
from app.schemas.icp import ICPAgentInput, ICPProfile

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

        if StepStatus(step.status) == StepStatus.completed:
            step.status = StepStatus.pending.value
            step.output_data = None
            step.selected_option = None
            await self._invalidate_downstream(project_id, step_type)
            await self.db.commit()
            await self.db.refresh(step)

        validate_transition(step.step_type, StepStatus(step.status), StepStatus.running)
        step.status = StepStatus.running.value
        from datetime import UTC, datetime

        step.started_at = datetime.now(UTC).replace(tzinfo=None)
        step.llm_provider = "default"
        await self.db.commit()

        start_ms = time.time()
        try:
            step_map = await self._get_step_map(project_id)
            agent, input_data = self._build_agent_inputs(project, step_type, step_map)
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

    async def invalidate_downstream(self, project_id: str, from_step: StepType) -> None:
        await self._invalidate_downstream(project_id, from_step)

    def _build_agent_inputs(
        self, project: Project, step_type: StepType, step_map: dict[StepType, PipelineStep]
    ) -> tuple:
        if step_type == StepType.icp:
            agent = ICPAgent()
            input_data = ICPAgentInput(
                raw_notes=project.raw_notes,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
            )
            return agent, input_data

        icp = self._extract_icp(step_map)

        if step_type == StepType.hook:
            agent = HookAgent()
            input_data = HookAgentInput(
                icp=icp,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
            )
            return agent, input_data

        selected_hook = self._extract_selected(step_map, StepType.hook, HookSuggestion)

        if step_type == StepType.narrative:
            agent = NarrativeAgent()
            input_data = NarrativeAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                topic=project.topic,
                target_format=project.target_format,
            )
            return agent, input_data

        selected_narrative = self._extract_selected(step_map, StepType.narrative, NarrativePattern)

        if step_type == StepType.retention:
            agent = RetentionAgent()
            input_data = RetentionAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                selected_narrative=selected_narrative,
                target_format=project.target_format,
            )
            return agent, input_data

        selected_retention = self._extract_selected(step_map, StepType.retention, RetentionTechnique)

        if step_type == StepType.cta:
            agent = CTAAgent()
            input_data = CTAAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                selected_narrative=selected_narrative,
                content_goal=project.content_goal,
            )
            return agent, input_data

        if step_type == StepType.writer:
            from app.schemas.agents import CTASuggestion

            selected_cta = self._extract_selected(step_map, StepType.cta, CTASuggestion)
            agent = WriterAgent()
            input_data = WriterAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                selected_narrative=selected_narrative,
                selected_retention=selected_retention,
                selected_cta=selected_cta,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
                raw_notes=project.raw_notes,
            )
            return agent, input_data

        raise ValueError(f"No agent configured for step type: {step_type}")

    def _extract_icp(self, step_map: dict[StepType, PipelineStep]) -> ICPProfile:
        icp_step = step_map.get(StepType.icp)
        if icp_step is None or icp_step.output_data is None:
            raise ValueError("ICP step has no output data")
        data = json.loads(icp_step.output_data)
        if "icp" in data:
            return ICPProfile.model_validate(data["icp"])
        return ICPProfile.model_validate(data)

    def _extract_selected(self, step_map: dict[StepType, PipelineStep], step_type: StepType, model_cls):
        step = step_map.get(step_type)
        if step is None:
            raise ValueError(f"Step {step_type.value} not found in step map")
        if step.selected_option:
            return model_cls.model_validate(json.loads(step.selected_option))
        if step.output_data:
            data = json.loads(step.output_data)
            key_map = {
                StepType.hook: "hooks",
                StepType.narrative: "patterns",
                StepType.retention: "techniques",
                StepType.cta: "ctas",
            }
            items = data.get(key_map.get(step_type, ""), [])
            if items:
                return model_cls.model_validate(items[0])
        raise ValueError(f"No selected option or output data for step {step_type.value}")

    async def _get_step_map(self, project_id: str) -> dict[StepType, PipelineStep]:
        steps = await self._get_all_steps(project_id)
        return {StepType(s.step_type): s for s in steps}

    async def _get_all_steps(self, project_id: str) -> list[PipelineStep]:
        result = await self.db.execute(select(PipelineStep).where(PipelineStep.project_id == project_id))
        return list(result.scalars().all())

    async def _invalidate_downstream(self, project_id: str, from_step: StepType) -> None:
        from_idx = STEP_ORDER.index(from_step)
        downstream = STEP_ORDER[from_idx + 1 :]
        if not downstream:
            return
        result = await self.db.execute(
            select(PipelineStep).where(
                PipelineStep.project_id == project_id,
                PipelineStep.step_type.in_([s.value for s in downstream]),
            )
        )
        steps = result.scalars().all()
        for step in steps:
            step.status = StepStatus.pending.value
            step.output_data = None
            step.selected_option = None
        await self.db.commit()

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
