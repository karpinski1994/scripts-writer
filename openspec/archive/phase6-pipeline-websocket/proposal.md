## Why

Phase 5 connected the frontend to the backend — dashboard, project CRUD, settings — but the core UX is missing. Users cannot run agents, see pipeline progress, review agent output, or make selections through the browser. All pipeline interaction currently requires manual API calls. Phase 6 builds the core interactive experience: agent panels, pipeline view with real-time status, WebSocket streaming, and step-by-step navigation through the creative pipeline.

## What Changes

- Add WebSocket endpoint on backend (`/ws/pipeline/{project_id}`) with ConnectionManager that broadcasts agent events
- Integrate WebSocket broadcasting into the existing PipelineOrchestrator so agent execution emits `agent_start`, `agent_progress`, and `agent_complete` events
- Add frontend WebSocket hook (`use-websocket.ts`) with auto-reconnect and exponential backoff
- Add frontend agent stream hook (`use-agent-stream.ts`) that processes WS events into pipeline store
- Add pipeline Zustand store with streaming output tracking
- Add pipeline-view component showing horizontal step cards with status indicators
- Add step-sidebar component for non-linear navigation
- Add agent panels: ICP (review, edit, approve), Hook (select/custom), Narrative (select with recommendation), Retention (multi-select), CTA (select/customize)
- Add streaming-text component for live token rendering
- Replace project detail page with pipeline-centric view

## Capabilities

### New Capabilities
- `websocket-backend`: WebSocket endpoint, ConnectionManager, agent event broadcasting from orchestrator
- `pipeline-ui`: Pipeline view with step cards, step sidebar, status indicators, step navigation
- `agent-panels`: ICP panel, Hook panel, Narrative panel, Retention panel, CTA panel with selection flows
- `streaming-ui`: Streaming text component, pipeline store with streaming output tracking

### Modified Capabilities
- `pipeline-management`: Orchestrator now emits WebSocket events during agent execution (previously synchronous only)
- `dashboard`: Project detail page replaced with pipeline-centric view

## Impact

- **New files**: `backend/app/ws/handlers.py`, `frontend/src/stores/pipeline-store.ts`, `frontend/src/hooks/use-websocket.ts`, `frontend/src/hooks/use-agent-stream.ts`, `frontend/src/components/pipeline/pipeline-view.tsx`, `frontend/src/components/pipeline/step-sidebar.tsx`, `frontend/src/components/agents/icp-panel.tsx`, `frontend/src/components/agents/hook-panel.tsx`, `frontend/src/components/agents/narrative-panel.tsx`, `frontend/src/components/agents/retention-panel.tsx`, `frontend/src/components/agents/cta-panel.tsx`, `frontend/src/components/shared/streaming-text.tsx`, `backend/tests/unit/test_websocket.py`
- **Modified files**: `backend/app/pipeline/orchestrator.py` (add WebSocket broadcasting), `backend/app/main.py` (mount WS route), `frontend/src/app/projects/[id]/page.tsx` (replace with pipeline view)
