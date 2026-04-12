## Context

The backend scaffolding is complete from `phase0-backend-init`: FastAPI app with `/health`, `AppSettings` config, all Python dependencies installed, and ruff configured. However, there is no database, no ORM models, no API endpoints beyond `/health`, and no test infrastructure.

The LLD (`docs/08-low-level-design.md`) defines the complete database schema (5 tables with UUID PKs, JSON columns, CHECK constraints) and the full API specification (5 project CRUD endpoints). The TRD (`docs/05-technical-requirements-document.md`) specifies SQLite + SQLAlchemy async + Alembic for the persistence layer.

This change builds the entire data layer and project CRUD API, enabling Phase 2 (LLM adapters) and Phase 3 (agents) to persist and retrieve data.

## Goals / Non-Goals

**Goals:**
- Fully functional SQLite database with all 5 tables managed via Alembic migrations
- Complete project CRUD API testable via Swagger UI at `/docs`
- Pydantic schemas with validation for all project endpoints
- Async SQLAlchemy service layer with proper session management
- Test infrastructure (in-memory SQLite, async client fixtures)
- Unit and integration tests for project CRUD

**Non-Goals:**
- ICP, pipeline, script, or analysis endpoints (Phases 3–4)
- LLM provider integration (Phase 2)
- Frontend (Phases 5–6)
- WebSocket support (Phase 6)
- Alembic migrations beyond the initial schema

## Decisions

### 1. SQLite with JSON columns stored as TEXT
**Choice:** Store JSON data (ICP demographics, pipeline step input/output, analysis findings) as TEXT columns in SQLite since SQLite doesn't have native JSONB. Use Pydantic's `model_dump()` / `model_validate()` for serialization/deserialization at the service layer.
**Alternative:** Use SQLAlchemy's `TypeDecorator` for JSON columns with automatic serialization
**Rationale:** SQLite handles JSON as TEXT natively. A custom `TypeDecorator` adds complexity for marginal benefit. Pydantic already handles serialization at the schema level. If we migrate to PostgreSQL later, we switch to native JSONB columns.

### 2. UUID primary keys stored as strings in SQLite
**Choice:** Store UUIDs as `String(36)` in SQLite since SQLite has no native UUID type. Generate UUIDs in Python via `uuid4()`.
**Alternative:** Use integer auto-increment PKs, use a SQLAlchemy UUID type decorator
**Rationale:** UUIDs are required by the LLD for global uniqueness and future distributed scenarios. String storage is straightforward and works across SQLite and PostgreSQL. The LLD explicitly requires UUID PKs.

### 3. Service layer between API routers and database
**Choice:** Create a `ProjectService` class that encapsulates all database operations. API routers call service methods, not ORM directly.
**Alternative:** Direct ORM access in routers, repository pattern with interfaces
**Rationale:** Service layer keeps routers thin, centralizes business logic, and is easy to test by mocking the service. Full repository pattern (with interfaces) is overkill for v1 single-user app.

### 4. Alembic for migrations with async engine
**Choice:** Use Alembic with async SQLAlchemy engine, configured in `env.py` using `run_async` pattern.
**Alternative:** Manual SQL scripts, no migrations
**Rationale:** Alembic is the standard migration tool for SQLAlchemy. Async support is required since the app uses an async engine. Manual scripts don't track schema versions.

### 5. Test with in-memory SQLite
**Choice:** Tests use `sqlite+aiosqlite:///:memory:` with per-test table creation and rollback.
**Alternative:** Test against the file-based database, use testcontainers
**Rationale:** In-memory SQLite is fast, isolated per test, and requires no cleanup. No Docker or file management needed. The async SQLAlchemy engine works identically with in-memory and file-based SQLite.

## Risks / Trade-offs

- **[Risk] SQLite CHECK constraints are parsed but not enforced in older versions** → Mitigation: SQLite 3.25+ enforces CHECK constraints. The Python 3.11+ runtime bundles SQLite 3.39+. Pydantic validation provides defense-in-depth at the API layer.

- **[Risk] JSON column queries are limited in SQLite** → Mitigation: No JSON-path queries needed for v1. All JSON data is read/written as whole documents. If we need JSON queries later, PostgreSQL migration handles this natively.

- **[Trade-off] No repository interfaces** → Harder to swap database layer later. Mitigation: Service layer provides sufficient abstraction. Adding repository interfaces is straightforward if needed.

- **[Trade-off] Storing UUIDs as strings** → Slightly larger index size vs native UUID in PostgreSQL. Mitigation: Negligible for single-user local app. Migration to PostgreSQL uses native UUID type.
