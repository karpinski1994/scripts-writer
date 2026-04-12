## 1. Backend WebSocket Infrastructure

- [ ] 1.1 Create `backend/app/ws/handlers.py` — `ConnectionManager` class with `connect(ws, project_id)`, `disconnect(ws, project_id)`, `broadcast(project_id, message: dict)`. Internally: `_connections: dict[str, list[WebSocket]]`. `broadcast` serializes to JSON, sends to all connections for project_id, silently removes failed connections. Also define `websocket_endpoint(websocket, project_id)` async function that accepts connection, calls `manager.connect()`, loops receiving messages (or waiting for disconnect), calls `manager.disconnect()` on close/error.
- [ ] 1.2 Create `backend/app/ws/connection.py` — singleton `connection_manager = ConnectionManager()` instance.
- [ ] 1.3 Update `backend/app/main.py` — import `connection_manager` and `websocket_endpoint`, add `@app.websocket("/ws/pipeline/{project_id}")` route that uses them.
- [ ] 1.4 Verify: `uv run python -c "from app.ws.handlers import ConnectionManager, websocket_endpoint; from app.ws.connection import connection_manager; print('ok')"` 

## 2. Orchestrator WebSocket Integration

- [ ] 2.1 Update `backend/app/pipeline/orchestrator.py` — add `ws_manager: ConnectionManager | None = None` param to `__init__`. In `run_step()`, after setting status to RUNNING, broadcast `agent_start` event if ws_manager exists. After agent completes successfully, broadcast `agent_complete` event with output_data if ws_manager exists. On failure, broadcast `agent_failed` event.
- [ ] 2.2 Update `backend/app/api/pipeline.py` — in `run_step` endpoint, pass `connection_manager` from `app.ws.connection` to the orchestrator constructor.
- [ ] 2.3 Update `backend/app/services/pipeline_service.py` — accept optional `ws_manager` param and pass to orchestrator.
- [ ] 2.4 Verify: `uv run pytest tests/ -q` passes (existing tests should still work since ws_manager is optional/None by default)

## 3. Backend WebSocket Tests

- [ ] 3.1 Create `backend/tests/unit/test_websocket.py` — test ConnectionManager: connect adds connection, disconnect removes, broadcast sends to all, broadcast with no connections doesn't error, broadcast removes failed connection.
- [ ] 3.2 Verify: `uv run pytest tests/unit/test_websocket.py -v` passes

## 4. Frontend Agent Output Types

- [ ] 4.1 Create `frontend/src/types/agents.ts` — `HookSuggestion`, `HookAgentOutput`, `NarrativePattern`, `NarrativeAgentOutput`, `RetentionTechnique`, `RetentionAgentOutput`, `CTASuggestion`, `CTAAgentOutput`, `ScriptDraft`, `WriterAgentOutput`, `ICPAgentOutput` matching backend schemas from `app/schemas/agents.py` and `app/schemas/icp.py`.
- [ ] 4.2 Verify: `npm run build` passes with no type errors

## 5. Frontend Pipeline Store & WebSocket Hooks

- [ ] 5.1 Create `frontend/src/stores/pipeline-store.ts` — Zustand store with `activeStepType`, `steps`, `streamingOutput`, `isRunning`, and all actions per spec. Also add `DEPENDENCY_MAP: Record<string, string[]>` matching backend (icp: [], hook: [icp], narrative: [icp, hook], retention: [icp, narrative], cta: [icp, hook, narrative], writer: [icp, hook, narrative, retention, cta]) for frontend dependency checks. Add `isStepReady(stepType)` computed method that checks if all dependencies are completed.
- [ ] 5.2 Create `frontend/src/hooks/use-websocket.ts` — WebSocket hook with auto-reconnect (exponential backoff, max 30s), connection status, lastEvent. WS URL derived from `NEXT_PUBLIC_API_URL` replacing `http` with `ws`.
- [ ] 5.3 Create `frontend/src/hooks/use-agent-stream.ts` — uses `useWebSocket(projectId)`, processes events into pipeline store actions. On `agent_start`: set step running. On `agent_complete`: update step output, invalidate TanStack Query pipeline key.
- [ ] 5.4 Verify: `npm run build` passes

## 6. Pipeline UI Components

- [ ] 6.1 Create `frontend/src/components/pipeline/pipeline-view.tsx` — horizontal step cards in two rows (Creative: ICP→Hook→Narrative→Retention→CTA→Writer, Analysis: FactCheck→Readability→Copyright→Policy). Each card: step name, status indicator (✓/●/○/✗), clickable. Active step highlighted.
- [ ] 6.2 Create `frontend/src/components/pipeline/step-sidebar.tsx` — vertical step list with status icons, active step highlighted, locked steps grayed out with tooltip showing required dependencies.
- [ ] 6.3 Create `frontend/src/components/shared/streaming-text.tsx` — renders streaming text from pipeline store with blinking cursor when active.
- [ ] 6.4 Verify: `npm run build` passes

## 7. Agent Panels

- [ ] 7.1 Create `frontend/src/components/agents/icp-panel.tsx` — display ICP profile (demographics, psychographics, pain_points, desires, objections, language_style), edit toggle, re-run button, approve & continue button. Parse `output_data` JSON into `ICPAgentOutput`.
- [ ] 7.2 Create `frontend/src/components/agents/hook-panel.tsx` — ranked hook suggestions as radio options, custom hook text input, continue button. Parse `output_data` into `HookAgentOutput`.
- [ ] 7.3 Create `frontend/src/components/agents/narrative-panel.tsx` — pattern radio options with name, description, fit_score, recommendation badge, continue button. Parse into `NarrativeAgentOutput`.
- [ ] 7.4 Create `frontend/src/components/agents/retention-panel.tsx` — technique checkboxes (multi-select), placement info, continue button. Parse into `RetentionAgentOutput`.
- [ ] 7.5 Create `frontend/src/components/agents/cta-panel.tsx` — CTA suggestions by type, suggested wording, customize input, placement options, continue button. Parse into `CTAAgentOutput`.
- [ ] 7.6 Create `frontend/src/components/agents/agent-panel-wrapper.tsx` — wrapper component that shows the correct agent panel based on `activeStepType`, handles "Run Agent" button for pending steps, shows loading state for running steps, and shows "step not ready" for locked steps.
- [ ] 7.7 Verify: `npm run build` passes

## 8. Project Detail Page Replacement

- [ ] 8.1 Replace `frontend/src/app/projects/[id]/page.tsx` — pipeline-centric view: fetch project + pipeline data via TanStack Query, render step-sidebar on left, pipeline-view at top, agent-panel-wrapper in main area. Use `useAgentStream(id)` to process WS events. Show project name + format badge as header. Auto-set `activeStepType` to the first pending step on initial load. Back button to dashboard.
- [ ] 8.2 Verify: `npm run build` passes, `npm run lint` passes

## 9. Full Stack Verification

- [ ] 9.1 Run `uv run pytest tests/ -v` — all backend tests pass
- [ ] 9.2 Run `uv run ruff check app/` — lint clean
- [ ] 9.3 Run `npm run lint && npm run build` — frontend clean
