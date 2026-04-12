## Why

The backend is initialized (FastAPI + health endpoint + config from `phase0-backend-init`) but has no database, no data models, and no API endpoints. Phase 1 builds the entire data persistence layer and project CRUD API — the foundation that every subsequent phase (LLM adapters, agents, pipeline) depends on. Without this, no project data can be stored or retrieved.

## What Changes

- Add SQLAlchemy async engine, session factory, and `get_db` dependency
- Create 5 ORM models: `Project`, `ICPProfile`, `PipelineStep`, `ScriptVersion`, `AnalysisResult` (matching LLD schema with UUID PKs, JSON columns, CHECK constraints, indexes, CASCADE deletes)
- Set up Alembic migrations with async support
- Create Pydantic request/response schemas for project CRUD
- Implement `ProjectService` with full async CRUD operations
- Create project API router with 5 REST endpoints
- Create aggregated API router mounting all sub-routers under `/api/v1`
- Update `main.py` to mount routers and add DB initialization in lifespan
- Add test fixtures (in-memory SQLite, async client, db session)
- Add unit tests for ProjectService and integration tests for project API endpoints

## Capabilities

### New Capabilities
- `project-crud`: Database persistence layer (SQLAlchemy + SQLite), Alembic migrations, project CRUD API endpoints, Pydantic schemas, service layer, and test infrastructure

### Modified Capabilities
- `backend-foundation`: Update `main.py` to mount API router and add DB table creation in lifespan

## Impact

- **New files**: `db/database.py`, `db/models.py`, `schemas/project.py`, `services/project_service.py`, `api/projects.py`, `api/router.py`, Alembic config + initial migration
- **Modified files**: `main.py` (mount router, add lifespan DB init), `tests/conftest.py` (test fixtures)
- **New dependency**: Alembic migrations directory and config
- **API surface**: 5 new endpoints under `/api/v1/projects`
- **Database**: SQLite file created at `data/scripts_writer.db` on first run
