## Context

Phase 2 built the LLM adapter layer with 4 providers, failover, cache, and settings API. The backend can now call LLMs, but no code actually does it — there are no agents, no pipeline, and no way for a user to trigger AI generation. The database already has the `pipeline_steps` and `icp_profiles` tables from Phase 1, but they're always empty because no service populates them.

The LLD defines the full agent hierarchy (`BaseAgent → ICPAgent`), the pipeline orchestrator, state machine, and all API endpoints. Phase 3 implements the ICP agent end-to-end as the first working agent in the pipeline.

## Goals / Non-Goals

**Goals:**
- Abstract `BaseAgent` that all future agents inherit from
- `ICPAgent` generating structured ICP profiles from raw notes
- `PipelineState` with step types, statuses, transitions, and dependency map
- `PipelineOrchestrator` that validates dependencies, runs agents, persists results
- Pipeline API endpoints (GET pipeline, POST run step, PATCH update step)
- ICP API endpoints (generate, get, edit, upload, approve)
- Auto-creation of 10 pipeline steps on project creation
- Unit tests for pipeline state and ICP agent

**Non-Goals:**
- Other creative agents (Hook, Narrative, Retention, CTA, Writer — Phase 4)
- Analysis agents (FactCheck, Readability, Copyright, Policy — Phase 8)
- WebSocket streaming (Phase 6)
- Frontend pipeline UI (Phase 6)
- Run-all endpoint (can add in Phase 4)

## Decisions

### 1. BaseAgent uses ABC with Generic type parameters
**Choice:** `BaseAgent(ABC, Generic[InputT, OutputT])` with abstract `build_prompt()` and concrete `execute()`
**Alternative:** Use Pydantic AI's agent class directly without our own base
**Rationale:** Our base adds cache integration, step tracking, and error handling that Pydantic AI doesn't provide. The generic parameters ensure type safety for each agent's input/output. Matches LLD exactly.

### 2. ICPAgent uses Pydantic AI for structured output
**Choice:** Build a `pydantic_ai.Agent` inside `ICPAgent._build_agent()` with `result_type=ICPAgentOutput`
**Alternative:** Use raw `ProviderFactory.execute_with_failover()` and parse the response manually
**Rationale:** Pydantic AI handles prompt templating, structured output parsing, retries on validation errors, and model configuration. Manual parsing is fragile and duplicative.

### 3. PipelineState is a module with enums and constants, not a class
**Choice:** `StepType` enum, `StepStatus` enum, `TRANSITIONS` dict, `DEPENDENCY_MAP` dict as module-level constants
**Alternative:** A `PipelineState` class with methods
**Rationale:** The state logic is simple (lookup in dicts/enums). A class adds unnecessary indirection. The orchestrator holds the actual state in the DB. Module-level constants are clear and testable. Matches LLD pattern.

### 4. Step order: ICP(0) → Hook(1) → Narrative(2) → Retention(3) → CTA(4) → Writer(5) → FactCheck(6) → Readability(7) → Copyright(8) → Policy(9)
**Choice:** Linear ordering matching the LLD pipeline flow
**Rationale:** The LLD defines exactly this order. Creative steps first (0-5), then analysis (6-9). Each step depends on the previous one completing.

### 5. Orchestrator is a class with DB session, not a standalone module
**Choice:** `PipelineOrchestrator(db: AsyncSession)` that directly queries and updates `pipeline_steps`
**Alternative:** Orchestrator calls PipelineService which calls the DB
**Rationale:** The orchestrator IS the business logic layer. Adding a service in between adds indirection with no benefit. PipelineService is a thin wrapper for the API layer. Matches LLD.

### 6. ICP approval updates `icp_profiles.approved = True` and sets `pipeline_steps.selected_option`
**Choice:** When a user approves an ICP, update the `icp_profiles` row's `approved` field and set the pipeline step's `selected_option` to the ICP data
**Rationale:** `selected_option` is what downstream steps read from. The `approved` flag on `icp_profiles` provides a human-readable approval state. Both need to be set.

### 7. Auto-create pipeline steps in ProjectService, not in the API layer
**Choice:** After creating a project in `ProjectService.create()`, also create 10 `pipeline_steps` rows
**Alternative:** Create steps on first pipeline access (lazy)
**Rationale:** Eager creation is simpler and matches the LLD ("On project creation, create 10 pipeline_steps rows"). Lazy creation would require checking/creating steps on every pipeline access.

## Risks / Trade-offs

- **[Risk] Pydantic AI version compatibility** → Mitigation: Pin version in pyproject.toml. The API is stable in v0.x but may change. Our `BaseAgent` abstracts it so agent code is isolated from SDK changes.

- **[Risk] LLM returning invalid JSON for ICP output** → Mitigation: Pydantic AI has built-in retry logic for structured output validation. If retries fail, the step is marked `failed` with the error message stored in `error_message`.

- **[Trade-off] No streaming in Phase 3** → Agent execution is request-response, not token-by-token streaming. WebSocket streaming is Phase 6. The UX will show a loading spinner during generation.

- **[Trade-off] ICP upload stores raw text, not parsed** → If the uploaded file is .txt, we store the text and parse it later. If .json, we validate it against `ICPProfile` schema. This is simpler than trying to extract structured data from free-form text.
