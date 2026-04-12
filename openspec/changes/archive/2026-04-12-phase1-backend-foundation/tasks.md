## 1. Database Layer

- [x] 1.1 Create `backend/app/db/database.py` with `create_async_engine`, `async_sessionmaker`, `get_db` dependency using `AppSettings.database_url`
- [x] 1.2 Create `backend/app/db/models.py` with `Base = DeclarativeBase`, and 5 ORM models: `Project`, `ICPProfile`, `PipelineStep`, `ScriptVersion`, `AnalysisResult` matching LLD schema (UUID String PKs, JSON text columns, CHECK constraints via `CheckConstraint`, indexes, CASCADE on foreign keys, relationships)
- [x] 1.3 Verify: `uv run python -c "from app.db.models import Project, ICPProfile, PipelineStep, ScriptVersion, AnalysisResult; print('ok')"`

## 2. Alembic Migrations

- [x] 2.1 Initialize Alembic: `uv run alembic init app/db/migrations`
- [x] 2.2 Configure `alembic.ini` to use `sqlalchemy.url` from `AppSettings.database_url`
- [x] 2.3 Configure `app/db/migrations/env.py` for async: import `Base.metadata` from models, use `run_async` pattern with `connectable = create_async_engine`
- [x] 2.4 Generate initial migration: `uv run alembic revision --autogenerate -m "initial"` and verify it contains all 5 tables
- [x] 2.5 Run migration: `uv run alembic upgrade head` and verify `data/scripts_writer.db` exists with all 5 tables

## 3. Pydantic Schemas

- [x] 3.1 Create `backend/app/schemas/project.py` with `ProjectCreateRequest` (name min 1 max 100, topic min 1 max 200, target_format enum, content_goal optional enum, raw_notes min 1 max 10000), `ProjectUpdateRequest` (all optional), `ProjectResponse`, `ProjectSummaryResponse`, `ProjectDetailResponse`
- [x] 3.2 Verify: `ProjectCreateRequest(name="", topic="x", target_format="VSL", raw_notes="x")` raises ValidationError

## 4. Service Layer

- [x] 4.1 Create `backend/app/services/project_service.py` with `ProjectService` class accepting `AsyncSession`, methods: `create`, `list_all` (skip/limit pagination), `get_by_id` (raise 404 if not found), `update`, `delete`
- [x] 4.2 Verify: Unit test creates a project, lists it, gets it, updates it, deletes it

## 5. API Layer

- [x] 5.1 Create `backend/app/api/projects.py` with 5 endpoints: `POST /api/v1/projects` (201), `GET /api/v1/projects` (list with skip/limit), `GET /api/v1/projects/{project_id}`, `PATCH /api/v1/projects/{project_id}`, `DELETE /api/v1/projects/{project_id}`
- [x] 5.2 Create `backend/app/api/router.py` aggregating all API routers under `/api/v1` prefix
- [x] 5.3 Update `backend/app/main.py`: import and mount `api.router`, add DB table creation in lifespan as fallback, keep existing health endpoint and CORS
- [x] 5.4 Verify: `curl -X POST localhost:8000/api/v1/projects -H "Content-Type: application/json" -d '{"name":"Test","topic":"Python","target_format":"VSL","raw_notes":"test notes"}'` returns 201

## 6. Tests

- [x] 6.1 Create `backend/tests/conftest.py` with in-memory SQLite async engine, `db_session` fixture (create all tables + rollback), `async_client` fixture using `httpx.AsyncClient` with `app` param
- [x] 6.2 Create `backend/tests/unit/test_project_service.py` with 5+ tests: create, list, get, update, delete
- [x] 6.3 Create `backend/tests/unit/test_project_api.py` with integration tests: create (201), list, get (200 + 404), update, delete
- [x] 6.4 Verify: `uv run pytest tests/` passes all tests
