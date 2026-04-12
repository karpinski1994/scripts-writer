## Why

The LLM adapter layer is complete (Phase 2), but no agent uses it yet. The app still can't generate any AI output — it only stores and retrieves projects. Phase 3 builds the first agent (ICP), the pipeline state machine, and the orchestrator that ties agents to the database. This is the inflection point where the app goes from "CRUD with settings" to "AI-powered script generation tool."

## What Changes

- Add abstract `BaseAgent(ABC, Generic[InputT, OutputT])` with cache-aware `execute()`, abstract `build_prompt()`, and `_compute_cache_key()`
- Add `ICPAgent` that generates an Ideal Customer Profile from raw notes using the LLM provider layer
- Add `PipelineState` with `StepType`/`StepStatus` enums, valid state transitions, and `DEPENDENCY_MAP` (each step's prerequisites)
- Add `PipelineOrchestrator` that runs agents, persists results to `pipeline_steps`, and validates dependencies before execution
- Add `PipelineService` as a thin service layer wrapping the orchestrator with DB session handling
- Add pipeline API endpoints: GET/POST/PATCH under `/api/v1/projects/{id}/pipeline/`
- Add ICP API endpoints: generate/get/edit/upload/approve under `/api/v1/projects/{id}/icp/`
- Add pipeline and ICP Pydantic schemas
- Modify `ProjectService.create()` to auto-create 10 `pipeline_steps` rows (icp → hook → narrative → retention → cta → writer → factcheck → readability → copyright → policy) on project creation
- Add unit tests for pipeline state, ICP agent prompt construction, and orchestrator

## Capabilities

### New Capabilities
- `pipeline-management`: Pipeline state machine, orchestrator, step execution, dependency validation, and pipeline API endpoints
- `icp-generation`: ICP agent with Pydantic AI, ICP API endpoints, ICP schemas, and agent test infrastructure

### Modified Capabilities
- `project-crud`: Project creation now auto-creates 10 pending pipeline steps; aggregated router includes pipeline and ICP routers

## Impact

- **New files**: `app/agents/base.py`, `app/agents/icp_agent.py`, `app/pipeline/state.py`, `app/pipeline/orchestrator.py`, `app/services/pipeline_service.py`, `app/schemas/pipeline.py`, `app/schemas/icp.py`, `app/api/pipeline.py`, `app/api/icp.py`, `tests/unit/test_pipeline_state.py`, `tests/unit/test_icp_agent.py`
- **Modified files**: `app/services/project_service.py` (auto-create steps), `app/api/router.py` (add pipeline + ICP routers)
- **New API surface**: 6 endpoints under `/api/v1/projects/{id}/pipeline/`, 4 endpoints under `/api/v1/projects/{id}/icp/`
- **New dependency**: `pydantic-ai` for agent construction (already in pyproject.toml)
