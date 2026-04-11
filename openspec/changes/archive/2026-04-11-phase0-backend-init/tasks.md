## 1. Project Initialization

- [x] 1.1 Create `backend/` directory and initialize with `uv init --name scripts-writer-backend`
- [x] 1.2 Update `backend/pyproject.toml` with project metadata (name, version, requires-python=">=3.11")
- [x] 1.3 Install all dependencies via `uv add`: fastapi, uvicorn[standard], pydantic, pydantic-settings, pydantic-ai, sqlalchemy[asyncio], aiosqlite, alembic, openai, google-generativeai, ollama, httpx, structlog, pytest, pytest-asyncio
- [x] 1.4 Add `ruff` as dev dependency via `uv add --dev ruff`
- [x] 1.5 Configure `ruff` in `pyproject.toml` under `[tool.ruff]`: line-length=120, select=["E","F","I","N","W","UP"]
- [x] 1.6 Verify: `uv run python -c "import fastapi; print(fastapi.__version__)"` prints a version number

## 2. App Package Structure

- [x] 2.1 Create `backend/app/__init__.py` (empty)
- [x] 2.2 Create empty `__init__.py` files for sub-packages: `app/api/`, `app/agents/`, `app/llm/`, `app/pipeline/`, `app/services/`, `app/schemas/`, `app/db/`, `app/ws/`
- [x] 2.3 Create empty directories: `backend/tests/`, `backend/tests/unit/`, `backend/tests/integration/`
- [x] 2.4 Create `backend/tests/conftest.py` (empty placeholder)
- [x] 2.5 Create `backend/scripts/` directory

## 3. Configuration Module

- [x] 3.1 Create `backend/app/config.py` with `AppSettings(BaseSettings)` class containing all fields: modal_api_key, modal_base_url (default "https://api.us-west-2.modal.direct/v1"), groq_api_key, gemini_api_key, ollama_base_url (default "http://localhost:11434"), ollama_enabled (default False), database_url (default "sqlite+aiosqlite:///./data/scripts_writer.db"), export_dir (default "./data/exports"), log_level (default "INFO"), cache_max_size (default 128), cache_ttl_seconds (default 3600), max_retries (default 3), debounce_save_ms (default 500)
- [x] 3.2 Configure `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")` on `AppSettings`
- [x] 3.3 Verify: `uv run python -c "from app.config import AppSettings; s=AppSettings(); print(s.database_url)"` prints the default database URL

## 4. FastAPI Application

- [x] 4.1 Create `backend/app/main.py` with FastAPI app instance, lifespan context manager that logs startup message, and `/health` GET endpoint returning `{"status": "ok"}`
- [x] 4.2 Add CORSMiddleware to app allowing `http://localhost:3000` origin with all methods and headers
- [x] 4.3 Verify: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` starts and `curl http://localhost:8000/health` returns `{"status":"ok"}`

## 5. Environment & Linting

- [x] 5.1 Create `.env.example` at project root with all AppSettings fields documented with placeholder values and comments
- [x] 5.2 Verify: `uv run ruff check app/` passes with no errors
- [x] 5.3 Verify: `uv run ruff format --check app/` passes (no formatting needed)
