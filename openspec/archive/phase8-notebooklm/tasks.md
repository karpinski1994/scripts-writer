## 1. Dependencies & Configuration

- [ ] 1.1 Install `google-auth` dependency: `uv add google-auth` in `backend/`
- [ ] 1.2 Update `backend/app/config.py` — add `google_cloud_project: str = ""`, `google_cloud_location: str = "us"`, `google_application_credentials: str = ""` to `AppSettings`
- [ ] 1.3 Verify: `uv run python -c "from app.config import AppSettings; s = AppSettings(); print(s.google_cloud_location)"`

## 2. NotebookLM API Client

- [ ] 2.1 Create `backend/app/integrations/__init__.py` (empty)
- [ ] 2.2 Create `backend/app/integrations/notebooklm.py` — `NotebookLMClient` with `__init__(cloud_project, location, credentials_path)`, `_get_credentials()` (loads service account key), `_get_base_url()`, `list_notebooks()` → `list[NotebookSummary]`, `query_notebook(notebook_id, query)` → `str`. Uses `google.auth` for credentials, `httpx.AsyncClient` for HTTP. Raises `NotebookLMAPIError` on failures. Base URL: `https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/{location}/notebooks`
- [ ] 2.3 Create `backend/app/integrations/errors.py` — `NotebookLMAPIError(Exception)` with `status_code` and `message`
- [ ] 2.4 Verify: `uv run python -c "from app.integrations.notebooklm import NotebookLMClient; from app.integrations.errors import NotebookLMAPIError; print('ok')"`

## 3. NotebookLM Schemas & Service

- [ ] 3.1 Create `backend/app/schemas/notebooklm.py` — `NotebookSummary` (id, title), `ConnectNotebookRequest` (notebook_id), `ConnectNotebookResponse` (project_id, notebook_id, notebook_title, connected), `NotebookQueryRequest` (query), `NotebookQueryResponse` (answer)
- [ ] 3.2 Create `backend/app/services/notebooklm_service.py` — `NotebookLMService` with `__init__(db, client)`, `list_notebooks(project_id)`, `connect_notebook(project_id, notebook_id)`, `disconnect_notebook(project_id)`, `query_notebook(project_id, query)`, `get_step_context(project_id, step_type)`. `get_step_context` generates step-specific query and calls `query_notebook`. Returns `None` if no notebook connected or on API error (log warning).
- [ ] 3.3 Verify: `uv run python -c "from app.schemas.notebooklm import NotebookSummary; from app.services.notebooklm_service import NotebookLMService; print('ok')"`

## 4. Database Migration

- [ ] 4.1 Update `backend/app/db/models.py` — add `notebooklm_notebook_id: Mapped[str | None] = mapped_column(String(100), nullable=True)` to `Project` model
- [ ] 4.2 Update `backend/app/db/models.py` — change `ICPProfile.source` CHECK constraint from `('generated','uploaded')` to `('generated','uploaded','notebooklm')`
- [ ] 4.3 Create Alembic migration: `uv run alembic revision --autogenerate -m "add_notebooklm_notebook_id_to_projects"`
- [ ] 4.4 Verify: `uv run alembic upgrade head` and `uv run python -c "from app.db.models import Project; print(Project.notebooklm_notebook_id)"`

## 5. NotebookLM API Endpoints

- [ ] 5.1 Create `backend/app/api/notebooklm.py` — `GET /projects/{project_id}/notebooklm/notebooks`, `POST /projects/{project_id}/notebooklm/connect`, `DELETE /projects/{project_id}/notebooklm/connect`, `POST /projects/{project_id}/notebooklm/query`
- [ ] 5.2 Update `backend/app/api/router.py` — include notebooklm router
- [ ] 5.3 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 6. Agent Context Enrichment

- [ ] 6.1 Update `backend/app/schemas/agents.py` — add `notebooklm_context: str | None = None` to `HookAgentInput`, `NarrativeAgentInput`, `RetentionAgentInput`, `CTAAgentInput`, `WriterAgentInput`. Also update `ICPAgentInput` in `app/schemas/icp.py`.
- [ ] 6.2 Update `backend/app/pipeline/orchestrator.py` — in `_build_agent_inputs()`, check if `project.notebooklm_notebook_id` is set. If so, instantiate `NotebookLMService` and call `get_step_context(project_id, step_type)`. Include the result as `notebooklm_context` in the agent input. On error, log warning and set `notebooklm_context=None`.
- [ ] 6.3 Update each agent's `build_prompt()` — in `icp_agent.py`, `hook_agent.py`, `narrative_agent.py`, `retention_agent.py`, `cta_agent.py`, `writer_agent.py` — include `"Additional research context from NotebookLM:\n{notebooklm_context}"` in the prompt when `notebooklm_context` is not None
- [ ] 6.4 Verify: `uv run pytest tests/ -v` passes (existing tests should still pass since notebooklm_context defaults to None)

## 7. Backend Tests

- [ ] 7.1 Create `backend/tests/unit/test_notebooklm.py` — test NotebookLMClient error handling, NotebookLMService connect/disconnect/query, get_step_context query generation per step type, graceful degradation on API error
- [ ] 7.2 Verify: `uv run pytest tests/unit/test_notebooklm.py -v` passes

## 8. Frontend Types & Store

- [ ] 8.1 Create `frontend/src/types/notebooklm.ts` — `NotebookSummary`, `ConnectNotebookRequest`, `ConnectNotebookResponse`, `NotebookQueryRequest`, `NotebookQueryResponse`, `ConnectedNotebook`
- [ ] 8.2 Create `frontend/src/stores/notebooklm-store.ts` — Zustand store with `connectedNotebook`, `stepContexts`, `isQuerying`, and all actions
- [ ] 8.3 Verify: `npm run build` passes

## 9. Frontend NotebookLM UI

- [ ] 9.1 Create `frontend/src/components/shared/notebooklm-context.tsx` — collapsible section showing connected notebook, query button, context preview, include checkbox. Props: `stepType`, `projectId`. Uses `useNotebookLMStore` and `api` client.
- [ ] 9.2 Update each agent panel (`icp-panel.tsx`, `hook-panel.tsx`, `narrative-panel.tsx`, `retention-panel.tsx`, `cta-panel.tsx`) — add `<NotebookLMContext stepType="..." projectId={projectId} />` component
- [ ] 9.3 Update `frontend/src/app/projects/[id]/page.tsx` — add NotebookLM connection indicator (notebook name or "Connect NotebookLM" button), connect dialog with notebook list
- [ ] 9.4 Verify: `npm run build` passes, `npm run lint` passes

## 10. Full Stack Verification

- [ ] 10.1 Run `uv run pytest tests/ -v` — all backend tests pass
- [ ] 10.2 Run `uv run ruff check app/` — lint clean
- [ ] 10.3 Run `npm run lint && npm run build` — frontend clean
