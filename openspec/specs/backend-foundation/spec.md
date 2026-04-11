## Purpose

Defines the Python backend project scaffolding: package initialization, FastAPI application with health endpoint, structured configuration via pydantic-settings, CORS middleware, linter setup, and environment variable documentation.

## Requirements

### Requirement: Backend project initialization
The system SHALL have a Python backend project initialized under `backend/` using `uv` as the package manager with a `pyproject.toml` defining project metadata, dependencies, and tool configuration.

#### Scenario: Backend package installs all dependencies
- **WHEN** `uv sync` is run in the `backend/` directory
- **THEN** all Python dependencies are installed: fastapi, uvicorn, pydantic, pydantic-settings, pydantic-ai, sqlalchemy, aiosqlite, alembic, openai, google-generativeai, ollama, httpx, structlog, pytest, pytest-asyncio, ruff

#### Scenario: Backend package structure matches LLD
- **WHEN** the `backend/` directory is inspected
- **THEN** it contains `app/` package with `__init__.py`, `main.py`, and `config.py`

### Requirement: FastAPI application with health endpoint
The system SHALL provide a FastAPI application that starts via `uvicorn` and exposes a `/health` endpoint returning `{"status": "ok"}`.

#### Scenario: Health endpoint returns ok
- **WHEN** a GET request is made to `/health`
- **THEN** the response status code is 200 and the body is `{"status": "ok"}`

#### Scenario: Application starts with uvicorn
- **WHEN** `uv run uvicorn app.main:app` is executed
- **THEN** the server starts on port 8000 and responds to HTTP requests

### Requirement: CORS middleware for local development
The system SHALL configure CORS middleware to allow requests from `http://localhost:3000` for frontend development.

#### Scenario: Frontend can make cross-origin requests
- **WHEN** a request originates from `http://localhost:3000`
- **THEN** the response includes appropriate CORS headers allowing the request

### Requirement: Structured configuration via pydantic-settings
The system SHALL load all configuration from environment variables via an `AppSettings(BaseSettings)` class with sensible defaults and `.env` file support.

#### Scenario: Settings load from .env file
- **WHEN** a `.env` file exists in the backend directory with `MODAL_API_KEY=test-key`
- **THEN** `AppSettings().modal_api_key` returns `"test-key"`

#### Scenario: Settings use defaults when env vars not set
- **WHEN** no `.env` file exists and no environment variables are set
- **THEN** `AppSettings()` initializes with default values (e.g., `database_url="sqlite+aiosqlite:///./data/scripts_writer.db"`, `log_level="INFO"`)

#### Scenario: All configuration fields are present
- **WHEN** `AppSettings` is instantiated
- **THEN** it contains fields for: modal_api_key, modal_base_url, groq_api_key, gemini_api_key, ollama_base_url, ollama_enabled, database_url, export_dir, log_level, cache_max_size, cache_ttl_seconds, max_retries, debounce_save_ms

### Requirement: Environment variable documentation
The system SHALL provide a `.env.example` file at the project root documenting all required environment variables with placeholder values and comments.

#### Scenario: Env example file lists all variables
- **WHEN** `.env.example` is inspected
- **THEN** it contains entries for all `AppSettings` fields with placeholder values and descriptive comments

### Requirement: Ruff linter configuration
The system SHALL configure `ruff` as the Python linter in `pyproject.toml` with line-length=120 and rule selectors E, F, I, N, W, UP.

#### Scenario: Ruff check passes on project code
- **WHEN** `uv run ruff check app/` is executed
- **THEN** it completes with no errors for conforming code

#### Scenario: Ruff formats code consistently
- **WHEN** `uv run ruff format app/` is executed
- **THEN** code is formatted with 120-character line length
