## 1. Dependencies & Agent Schemas

- [ ] 1.1 Install `aiofiles` dependency: `uv add aiofiles` in backend/
- [ ] 1.2 Create `backend/app/schemas/agents.py` — `HookSuggestion`, `HookAgentInput`, `HookAgentOutput`, `NarrativePattern`, `NarrativeAgentInput`, `NarrativeAgentOutput`, `RetentionTechnique`, `RetentionAgentInput`, `RetentionAgentOutput`, `CTASuggestion`, `CTAAgentInput`, `CTAAgentOutput`, `ScriptDraft`, `WriterAgentInput`, `WriterAgentOutput`. Use `ICPProfile` from `app.schemas.icp` (not redefined). HookAgentInput.icp should be `ICPProfile` type, etc. Note: existing ICPDemographics has fields `age_range`, `gender`, `income_level`, `education`, `location`, `occupation` (all str) — use these, not the LLD version.
- [ ] 1.3 Verify: `uv run python -c "from app.schemas.agents import HookAgentInput, NarrativeAgentInput, RetentionAgentInput, CTAAgentInput, WriterAgentInput; print('ok')"`

## 2. Creative Agents

- [ ] 2.1 Create `backend/app/agents/hook_agent.py` — `HookAgent(BaseAgent[HookAgentInput, HookAgentOutput])` with Pydantic AI agent, system prompt for hook generation, `build_prompt()` including ICP summary + topic + format + goal
- [ ] 2.2 Create `backend/app/agents/narrative_agent.py` — `NarrativeAgent(BaseAgent[NarrativeAgentInput, NarrativeAgentOutput])` with Pydantic AI agent, system prompt for narrative pattern generation, `build_prompt()` including ICP + selected hook + topic + format
- [ ] 2.3 Create `backend/app/agents/retention_agent.py` — `RetentionAgent(BaseAgent[RetentionAgentInput, RetentionAgentOutput])` with Pydantic AI agent, system prompt for retention technique generation, `build_prompt()` including ICP + hook + narrative + format
- [ ] 2.4 Create `backend/app/agents/cta_agent.py` — `CTAAgent(BaseAgent[CTAAgentInput, CTAAgentOutput])` with Pydantic AI agent, system prompt for CTA generation, `build_prompt()` including ICP + hook + narrative + goal
- [ ] 2.5 Create `backend/app/agents/writer_agent.py` — `WriterAgent(BaseAgent[WriterAgentInput, WriterAgentOutput])` with Pydantic AI agent, system prompt for script generation, `build_prompt()` including all upstream selections + topic + format + raw notes
- [ ] 2.6 Verify: `uv run python -c "from app.agents.hook_agent import HookAgent; from app.agents.narrative_agent import NarrativeAgent; from app.agents.retention_agent import RetentionAgent; from app.agents.cta_agent import CTAAgent; from app.agents.writer_agent import WriterAgent; print('ok')"`

## 3. Orchestrator Extensions

- [ ] 3.1 Extend `backend/app/pipeline/orchestrator.py` — add `_build_agent_inputs()` cases for `StepType.HOOK`, `StepType.NARRATIVE`, `StepType.RETENTION`, `StepType.CTA`, `StepType.WRITER` reading `selected_option` (JSON string, needs `json.loads()`) from upstream steps. Add `_extract_icp(step_map)` helper to parse ICPProfile from ICP step's `selected_option` or `output_data`. Fetch all steps via `_get_all_steps(project_id)` and build a `step_map = {s.step_type: s}` dict. Signature changes: `_build_agent_inputs(self, project, step_type, step_map)` (add step_map param).
- [ ] 3.2 Implement `backend/app/pipeline/orchestrator.py` — add `_invalidate_downstream(project_id, from_step)` that resets all steps after `from_step` in STEP_ORDER to PENDING (clears output_data=None, selected_option=None). In `run_step()`, before running a completed step, first reset it to PENDING (since TRANSITIONS doesn't allow completed→running), then call `_invalidate_downstream()`, then proceed with normal pending→running flow. Also add `_get_all_steps(project_id)` helper.
- [ ] 3.3 Extend `backend/app/api/pipeline.py` — in PATCH step endpoint, call orchestrator's `_invalidate_downstream()` when updating `selected_option` on a completed step (use pipeline_service which delegates to orchestrator)
- [ ] 3.4 Verify: `uv run python -c "from app.pipeline.orchestrator import PipelineOrchestrator; print('ok')"`

## 4. Script Schemas & Service

- [ ] 4.1 Create `backend/app/schemas/script.py` — `ScriptVersionResponse` (id, project_id, version_number, content, format, hook_text, narrative_pattern, cta_text, created_at), `ScriptUpdateRequest` (content: str)
- [ ] 4.2 Create `backend/app/services/export_service.py` — `ExportService(db, export_dir)` with `export_txt()`, `export_md()`, `_format_as_markdown()`, `_slugify()`
- [ ] 4.3 Verify: `uv run python -c "from app.schemas.script import ScriptVersionResponse; from app.services.export_service import ExportService; print('ok')"`

## 5. API Layer

- [ ] 5.1 Create `backend/app/api/scripts.py` — `GET /api/v1/projects/{id}/scripts`, `GET /api/v1/scripts/{version_id}`, `POST /api/v1/projects/{id}/scripts/generate`, `PATCH /api/v1/scripts/{version_id}`
- [ ] 5.2 Create `backend/app/api/export.py` — `GET /api/v1/projects/{id}/export?format=txt|md`
- [ ] 5.3 Update `backend/app/api/router.py` — include scripts and export routers
- [ ] 5.4 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 6. Tests

- [ ] 6.1 Create `backend/tests/unit/test_agents.py` — prompt construction tests for all 5 creative agents: verify `build_prompt()` contains expected upstream data (ICP summary, hook text, narrative, etc.), verify `_compute_cache_key()` is deterministic
- [ ] 6.2 Create `backend/tests/unit/test_export_service.py` — test `export_txt()` creates file with raw content, test `export_md()` creates file with metadata header, test `_slugify()` sanitizes filenames
- [ ] 6.3 Verify: `uv run pytest tests/ -v` passes all tests
