## Purpose

Updates to the existing backend-foundation capability to support API router mounting and database initialization in the application lifespan.

## MODIFIED Requirements

### Requirement: FastAPI application with health endpoint
The system SHALL provide a FastAPI application that starts via `uvicorn`, exposes a `/health` endpoint returning `{"status": "ok"}`, mounts the aggregated API router at `/api/v1`, and initializes database tables in the lifespan context manager as a fallback when Alembic has not been run.

#### Scenario: Health endpoint returns ok
- **WHEN** a GET request is made to `/health`
- **THEN** the response status code is 200 and the body is `{"status": "ok"}`

#### Scenario: API router mounted at /api/v1
- **WHEN** the application starts
- **THEN** all endpoints under `/api/v1/projects` are accessible

#### Scenario: Database tables created on startup as fallback
- **WHEN** the application starts and no database file exists
- **THEN** all ORM model tables are created automatically as a fallback (Alembic is the primary migration tool)
