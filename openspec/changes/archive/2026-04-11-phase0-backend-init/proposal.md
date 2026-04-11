## Why

Phase 0 (Step 0.1) of the development plan requires initializing the Python backend project with all core dependencies. This is the foundational step — nothing else can be built until the backend package structure, dependency management, and configuration are in place. The backend must be runnable with `uvicorn` and respond to a `/health` endpoint before any agent, pipeline, or frontend work begins.

## What Changes

- Initialize `backend/` directory with `uv` package manager and `pyproject.toml`
- Install all Python dependencies: FastAPI, uvicorn, Pydantic 2.x, pydantic-settings, Pydantic AI, SQLAlchemy 2.x (async), aiosqlite, Alembic, openai SDK, google-generativeai SDK, ollama SDK, httpx, structlog, pytest, pytest-asyncio, ruff
- Create `backend/app/__init__.py` and minimal package structure
- Create `backend/app/config.py` with `AppSettings(BaseSettings)` loading all configuration from `.env` (API keys, database URL, export dir, cache settings, retry settings)
- Create `backend/app/main.py` with FastAPI app instance, `/health` endpoint, CORS middleware, and startup lifespan
- Create `.env.example` at project root with all environment variable placeholders documented
- Configure `ruff` linter in `pyproject.toml`

## Capabilities

### New Capabilities
- `backend-foundation`: Python backend package structure, dependency management via uv, FastAPI application with health endpoint, pydantic-settings configuration, and linter setup

### Modified Capabilities
<!-- No existing capabilities to modify — this is the first change -->

## Impact

- **New directory**: `backend/` with full Python package structure
- **New files**: `pyproject.toml`, `app/main.py`, `app/config.py`, `.env.example`
- **Dependencies**: 15+ Python packages installed via uv
- **Development workflow**: Backend can now be started with `uv run uvicorn app.main:app --reload`
- **No breaking changes**: This is the initial setup
