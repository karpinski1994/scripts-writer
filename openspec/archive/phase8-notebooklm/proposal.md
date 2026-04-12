## Why

Phases 0–7 built the complete pipeline: backend agents, orchestrator, pipeline state machine, WebSocket streaming, frontend dashboard, agent panels, and script editor. But agents operate only on the user's raw notes and upstream selections. Creators often have existing research, audience data, and content stored in Google NotebookLM notebooks that could enrich every creative step. Currently there's no way to bring that knowledge into the pipeline — users must copy-paste or re-enter everything as raw notes. Phase 8 adds Google NotebookLM integration so agents can query connected notebooks for step-relevant context before generating output.

## What Changes

- Add `app/integrations/notebooklm.py` — Google Cloud Discovery Engine API client with `list_notebooks()`, `connect()`, `disconnect()`, `query()`, `get_step_context()`
- Add `app/schemas/notebooklm.py` — request/response schemas for all NotebookLM endpoints
- Add `app/services/notebooklm_service.py` — service wrapping NotebookLM client with DB session
- Add `app/api/notebooklm.py` — 4 API endpoints (list, connect, disconnect, query)
- Add `google-auth` + `httpx` dependencies for Google Cloud API authentication
- Add `notebooklm_notebook_id` column to projects table via Alembic migration
- Update `icp_profiles.source` CHECK constraint to include `'notebooklm'`
- Add `notebooklm_context: str | None = None` to all creative agent input schemas
- Update `PipelineOrchestrator._build_agent_inputs()` to resolve NotebookLM context when notebook connected
- Add `frontend/src/types/notebooklm.ts` — TypeScript types for NotebookLM
- Add `frontend/src/stores/notebooklm-store.ts` — Zustand store for connected notebook and step contexts
- Add NotebookLM context section to each creative agent panel (ICP, Hook, Narrative, Retention, CTA)
- Add NotebookLM connection UI to project detail page

## Capabilities

### New Capabilities
- `notebooklm-backend`: Google Cloud Discovery Engine API client, NotebookLM service, API endpoints, orchestrator context enrichment
- `notebooklm-frontend`: NotebookLM types, store, agent panel context sections, project connection UI
- `agent-context-enrichment`: Orchestrator queries NotebookLM before each creative step and injects context into agent prompts

### Modified Capabilities
- `pipeline-management`: Orchestrator now optionally resolves NotebookLM context and includes it in agent inputs
- `icp-generation`: ICP agent can receive NotebookLM-enriched audience research
- `creative-agents`: Hook, Narrative, Retention, CTA, Writer agents can receive NotebookLM-enriched context

## Impact

- **New files**: `app/integrations/notebooklm.py`, `app/schemas/notebooklm.py`, `app/services/notebooklm_service.py`, `app/api/notebooklm.py`, `frontend/src/types/notebooklm.ts`, `frontend/src/stores/notebooklm-store.ts`, `backend/tests/unit/test_notebooklm.py`
- **Modified files**: `app/db/models.py` (add notebooklm_notebook_id), `app/schemas/agents.py` (add notebooklm_context field to all inputs), `app/pipeline/orchestrator.py` (resolve NotebookLM context), `app/config.py` (add Google Cloud settings), `app/api/router.py` (add notebooklm router), `frontend/src/components/agents/*.tsx` (add NotebookLM context section), `frontend/src/app/projects/[id]/page.tsx` (add connection UI)
- **Database migration**: Add `notebooklm_notebook_id` column to `projects` table, update `icp_profiles.source` CHECK constraint
