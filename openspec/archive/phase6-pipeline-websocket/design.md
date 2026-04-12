## Context

Phases 3–4 built the complete backend pipeline: all creative agents, orchestrator with dependency resolution and downstream invalidation, pipeline API, ICP API, scripts API, and export API. The orchestrator runs agents synchronously — `run_step()` calls `agent.execute()`, gets the result, and saves it to the DB. There is no WebSocket support yet.

Phase 5 built the frontend shell: dashboard, project CRUD, project detail page, settings page. The `backend/app/ws/` directory exists but is empty. The frontend has `api.ts`, all TypeScript types, Zustand stores for project and settings, and Shadcn/UI components.

The LLD defines WebSocket events (`agent_start`, `agent_progress`, `agent_complete`), a ConnectionManager, and frontend hooks (`use-websocket`, `use-agent-stream`) that process WS events into the pipeline store.

## Goals / Non-Goals

**Goals:**
- WebSocket endpoint on backend broadcasting pipeline events
- Orchestrator emits events during agent execution
- Frontend WebSocket hook with auto-reconnect
- Pipeline view showing all 10 steps with status indicators
- Step sidebar for navigation
- Agent panels for ICP, Hook, Narrative, Retention, CTA with selection flows
- Streaming text component for live token rendering
- Project detail page replaced with pipeline-centric view

**Non-Goals:**
- Writer agent panel (Phase 7 — script editor)
- Analysis agent panels (Phase 8)
- Run-all endpoint (deferred)
- Branch project (Phase 9)
- Tiptap rich editor (Phase 7)
- Export UI (Phase 9)

## Decisions

### 1. WebSocket endpoint uses FastAPI native WebSocket
**Choice:** Use `@app.websocket("/ws/pipeline/{project_id}")` with FastAPI's native WebSocket support and a `ConnectionManager` class tracking active connections per project_id
**Alternative:** Use Socket.IO or SSE
**Rationale:** FastAPI has built-in WebSocket support. No extra dependencies needed. SSE doesn't support bidirectional communication. Socket.IO adds unnecessary complexity for a single-user app.

### 2. Orchestrator accepts optional WebSocket manager parameter
**Choice:** `PipelineOrchestrator.__init__` takes an optional `ws_manager: ConnectionManager | None = None`. When present, `run_step()` emits events. When absent (unit tests), it runs silently.
**Alternative:** Use global singleton ConnectionManager
**Rationale:** Dependency injection makes testing easy. The orchestrator doesn't need WS — it's optional. Unit tests pass `None` and work without WS infrastructure.

### 3. Agent execution doesn't stream tokens in Phase 6
**Choice:** `agent_progress` events will NOT contain streaming tokens in Phase 6. The `agent_start` and `agent_complete` events are emitted, but real token streaming requires modifying the LLM provider layer (which uses `execute_with_failover` that returns complete responses). Token streaming is deferred.
**Alternative:** Implement token streaming now
**Rationale:** The current LLM adapter returns complete responses (no streaming). Token streaming requires significant refactoring of `ProviderFactory.execute_with_failover()` and `BaseAgent.execute()`. Deferring avoids scope creep. The `agent_progress` event type is reserved for future use but won't fire in Phase 6. The UI shows a loading state during agent execution instead.

### 4. Pipeline view replaces project detail page
**Choice:** The project detail page at `/projects/[id]` becomes the pipeline-centric view showing pipeline-view + step-sidebar + active agent panel
**Alternative:** Separate pipeline route at `/projects/[id]/pipeline`
**Rationale:** The pipeline IS the main interaction for a project. Every visit to a project is a pipeline interaction. A separate route adds unnecessary navigation depth.

### 5. Active step selection stored in pipeline Zustand store
**Choice:** `pipeline-store.ts` has `activeStepType: string | null` tracking which step's agent panel is currently shown. Clicking a step card or sidebar item sets the active step. The agent panel for the active step renders in the main content area.
**Alternative:** Use URL query parameter `?step=icp`
**Rationale:** Zustand is simpler for this. URL query params add complexity for something that's purely client-side navigation. Can add URL sync later.

### 6. Agent panels read output_data from pipeline steps and parse JSON
**Choice:** Agent panels receive the `PipelineStep` object, parse `output_data` JSON string into the appropriate schema (e.g., `HookAgentOutput`), and render the structured data. The parsing happens client-side.
**Alternative:** Add dedicated API endpoints per agent type
**Rationale:** The pipeline API already returns `output_data`. Parsing client-side avoids adding more API endpoints. The TypeScript types for agent outputs already exist or can be added to the existing types files.

### 7. Selection flow uses PATCH pipeline step endpoint
**Choice:** Each agent panel's "Continue" action calls `PATCH /api/v1/projects/{id}/pipeline/{step_id}` with `selected_option` as JSON. This triggers downstream invalidation if needed (already implemented in backend).
**Alternative:** Separate selection endpoints per agent type
**Rationale:** The pipeline PATCH endpoint already handles selection and invalidation. No new backend code needed for selections.

## Risks / Trade-offs

- **[Risk] No token streaming in Phase 6** → Mitigation: Show a loading spinner with "Agent is running..." during execution. The `agent_complete` event fires when done, instantly showing results. This is acceptable for v1.

- **[Risk] WebSocket connection management complexity** → Mitigation: Single-user app means typically 1 connection. ConnectionManager is simple: dict of project_id → set of WebSocket connections. Auto-reconnect on frontend handles disconnects.

- **[Trade-off] Parsing output_data JSON on client** → The backend stores output_data as a JSON string. The frontend must `JSON.parse()` it. This is fine for structured agent outputs but means the frontend needs to know each agent's output schema.

- **[Trade-off] No re-run confirmation in Phase 6** → Clicking "Re-run" on a completed step immediately re-runs the agent and invalidates downstream. A confirmation dialog would be nice but is deferred to Phase 9 (polish).
