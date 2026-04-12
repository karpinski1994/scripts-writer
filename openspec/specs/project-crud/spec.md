# project-crud Specification

## Purpose

Defines the async SQLAlchemy database engine and sessions, five ORM models with Alembic migrations, Pydantic project schemas, the ProjectService CRUD layer, five REST endpoints under /api/v1/projects, the aggregated API router, and in-memory SQLite test infrastructure.
## Requirements
### Requirement: Async SQLAlchemy database engine and sessions
The system SHALL provide an async SQLAlchemy engine configured via `AppSettings.database_url` with an `async_sessionmaker` and a `get_db` FastAPI dependency that yields async database sessions.

#### Scenario: Database engine creates connection
- **WHEN** the application starts
- **THEN** an async SQLAlchemy engine is created using `AppSettings.database_url`

#### Scenario: Get DB dependency yields session
- **WHEN** a FastAPI endpoint has `db: AsyncSession = Depends(get_db)` parameter
- **THEN** an async database session is provided and closed after the request

### Requirement: SQLAlchemy ORM models for all 5 tables
The system SHALL define ORM models for `Project`, `ICPProfile`, `PipelineStep`, `ScriptVersion`, and `AnalysisResult` matching the LLD schema with UUID string primary keys, JSON text columns, CHECK constraints, indexes, and CASCADE deletes.

#### Scenario: All 5 models are defined
- **WHEN** the `app.db.models` module is imported
- **THEN** `Project`, `ICPProfile`, `PipelineStep`, `ScriptVersion`, and `AnalysisResult` classes exist with correct column types and relationships

#### Scenario: Project model has required fields
- **WHEN** the `Project` model is inspected
- **THEN** it has columns: id (String PK), name, topic, target_format, content_goal, raw_notes, status, current_step, created_at, updated_at with appropriate types and constraints

### Requirement: Alembic migrations with async support
The system SHALL use Alembic for database schema migrations with async engine support, configured to read `AppSettings.database_url` and autogenerate migrations from ORM models.

#### Scenario: Initial migration creates all tables
- **WHEN** `alembic upgrade head` is executed
- **THEN** all 5 tables (projects, icp_profiles, pipeline_steps, script_versions, analysis_results) are created in the SQLite database

### Requirement: Pydantic project schemas with validation
The system SHALL define Pydantic schemas for project CRUD: `ProjectCreateRequest` with required fields and validation, `ProjectUpdateRequest` with all optional fields, `ProjectResponse`, `ProjectSummaryResponse`, and `ProjectDetailResponse`.

#### Scenario: Create request validates required fields
- **WHEN** `ProjectCreateRequest(name="", topic="x", target_format="VSL", raw_notes="x")` is validated
- **THEN** a ValidationError is raised for empty name

#### Scenario: Create request validates target_format enum
- **WHEN** `ProjectCreateRequest(name="x", topic="x", target_format="INVALID", raw_notes="x")` is validated
- **THEN** a ValidationError is raised for invalid target_format

### Requirement: ProjectService with async CRUD operations
The system SHALL provide a `ProjectService` class with async methods: `create`, `list_all`, `get_by_id`, `update`, and `delete` that encapsulate all database operations for projects.

#### Scenario: Create and retrieve project
- **WHEN** `ProjectService.create(data)` is called with valid data and then `ProjectService.get_by_id(id)` is called
- **THEN** the returned project matches the created data

#### Scenario: Delete project cascades to related data
- **WHEN** a project with associated ICP, pipeline steps, script versions, and analysis results is deleted
- **THEN** all related records are also deleted

### Requirement: Project CRUD API endpoints
The system SHALL expose 5 REST endpoints under `/api/v1/projects`: POST (create, 201), GET (list with pagination), GET by ID, PATCH (update), DELETE.

#### Scenario: Create project returns 201
- **WHEN** a POST request with valid project data is sent to `/api/v1/projects`
- **THEN** the response status is 201 and the body contains the created project with an assigned UUID

#### Scenario: List projects with pagination
- **WHEN** a GET request is sent to `/api/v1/projects?skip=0&limit=10`
- **THEN** the response contains a list of project summaries with pagination

#### Scenario: Get non-existent project returns 404
- **WHEN** a GET request is sent to `/api/v1/projects/{nonexistent-uuid}`
- **THEN** the response status is 404

### Requirement: Aggregated API router
The system SHALL provide an aggregated router that mounts all API sub-routers under the `/api/v1` prefix, including the project router and the settings router.

#### Scenario: All project endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** all project endpoints are accessible at `/api/v1/projects`

#### Scenario: Settings endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** all settings endpoints are accessible at `/api/v1/settings/llm`

### Requirement: Test infrastructure with in-memory SQLite
The system SHALL provide test fixtures in `conftest.py` including: in-memory SQLite async engine, `db_session` fixture with per-test table creation and rollback, and `async_client` fixture using `httpx.AsyncClient`.

#### Scenario: Test fixtures provide working database
- **WHEN** a test uses the `db_session` fixture
- **THEN** the session connects to an in-memory SQLite database with all tables created

### Requirement: Unit and integration tests for project CRUD
The system SHALL include unit tests for `ProjectService` and integration tests for project API endpoints covering create, list, get, update, and delete operations.

#### Scenario: Unit tests pass for ProjectService
- **WHEN** `pytest tests/unit/test_project_service.py` is executed
- **THEN** all tests pass with 5+ test cases

#### Scenario: Integration tests pass for project API
- **WHEN** `pytest tests/unit/test_project_api.py` is executed
- **THEN** all tests pass with create/list/get/update/delete test cases

