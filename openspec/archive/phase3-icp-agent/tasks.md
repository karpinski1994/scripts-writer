## 1. Pipeline State Machine & Errors

- [ ] 1.1 Create `backend/app/pipeline/state.py` — `StepType` enum (10 values), `StepStatus` enum (4 values), `STEP_ORDER` list, `TRANSITIONS` dict (pending→running, running→completed, running→failed, failed→running), `DEPENDENCY_MAP` dict, `can_transition()` function, `validate_step_ready()` function (raises `DependencyNotMetError` if dependencies not met)
- [ ] 1.2 Create `backend/app/pipeline/errors.py` — `InvalidStateTransitionError`, `DependencyNotMetError`, `AgentExecutionError`
- [ ] 1.3 Verify: `uv run python -c "from app.pipeline.state import StepType, StepStatus, DEPENDENCY_MAP; print(len(StepType), len(StepStatus))"` prints `10 4`

## 2. Base Agent

- [ ] 2.1 Create `backend/app/agents/base.py` — `BaseAgent(ABC, Generic[InputT, OutputT])` with `name`, `step_type` properties, abstract `build_prompt(input_data) -> str`, concrete `execute(input_data, cache, factory) -> OutputT` (cache check → factory call → cache write → return), `_compute_cache_key(input_data) -> str` using SHA256
- [ ] 2.2 Verify: `uv run python -c "from app.agents.base import BaseAgent; BaseAgent()"` raises TypeError

## 3. ICP Agent

- [ ] 3.1 Create `backend/app/agents/icp_agent.py` — `ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput])` with Pydantic AI agent, system prompt for ICP generation, `build_prompt()` including notes + topic + format + goal. Import ICP input/output models from `app/schemas/icp.py`
- [ ] 3.2 Create `backend/app/schemas/icp.py` — `ICPDemographics`, `ICPPsychographics`, `ICPProfile`, `ICPAgentInput`, `ICPAgentOutput` Pydantic models matching LLD. Also `ICPProfileResponse`, `ICPUpdateRequest` API schemas
- [ ] 3.3 Verify: `uv run python -c "from app.agents.icp_agent import ICPAgent; from app.schemas.icp import ICPAgentInput; print('ok')"`

## 4. Pipeline Orchestrator

- [ ] 4.1 Create `backend/app/pipeline/orchestrator.py` — `PipelineOrchestrator(db: AsyncSession)` with `run_step(project_id, step_type)` (validate deps → set running → build inputs → execute agent → save output → set completed), `_build_agent_inputs()` for ICP case, `_get_or_create_step()`
- [ ] 4.2 Verify: `uv run python -c "from app.pipeline.orchestrator import PipelineOrchestrator; print('ok')"`

## 5. Pipeline & ICP Schemas

- [ ] 5.1 Create `backend/app/schemas/pipeline.py` — `PipelineStepResponse` (id, step_type, step_order, status, output_data, selected_option, duration_ms, error_message), `StepUpdateRequest` (selected_option dict), `PipelineResponse` (project_id, current_step, steps list)
- [ ] 5.2 Verify: schemas validate without error

## 6. Services

- [ ] 6.1 Create `backend/app/services/pipeline_service.py` — `PipelineService(db: AsyncSession)` with `get_pipeline(project_id)`, `run_step(project_id, step_type)`, `update_step(project_id, step_id, data)` wrapping orchestrator
- [ ] 6.2 Update `backend/app/services/project_service.py` — in `create()`, after creating project, also create 10 `pipeline_steps` rows with correct step_types, step_orders, and status=pending
- [ ] 6.3 Verify: `uv run python -c "from app.services.pipeline_service import PipelineService; from app.services.project_service import ProjectService; print('ok')"`

## 7. API Layer

- [ ] 7.1 Create `backend/app/api/pipeline.py` — `GET /api/v1/projects/{id}/pipeline`, `POST /api/v1/projects/{id}/pipeline/run/{step_type}`, `PATCH /api/v1/projects/{id}/pipeline/{step_id}`
- [ ] 7.2 Create `backend/app/api/icp.py` — `POST /api/v1/projects/{id}/icp/generate`, `GET /api/v1/projects/{id}/icp`, `PATCH /api/v1/projects/{id}/icp`, `POST /api/v1/projects/{id}/icp/upload`
- [ ] 7.3 Update `backend/app/api/router.py` — include pipeline and ICP routers
- [ ] 7.4 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 8. Tests

- [ ] 8.1 Create `backend/tests/unit/test_pipeline_state.py` — test state transitions (valid + invalid), dependency validation (met + unmet), step order
- [ ] 8.2 Create `backend/tests/unit/test_icp_agent.py` — test `build_prompt()` contains notes and topic, test `_compute_cache_key()` is deterministic
- [ ] 8.3 Update `backend/tests/unit/test_project_api.py` — verify project creation returns 201 and creates 10 pipeline steps (GET /pipeline returns 10 steps)
- [ ] 8.4 Verify: `uv run pytest tests/ -v` passes all tests
