## 1. Branch Project Backend

- [ ] 1.1 Create `backend/app/api/projects.py` — add `POST /projects/{id}/branch` endpoint accepting `{branch_from_step: str, name: str}`. It creates a new project with same metadata (topic, format, goal, raw_notes), copies all pipeline steps up to and including `branch_from_step` with output_data and selected_option, and creates pending steps for the rest. Returns the new project.
- [ ] 1.2 Update `backend/app/services/project_service.py` — add `branch_project(project_id, branch_from_step, name)` method implementing the copy logic.
- [ ] 1.3 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 2. Structlog Logging

- [ ] 2.1 Install structlog: `uv add structlog` in backend/
- [ ] 2.2 Create `backend/app/logging_config.py` — configure structlog with JSON renderer to stdout, file handler to `./logs/app.log` (10MB max, 5 backups), console renderer in dev. Provide `setup_logging()` function called from main.py.
- [ ] 2.3 Update `backend/app/main.py` — call `setup_logging()` at startup
- [ ] 2.4 Update `backend/app/pipeline/orchestrator.py` — add structlog logging for agent execution: log agent_name, step_type, project_id, duration_ms, provider, status on each run_step completion/failure
- [ ] 2.5 Verify: `uv run python -c "import structlog; from app.logging_config import setup_logging; print('ok')"`

## 3. Export Panel Frontend

- [ ] 3.1 Create `frontend/src/components/shared/export-panel.tsx` — format selector (txt, md), download button (calls GET /export), copy-to-clipboard button. Show only when a script version exists.
- [ ] 3.2 Integrate export panel into project detail page — add below pipeline view when Writer step is completed
- [ ] 3.3 Verify: `npm run build` passes

## 4. Re-run Confirmation Dialog

- [ ] 4.1 Update `frontend/src/components/agents/agent-panel-wrapper.tsx` — when "Re-run" is clicked on a completed step, show a dialog with downstream step names and warning message. Only confirm triggers the re-run API call.
- [ ] 4.2 Verify: Click Re-run on ICP → dialog shows downstream steps → confirm → agent re-runs

## 5. Branch Project Frontend

- [ ] 5.1 Create `frontend/src/components/shared/branch-dialog.tsx` — dialog with project name input and step selector dropdown, calls POST /branch, shows success toast, navigates to new project or refreshes dashboard
- [ ] 5.2 Add "Branch" button to project detail page header
- [ ] 5.3 Verify: Branch from Narrative → new project appears in dashboard with ICP+Hook+Narrative completed

## 6. ICP Upload UI

- [ ] 6.1 Update `frontend/src/components/agents/icp-panel.tsx` — add "Upload ICP" button with file input accepting .json and .txt, calls POST /icp/upload with file content
- [ ] 6.2 Verify: Upload .json → ICP profile updated in panel

## 7. Error Handling & Polish

- [ ] 7.1 Update `frontend/src/lib/api.ts` — add toast.error() on non-2xx responses and network errors using sonner
- [ ] 7.2 Create `frontend/src/components/shared/error-boundary.tsx` — React error boundary with fallback UI ("Something went wrong" + Reload button)
- [ ] 7.3 Update `frontend/src/app/projects/[id]/page.tsx` — wrap pipeline area with ErrorBoundary
- [ ] 7.4 Add loading skeletons to `frontend/src/app/page.tsx` (dashboard) — skeleton cards while fetching projects
- [ ] 7.5 Add empty states to dashboard and pipeline — "Create your first script" on empty dashboard, "Run ICP Agent to get started" on empty pipeline
- [ ] 7.6 Verify: `npm run build` passes, `npm run lint` passes

## 8. Full Stack Verification

- [ ] 8.1 Run `uv run pytest tests/ -v` — all backend tests pass
- [ ] 8.2 Run `uv run ruff check app/` — lint clean
- [ ] 8.3 Run `npm run lint && npm run build` — frontend clean
