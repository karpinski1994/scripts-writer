## 1. Piragi Dependency & Configuration

- [ ] 1.1 Install `piragi` dependency: `uv add piragi` (verify: `uv run python -c "import piragi; print('ok')"`)
- [ ] 1.2 Create `backend/app/rag/config.py` — `STEP_CATEGORY_MAP` dict mapping StepType to category folders, `PIRAGI_PERSIST_DIR`, `PIRAGI_DEFAULT_TOP_K`, `PIRAGI_EMBEDDING_MODEL`, `PIRAGI_CHUNK_STRATEGY`
- [ ] 1.3 Verify: `uv run python -c "from app.rag.config import STEP_CATEGORY_MAP, PIRAGI_PERSIST_DIR; print('ok')"`

## 2. Piragi Manager

- [ ] 2.1 Create `backend/app/rag/__init__.py` — `PiragiManager` class with: `_ragi_cache: dict[str, Ragi]`, `get_or_create(category: str) -> Ragi`, `query(category: str, query: str, top_k: int) -> list[str]`, `add_documents(category: str, sources: list[str])`, `refresh(category: str)`, `_resolve_category_path(category: str) -> Path`
- [ ] 2.2 Use `piragi.Ragi` or `piragi.AsyncRagi` with `persist_dir=".piragi/{category}"`. Each category maps to `documents/{category}/` subfolder.
- [ ] 2.3 Implement directory creation and validation in `get_or_create()`: create category folder if missing, create `.piragi/{category}` index folder if missing.
- [ ] 2.4 Verify: `uv run python -c "from app.rag import PiragiManager; print('ok')"`

## 3. Piragi Schemas

- [ ] 3.1 Create `backend/app/schemas/piragi.py` — `DocumentSummary` (category, file_count, path), `ConnectDocumentsRequest` (document_paths), `ConnectDocumentsResponse` (project_id, document_paths, connected), `PiragiQueryRequest` (query, step_type), `PiragiQueryResponse` (query, results: list[ChunkResult]), `ChunkResult` (chunk, source, relevance)
- [ ] 3.2 Verify: `uv run python -c "from app.schemas.piragi import ConnectDocumentsRequest, PiragiQueryResponse; print('ok')"`

## 4. Piragi Service

- [ ] 4.1 Create `backend/app/services/piragi_service.py` — `PiragiService` wrapping `PiragiManager`. Methods: `connect_documents(project_id, document_paths)`, `disconnect_documents(project_id)`, `query_documents(project_id, query, step_type)`, `get_step_context(project_id, step_type)`. DB session handling, project lookup.
- [ ] 4.2 Implement `get_step_context()`: check `project.piragi_document_paths`, map step_type to category via `STEP_CATEGORY_MAP`, call `PiragiManager.query()`, join chunks with `\n\n`, return None if no paths, empty results, or error.
- [ ] 4.3 Verify: `uv run python -c "from app.services.piragi_service import PiragiService; print('ok')"`

## 5. Piragi API Endpoints

- [ ] 5.1 Create `backend/app/api/piragi.py` — `GET /projects/{id}/piragi/documents`, `POST /projects/{id}/piragi/connect`, `DELETE /projects/{id}/piragi/connect`, `POST /projects/{id}/piragi/query`. Validate project exists (404 if not).
- [ ] 5.2 Update `backend/app/api/router.py` — include piragi router
- [ ] 5.3 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 6. Database Migration

- [ ] 6.1 Create Alembic migration: `uv run alembic revision --autogenerate -m "add piragi_document_paths"` — adds `piragi_document_paths` VARCHAR(500) nullable to projects table
- [ ] 6.2 Create Alembic migration: `uv run alembic revision --autogenerate -m "drop notebooklm_notebook_id"` — drops `notebooklm_notebook_id` column from projects
- [ ] 6.3 Create Alembic migration: `uv run alembic revision --autogenerate -m "update icp_profiles source check"` — replaces 'notebooklm' with 'piragi' in CHECK constraint
- [ ] 6.4 Run migrations: `uv run alembic upgrade head`
- [ ] 6.5 Verify: `sqlite3 data/scripts_writer.db "PRAGMA table_info(projects);"` shows piragi_document_paths

