import asyncio
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.copyright_agent import CopyrightAgent
from app.agents.cta_agent import CTAAgent
from app.agents.factcheck_agent import FactCheckAgent
from app.agents.hook_agent import HookAgent
from app.agents.icp_agent import ICPAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.readability_agent import ReadabilityAgent
from app.agents.retention_agent import RetentionAgent
from app.agents.writer_agent import WriterAgent
from app.db.models import PipelineStep, Project, ScriptVersion
from app.llm.cache import LLMCache
from app.llm.provider_factory import ProviderFactory
from app.pipeline.errors import AgentExecutionError
from app.pipeline.state import STEP_ORDER, StepStatus, StepType, has_retention, validate_step_ready, validate_transition
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
from app.schemas.analysis import (
    CopyrightAgentInput,
    FactCheckAgentInput,
    PolicyAgentInput,
    ReadabilityAgentInput,
)
from app.schemas.icp import ICPAgentInput, ICPProfile
from app.ws.handlers import ConnectionManager

logger = structlog.get_logger()


class PipelineOrchestrator:
    def __init__(self, db: AsyncSession, ws_manager: ConnectionManager | None = None):
        self.db = db
        self.ws_manager = ws_manager

    async def run_step(self, project_id: str, step_type: StepType) -> PipelineStep:
        logger.info(f"[ORCHESTRATOR] Starting step: {step_type.value} for project: {project_id}")

        project = await self.db.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        logger.debug(f"[ORCHESTRATOR] Project details - topic: {project.topic}, target_format: {project.target_format}")

        step = await self._get_or_create_step(project_id, step_type)
        logger.debug(f"[ORCHESTRATOR] Current step status: {step.status}")

        if step_type == StepType.retention and not has_retention(project.target_format):
            logger.info(f"[ORCHESTRATOR] Skipping retention step for non-video format: {project.target_format}")
            step.status = StepStatus.completed.value
            step.completed_at = datetime.now(UTC).replace(tzinfo=None)
            await self.db.commit()
            return step

        completed_types = await self._get_completed_step_types(project_id)
        logger.debug(f"[ORCHESTRATOR] Completed steps: {[s.value for s in completed_types]}")
        validate_step_ready(step_type, completed_types, project.target_format)

        if StepStatus(step.status) == StepStatus.completed:
            logger.info(f"[ORCHESTRATOR] Step {step_type.value} was completed, resetting to pending")
            step.status = StepStatus.pending.value
            step.output_data = None
            step.selected_option = None
            await self._invalidate_downstream(project_id, step_type)
            await self.db.commit()
            await self.db.refresh(step)

        validate_transition(step.step_type, StepStatus(step.status), StepStatus.running)
        step.status = StepStatus.running.value

        step.started_at = datetime.now(UTC).replace(tzinfo=None)
        step.llm_provider = "default"
        await self.db.commit()

        if self.ws_manager:
            await self.ws_manager.broadcast(
                project_id,
                {
                    "event": "agent_start",
                    "step_type": step_type.value,
                },
            )

        logger.info(f"[ORCHESTRATOR] Step {step_type.value} set to running")
        start_ms = time.time()

        if step_type == StepType.subject:
            step.output_data = "{}"
            step.status = StepStatus.completed.value
            step.completed_at = datetime.now(UTC).replace(tzinfo=None)
            step.duration_ms = int((time.time() - start_ms) * 1000)
            await self.db.commit()
            if self.ws_manager:
                await self.ws_manager.broadcast(
                    project_id,
                    {
                        "event": "agent_complete",
                        "step_type": step_type.value,
                    },
                )
            return step

        try:
            logger.info(f"[ORCHESTRATOR] Building agent inputs for step: {step_type.value}")
            step_map = await self._get_step_map(project_id)
            agent, input_data = await self._build_agent_inputs(project, step_type, step_map)

            if agent is None and isinstance(input_data, dict):
                step.output_data = json.dumps(input_data)
                step.status = StepStatus.completed.value
                step.completed_at = datetime.now(UTC).replace(tzinfo=None)
                step.duration_ms = int((time.time() - start_ms) * 1000)

                logger.info(
                    "agent_step_completed",
                    agent_name=step_type.value,
                    step_type=step_type.value,
                    project_id=project_id,
                    duration_ms=step.duration_ms,
                    status="completed",
                )

                if self.ws_manager:
                    await self.ws_manager.broadcast(
                        project_id,
                        {
                            "event": "agent_complete",
                            "step_type": step_type.value,
                            "output_data": input_data,
                        },
                    )
                await self.db.commit()
                await self.db.refresh(step)
                return step

            logger.debug(f"[ORCHESTRATOR] Agent type: {type(agent).__name__}")
            logger.debug(f"[ORCHESTRATOR] Input data keys: {list(input_data.model_dump().keys())}")

            from app.config import get_settings

            factory = ProviderFactory(get_settings())
            cache = LLMCache(max_size=get_settings().cache_max_size, ttl_seconds=get_settings().cache_ttl_seconds)
            logger.info(f"[ORCHESTRATOR] Executing agent for step: {step_type.value}")

            result = await agent.execute(input_data, cache, factory)

            step.output_data = json.dumps(result.model_dump())
            step.status = StepStatus.completed.value
            step.completed_at = datetime.now(UTC).replace(tzinfo=None)
            step.duration_ms = int((time.time() - start_ms) * 1000)
            step.llm_provider = factory._default_provider if hasattr(factory, "_default_provider") else "default"

            logger.info(
                "agent_step_completed",
                agent_name=step_type.value,
                step_type=step_type.value,
                project_id=project_id,
                duration_ms=step.duration_ms,
                provider=step.llm_provider,
                status="completed",
            )

            if step_type == StepType.icp:
                await self._save_icp_profile(project_id, result)

            if step_type == StepType.writer:
                await self._save_script_version(project_id, result)

            if self.ws_manager:
                await self.ws_manager.broadcast(
                    project_id,
                    {
                        "event": "agent_complete",
                        "step_type": step_type.value,
                        "output_data": result.model_dump(),
                    },
                )

        except Exception as e:
            step.status = StepStatus.failed.value
            step.error_message = str(e)
            step.duration_ms = int((time.time() - start_ms) * 1000)
            logger.error(
                "agent_step_failed",
                agent_name=step_type.value,
                step_type=step_type.value,
                project_id=project_id,
                duration_ms=step.duration_ms,
                provider="default",
                status="failed",
                error=str(e),
            )
            if self.ws_manager:
                await self.ws_manager.broadcast(
                    project_id,
                    {
                        "event": "agent_failed",
                        "step_type": step_type.value,
                        "error": str(e),
                    },
                )
            raise AgentExecutionError(step_type.value, str(e)) from e
        finally:
            await self.db.commit()
            await self.db.refresh(step)

        return step

    async def invalidate_downstream(self, project_id: str, from_step: StepType) -> None:
        await self._invalidate_downstream(project_id, from_step)

    async def _build_agent_inputs(
        self, project: Project, step_type: StepType, step_map: dict[StepType, PipelineStep]
    ) -> tuple:
        logger.info(f"[ORCHESTRATOR] Building agent inputs for step: {step_type.value}")

        piragi_context = await self._resolve_rag_context(project, step_type)
        logger.debug(f"[ORCHESTRATOR] PIRAGI context length: {len(piragi_context) if piragi_context else 0}")

        if step_type == StepType.subject:
            return {}, {}

        project_slug = project.name.lower().replace(" ", "-")
        docs_base = Path(f"/Users/karpinski94/projects/scripts-writer/documents/{project_slug}")
        playbooks_base = Path("/Users/karpinski94/projects/scripts-writer/documents/playbooks")

        if step_type == StepType.icp:
            logger.info("[ORCHESTRATOR] Building ICP agent input")
            raw_notes = project.raw_notes or ""
            logger.debug(f"[ORCHESTRATOR] ICP raw_notes length: {len(raw_notes)}")

            faiss_context = ""
            project_icp_dir = docs_base / "icp"

            try:
                from app.rag.faiss_service import (
                    ICP_QUERY,
                    create_index,
                    index_exists,
                    load_documents,
                    search_project_documents,
                )

                if project_icp_dir.exists():
                    txt_files = list(project_icp_dir.glob("*.txt"))
                    if txt_files and not index_exists(project.id):
                        documents = load_documents(str(project_icp_dir))
                        create_index(documents, project.id)
                        logger.info(f"[ORCHESTRATOR] Created FAISS index for project {project.id}")

                    if index_exists(project.id):
                        results = search_project_documents(project.id, ICP_QUERY, k=5)
                        if results:
                            retrieved_chunks = "\n\n".join(
                                [
                                    f"[Source: {meta['source']}, Distance: {dist:.2f}]\n{text}"
                                    for text, meta, dist in results
                                ]
                            )
                            faiss_context = f"Retrieved context from project documents:\n{retrieved_chunks}"
                            logger.debug(f"[ORCHESTRATOR] FAISS retrieved {len(results)} chunks")
            except Exception as e:
                logger.warning(f"[ORCHESTRATOR] FAISS search failed: {e}, using raw_notes only")

            agent = ICPAgent()
            input_data = ICPAgentInput(
                raw_notes=raw_notes,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
                faiss_context=faiss_context,
            )
            logger.info(
                f"[ORCHESTRATOR] ICP input built - topic: {project.topic}, target_format: {project.target_format}"
            )
            return agent, input_data

        icp = self._extract_icp(step_map)
        logger.debug(f"[ORCHESTRATOR] Extracted ICP: {type(icp).__name__ if icp else 'None'}")

        if step_type == StepType.hook:
            logger.info("[ORCHESTRATOR] Building Hook agent input")
            hook_context = ""

            icp_summary = ""
            if icp:
                demographics = icp.demographics
                pain_pts = ", ".join(icp.pain_points[:3]) if icp.pain_points else ""
                desires = ", ".join(icp.desires[:3]) if icp.desires else ""
                icp_summary = (
                    f"ICP: age={demographics.age_range}, gender={demographics.gender}, "
                    f"income={demographics.income_level}, pain_points={pain_pts}, desires={desires}"
                )

            query = f"{project.topic or ''} {project.draft[:200] if project.draft else ''} {icp_summary}"

            try:
                from app.rag.faiss_service import (
                    global_index_exists,
                    search_global_documents,
                )

                if global_index_exists("global_hooks"):
                    results = search_global_documents("global_hooks", query, k=5)
                    if results:
                        hook_chunks = "\n\n".join(
                            [
                                f"[Source: {meta['source']}, Distance: {dist:.2f}]\n{text}"
                                for text, meta, dist in results
                            ]
                        )
                        hook_context = f"Retrieved hook examples:\n{hook_chunks}"
                        logger.debug(f"[ORCHESTRATOR] FAISS retrieved {len(results)} hook examples")
            except Exception as e:
                logger.warning(f"[ORCHESTRATOR] FAISS hook search failed: {e}, using empty context")

            agent = HookAgent()
            input_data = HookAgentInput(
                icp=icp,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
                draft=project.draft,
                piragi_context=hook_context or piragi_context,
            )
            logger.info(f"[ORCHESTRATOR] Hook input built - topic: {project.topic}, has_icp: {bool(icp)}")
            return agent, input_data

        selected_hook = self._extract_selected(step_map, StepType.hook, HookSuggestion)
        logger.debug(f"[ORCHESTRATOR] Selected hook: {selected_hook.text[:50] if selected_hook else 'None'}...")

        if step_type == StepType.narrative:
            logger.info("[ORCHESTRATOR] Building Narrative agent input")
            narrative_context = ""

            icp_summary = ""
            if icp:
                demographics = icp.demographics
                pain_pts = ", ".join(icp.pain_points[:3]) if icp.pain_points else ""
                desires = ", ".join(icp.desires[:3]) if icp.desires else ""
                icp_summary = (
                    f"ICP: age={demographics.age_range}, gender={demographics.gender}, "
                    f"income={demographics.income_level}, pain_points={pain_pts}, desires={desires}"
                )

            hook_text = selected_hook.text if selected_hook else ""
            query = f"{project.topic or ''} {project.draft[:200] if project.draft else ''} {hook_text} {icp_summary}"

            try:
                from app.rag.faiss_service import (
                    global_index_exists,
                    search_global_documents,
                )

                if global_index_exists("global_narratives"):
                    results = search_global_documents("global_narratives", query, k=5)
                    if results:
                        narrative_chunks = "\n\n".join(
                            [
                                f"[Source: {meta['source']}, Distance: {dist:.2f}]\n{text}"
                                for text, meta, dist in results
                            ]
                        )
                        narrative_context = f"Retrieved narrative templates:\n{narrative_chunks}"
                        logger.debug(f"[ORCHESTRATOR] FAISS retrieved {len(results)} narrative examples")
            except Exception as e:
                logger.warning(f"[ORCHESTRATOR] FAISS narrative search failed: {e}, using empty context")

            agent = NarrativeAgent()
            input_data = NarrativeAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                topic=project.topic,
                target_format=project.target_format,
                draft=project.draft,
                piragi_context=narrative_context or piragi_context,
            )
            logger.info(f"[ORCHESTRATOR] Narrative input built - topic: {project.topic}")
            return agent, input_data

        selected_narrative = self._extract_selected(step_map, StepType.narrative, NarrativePattern)
        logger.debug(
            f"[ORCHESTRATOR] Selected narrative: {selected_narrative.pattern_name if selected_narrative else 'None'}"
        )

        if step_type == StepType.retention:
            logger.info("[ORCHESTRATOR] Building Retention agent input")
            retention_context = ""

            project_retention_dir = docs_base / "retention"
            if project_retention_dir.exists():
                files = list(project_retention_dir.glob("*"))
                if files:
                    for f in files[:1]:
                        if f.is_file() and f.suffix in [".txt", ".md", ".json"]:
                            retention_context = f"Project retention reference:\n{f.read_text()}\n\n"

            playbook_retention_dir = playbooks_base / "retention_tactics"
            if playbook_retention_dir.exists():
                files = sorted(
                    [
                        f
                        for f in playbook_retention_dir.glob("*")
                        if f.is_file() and f.suffix in [".txt", ".md", ".json"]
                    ]
                )
                if files:
                    for f in files:
                        retention_context += f"=== {f.name} ===\n{f.read_text()}\n\n"

            agent = RetentionAgent()
            input_data = RetentionAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                selected_narrative=selected_narrative,
                target_format=project.target_format,
                content_goal=project.content_goal,
                draft=project.draft,
                piragi_context=retention_context or piragi_context,
            )
            logger.info("[ORCHESTRATOR] Retention input built")
            return agent, input_data

        selected_retention = None
        if has_retention(project.target_format):
            selected_retention = self._extract_selected(step_map, StepType.retention, RetentionTechnique)
        if isinstance(selected_retention, list):
            logger.debug(f"[ORCHESTRATOR] Selected retention: {len(selected_retention)} techniques")
        else:
            logger.debug(
                f"[ORCHESTRATOR] Selected retention: "
                f"{selected_retention.technique_name if selected_retention else 'None'}"
            )

        if step_type == StepType.cta:
            logger.info("[ORCHESTRATOR] Building CTA agent input")
            agent = CTAAgent()
            input_data = CTAAgentInput(
                icp=icp,
                selected_hook=selected_hook,
                selected_narrative=selected_narrative,
                content_goal=project.content_goal,
                cta_purpose=project.cta_purpose,
                draft=project.draft,
                piragi_context=piragi_context,
            )
            logger.info("[ORCHESTRATOR] CTA input built")
            return agent, input_data

        if step_type == StepType.writer:
            from app.schemas.agents import CTASuggestion

            selected_cta = self._extract_selected(step_map, StepType.cta, CTASuggestion)
            logger.debug(f"[ORCHESTRATOR] Selected CTA: {selected_cta.text if selected_cta else 'None'}")

            logger.info("[ORCHESTRATOR] Building Writer agent input")
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
                draft=project.draft,
                raw_notes=project.raw_notes,
                piragi_context=piragi_context,
            )
            logger.info(
                f"[ORCHESTRATOR] Writer input built - topic: {project.topic}, "
                f"has_retention: {bool(selected_retention)}, has_cta: {bool(selected_cta)}"
            )
            return agent, input_data

        def _build_single_analysis_agent(agent_type: StepType, project: Project, script_content: str):
            if agent_type == StepType.factcheck:
                agent = FactCheckAgent()
                input_data = FactCheckAgentInput(
                    script_content=script_content,
                    topic=project.topic,
                    target_format=project.target_format,
                )
                return agent, input_data
            if agent_type == StepType.readability:
                agent = ReadabilityAgent()
                input_data = ReadabilityAgentInput(
                    script_content=script_content,
                    target_format=project.target_format,
                )
                return agent, input_data
            if agent_type == StepType.copyright:
                agent = CopyrightAgent()
                input_data = CopyrightAgentInput(
                    script_content=script_content,
                    topic=project.topic,
                    target_format=project.target_format,
                )
                return agent, input_data
            if agent_type == StepType.policy:
                agent = PolicyAgent()
                input_data = PolicyAgentInput(
                    script_content=script_content,
                    topic=project.topic,
                    target_format=project.target_format,
                )
                return agent, input_data
            raise ValueError(f"Unknown analysis agent type: {agent_type}")

        if step_type == StepType.factcheck:
            script_content = await self._get_latest_script_content(project.id)
            agent, input_data = _build_single_analysis_agent(StepType.factcheck, project, script_content)
            return agent, input_data

        if step_type == StepType.readability:
            script_content = await self._get_latest_script_content(project.id)
            agent, input_data = _build_single_analysis_agent(StepType.readability, project, script_content)
            return agent, input_data

        if step_type == StepType.copyright:
            script_content = await self._get_latest_script_content(project.id)
            agent, input_data = _build_single_analysis_agent(StepType.copyright, project, script_content)
            return agent, input_data

        if step_type == StepType.policy:
            script_content = await self._get_latest_script_content(project.id)
            agent, input_data = _build_single_analysis_agent(StepType.policy, project, script_content)
            return agent, input_data

        if step_type == StepType.analysis:
            script_content = await self._get_latest_script_content(project.id)
            results = {}
            for agent_type in [StepType.factcheck, StepType.readability, StepType.copyright, StepType.policy]:
                try:
                    agent, input_data = self._build_single_analysis_agent(agent_type, project, script_content)
                    from app.config import get_settings

                    factory = ProviderFactory(get_settings())
                    cache = LLMCache(
                        max_size=get_settings().cache_max_size, ttl_seconds=get_settings().cache_ttl_seconds
                    )
                    result = await agent.execute(input_data, cache, factory)
                    results[agent_type.value] = result.model_dump()
                except Exception as e:
                    logger.warning("Analysis step %s failed: %s", agent_type.value, e)
                    results[agent_type.value] = {"error": str(e)}
            from app.schemas.analysis import AnalysisOutput

            output = AnalysisOutput(
                factcheck=results.get("factcheck", {}),
                readability=results.get("readability", {}),
                copyright=results.get("copyright", {}),
                policy=results.get("policy", {}),
            )
            logger.info(f"[ORCHESTRATOR] Analysis completed for project: {project.id}")
            return None, output.model_dump()

        raise ValueError(f"No agent configured for step type: {step_type}")

    async def _resolve_rag_context(self, project: Project, step_type: StepType) -> str | None:
        if not project.piragi_document_paths:
            return None
        try:
            from app.services.piragi_service import PiragiService

            service = PiragiService(self.db)
            return await service.get_step_context(project.id, step_type)
        except Exception:
            logger.warning("Piragi context resolution failed for project %s step %s", project.id, step_type.value)
            return None

    async def _get_latest_script_content(self, project_id: str) -> str:
        result = await self.db.execute(
            select(ScriptVersion)
            .where(ScriptVersion.project_id == project_id)
            .order_by(ScriptVersion.version_number.desc())
            .limit(1)
        )
        version = result.scalar_one_or_none()
        if version is None:
            raise ValueError(f"No script version found for project {project_id}")
        return version.content

    async def run_analysis_parallel(self, project_id: str) -> list[PipelineStep]:
        analysis_types = [StepType.factcheck, StepType.readability, StepType.copyright, StepType.policy]

        async def _run(step_type: StepType):
            try:
                return await self.run_step(project_id, step_type)
            except Exception as e:
                logger.error("Analysis step %s failed for project %s: %s", step_type.value, project_id, e)
                return e

        results = await asyncio.gather(*[_run(st) for st in analysis_types], return_exceptions=True)
        steps = []
        for r in results:
            if isinstance(r, PipelineStep):
                steps.append(r)
        return steps

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
            return None
        if step.selected_option:
            data = json.loads(step.selected_option)
            if isinstance(data, list):
                if step_type == StepType.retention:
                    return [model_cls.model_validate(item) for item in data]
                return model_cls.model_validate(data[0]) if data else None
            return model_cls.model_validate(data)
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
                if step_type == StepType.retention:
                    return [model_cls.model_validate(item) for item in items]
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

    async def _save_script_version(self, project_id: str, result) -> None:
        from app.db.models import ScriptVersion

        script_data = result.script
        content = script_data.content if hasattr(script_data, "content") else str(script_data)

        existing = await self.db.execute(
            select(ScriptVersion)
            .where(ScriptVersion.project_id == project_id)
            .order_by(ScriptVersion.version_number.desc())
            .limit(1)
        )
        latest = existing.scalars().first()
        version_number = (latest.version_number + 1) if latest else 1

        version = ScriptVersion(
            id=str(uuid4()),
            project_id=project_id,
            version_number=version_number,
            content=content,
            format="VSL",
        )
        self.db.add(version)
        await self.db.commit()
