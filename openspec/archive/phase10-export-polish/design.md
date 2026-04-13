## Context

Phases 0–9 built the complete application: backend with all agents (creative + analysis), NotebookLM, pipeline orchestration, WebSocket, and export API. Frontend has dashboard, pipeline view, agent panels, analysis panel, script editor, and settings. The backend already has `ExportService` with `export_txt()` and `export_md()`, and an `GET /api/v1/projects/{id}/export?format=txt|md` endpoint that returns a file download.

Missing polish: no export UI in the frontend, no re-run confirmation dialog, no branch project feature, no ICP file upload UI, no error toasts, no loading skeletons, no empty states, no structured logging.

## Goals / Non-Goals

**Goals:**
- Export panel with download and clipboard copy
- Re-run confirmation with downstream invalidation warning
- Branch project (creates copy with steps up to selected step)
- ICP file upload UI (.json and .txt)
- Toast notifications for API errors
- Error boundary wrapping pipeline
- Loading skeletons for project list
- Empty states for dashboard and pipeline
- Structlog JSON logging in backend

**Non-Goals:**
- Auto-apply analysis suggestions to script (future)
- Version comparison UI (future)
- Collaborative editing (single-user app)
- Performance optimization (deferred)

## Decisions

### 1. Export panel uses existing backend export endpoint
**Choice:** The export panel calls the existing `GET /projects/{id}/export?format=txt|md` endpoint for download, and implements clipboard copy client-side by fetching the script content
**Rationale:** The backend already exports files. No new backend code needed for export. Clipboard copy reads the latest script version content.

### 2. Branch project copies all completed steps and their selections
**Choice:** `POST /api/v1/projects/{id}/branch` creates a new project with the same metadata, copies all pipeline steps up to and including the specified step, including their output_data and selected_option
**Alternative:** Only copy project metadata, not pipeline state
**Rationale:** Branching is for exploring alternatives from a decision point. You want the full context up to that point, not an empty pipeline.

### 3. Re-run confirmation uses a dialog component
**Choice:** Clicking "Re-run" on a completed step shows a dialog: "Re-running {step} will reset all downstream steps ({list}). Continue?" with Cancel and Re-run buttons
**Rationale:** Downstream invalidation is destructive. The user must explicitly confirm.

### 4. Error handling uses sonner toast (already installed)
**Choice:** Use the existing `sonner` toast library for error notifications. Add a React error boundary component wrapping the pipeline area that shows a fallback UI on render errors.
**Rationale:** Sonner is already installed (from Phase 5). Error boundary catches React rendering errors. Together they cover API errors and render errors.

### 5. Structlog configured at app startup
**Choice:** Configure `structlog` in `app/main.py` startup with JSON output to stdout. Add a `./logs/` file handler for agent execution logs.
**Rationale:** Structured logs are easier to search and filter. JSON to stdout works with Docker. File logs give persistence for debugging.

### 6. ICP upload reuses existing `POST /api/v1/projects/{id}/icp/upload` endpoint
**Choice:** The ICP panel gets a file upload input that calls the existing ICP upload endpoint
**Rationale:** The backend already has an ICP upload endpoint. Just need the frontend UI.

## Risks / Trade-offs

- **[Trade-off] Branch copies all data, not references** → Branch creates independent copies. Changes to the original don't affect the branch and vice versa. This is correct for the use case but means branching a large project duplicates data.

- **[Trade-off] No undo for re-run** → Once confirmed, downstream steps are invalidated. No undo. The confirmation dialog makes this explicit.

- **[Trade-off] Structlog adds a dependency** → But it's a widely-used, stable Python library. The benefit of structured logs outweighs the cost.