## 7. AppSettings Update

- [ ] 7.1 Update `backend/app/config.py` — remove `google_cloud_project`, `google_cloud_location`, `google_application_credentials`, `notebooklm_storage_path`. Add `piragi_persist_dir`, `piragi_default_top_k`, `piragi_embedding_model`, `piragi_chunk_strategy`.
- [ ] 7.2 Verify: `uv run python -c "from app.config import AppSettings; print(AppSettings().piragi_persist_dir)"`

## 8. Agent Input Schema Updates

- [ ] 8.1 Update `backend/app/schemas/agents.py` — rename `notebooklm_context` to `piragi_context` on: `ICPAgentInput`, `HookAgentInput`, `NarrativeAgentInput`, `RetentionAgentInput`, `CTAAgentInput`, `WriterAgentInput`
- [ ] 8.2 Verify: `uv run python -c "from app.schemas.agents import HookAgentInput; print(HookAgentInput.model_fields)"`

## 9. Orchestrator Integration

- [ ] 9.1 Update `backend/app/pipeline/orchestrator.py` — replace `_resolve_notebooklm_context()` with `_resolve_rag_context()`. Update `_build_agent_inputs()` to check `project.piragi_document_paths` and call `PiragiService.get_step_context()`. Set `piragi_context` field on agent input. Error handling: log warning, set None, continue.
- [ ] 9.2 Verify: `uv run python -c "from app.pipeline.orchestrator import PipelineOrchestrator; print('ok')"`

## 10. Agent Prompt Updates

- [ ] 10.1 Update each creative agent's `build_prompt()` — add conditional section: `if inputs.piragi_context: prompt += f"\n\nRelevant reference material:\n{inputs.piragi_context}"`
- [ ] 10.2 Verify: `uv run python -c "from app.agents.hook_agent import HookAgent; print('ok')"`

## 11. Frontend Types & Store

- [ ] 11.1 Create `frontend/src/types/piragi.ts` — `DocumentSummary`, `ConnectedDocuments`, `PiragiQuery`, `PiragiQueryResult`, `ChunkResult` types matching backend schemas
- [ ] 11.2 Create `frontend/src/stores/piragi-store.ts` — Zustand store: `connectedPaths`, `stepContexts`, `isQuerying`, actions
- [ ] 11.3 Verify: `npm run build` passes

## 12. Frontend Piragi Components

- [ ] 12.1 Create `frontend/src/components/piragi/piragi-connect-panel.tsx` — document path input, connect/disconnect buttons, connected documents display, status indicator
- [ ] 12.2 Create `frontend/src/components/piragi/piragi-context-preview.tsx` — RAG context indicator, preview of context chunks, "Query for insights" button
- [ ] 12.3 Create `frontend/src/components/piragi/piragi-query-modal.tsx` — query input, step type selector, results display with source and relevance
- [ ] 12.4 Update each agent panel (ICP, Hook, Narrative, Retention, CTA) — add "RAG Context" section with include checkbox, connected files count, query button, context preview
- [ ] 12.5 Update project detail page — add Piragi connection panel at top or in settings drawer
- [ ] 12.6 Verify: `npm run build` passes

## 13. Backend Tests

- [ ] 13.1 Create `backend/tests/unit/test_piragi.py` — test PiragiManager, PiragiService, API endpoints
- [ ] 13.2 Verify: `uv run pytest tests/unit/test_piragi.py -v` passes

## 14. Full Stack Verification

- [ ] 14.1 Run `uv run pytest tests/ -v` — all backend tests pass
- [ ] 14.2 Run `uv run ruff check app/` — lint clean
- [ ] 14.3 Run `npm run lint && npm run build` — frontend clean