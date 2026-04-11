## Context

Scripts Writer is a new project with no existing backend code. The `backend/` directory does not exist yet. This change creates the entire Python backend foundation from scratch, following the architecture defined in `docs/05-technical-requirements-document.md` through `docs/08-low-level-design.md`.

The project uses a **modular monolith** architecture with FastAPI as the web framework, Pydantic AI for agent definitions, SQLAlchemy async for persistence, and multiple LLM provider adapters. All infrastructure decisions are already documented in the design docs — this change implements the scaffolding that all future phases depend on.

Key constraints:
- Must use `uv` for Python package management (not pip/poetry)
- Must support macOS as primary platform
- Must be runnable locally with no paid services
- Must follow the directory structure defined in `docs/09-development-plan.md`

## Goals / Non-Goals

**Goals:**
- Initialize a working Python backend that starts via `uvicorn` and responds to `/health`
- Install all dependencies needed for Phases 1–4 (FastAPI, Pydantic AI, SQLAlchemy, LLM SDKs, etc.)
- Provide structured configuration via `pydantic-settings` loading from `.env`
- Configure `ruff` linter for code quality
- Create `.env.example` documenting all required environment variables

**Non-Goals:**
- Database models or migrations (Phase 1)
- LLM provider implementations (Phase 2)
- Agent implementations (Phase 3)
- Frontend initialization (Phase 0 steps 0.4–0.10)
- Docker setup (Phase 10)

## Decisions

### 1. Package manager: `uv`
**Choice:** Use `uv` for all Python dependency management.
**Alternative:** pip + venv, Poetry, Pipenv
**Rationale:** `uv` is extremely fast (Rust-based), supports `pyproject.toml` natively, handles virtual environments automatically, and is the emerging standard. The dev plan specifies `uv` explicitly.

### 2. App structure: Flat module under `backend/app/`
**Choice:** Single `app/` package with sub-packages (`api/`, `agents/`, `llm/`, `pipeline/`, `services/`, `schemas/`, `db/`, `ws/`) following the LLD directory structure.
**Alternative:** Multi-package monorepo, src-layout (`src/app/`)
**Rationale:** Matches the LLD exactly. Flat structure is simpler for a single-developer project. No need for src-layout since the project won't be published as a library.

### 3. Configuration: `pydantic-settings` with `.env`
**Choice:** All configuration loaded via `AppSettings(BaseSettings)` from `.env` file with documented defaults.
**Alternative:** Config files (YAML/TOML), environment-only (no .env file)
**Rationale:** `pydantic-settings` provides type validation, default values, and `.env` file support out of the box. Matches the LLD `AppSettings` model exactly. `.env` file is standard for local development and Docker deployment.

### 4. CORS: Allow localhost:3000 for frontend dev
**Choice:** Add CORS middleware allowing `http://localhost:3000` origins.
**Alternative:** No CORS (frontend and backend on same port via proxy), wildcard `*`
**Rationale:** During development, frontend runs on :3000 and backend on :8000. CORS is required for browser requests. Using specific origin (not wildcard) is more secure even for local dev.

### 5. Linter: `ruff` with extended rule set
**Choice:** Configure `ruff` with line-length=120 and rules: E, F, I, N, W, UP.
**Alternative:** flake8 + black + isort (separate tools), minimal ruff config
**Rationale:** `ruff` replaces flake8, black, and isort in a single fast tool. Extended rule set catches common issues without being oppressive. 120 char line length accommodates Python's verbose nature.

### 6. Dependency pinning strategy
**Choice:** Use `>=` version specifiers for major versions (e.g., `fastapi>=0.110`) rather than exact pins.
**Alternative:** Exact pins (`fastapi==0.110.0`), `^` caret ranges
**Rationale:** For active development, `>=` allows compatible updates without manual intervention. Exact pins are better for production deployment but premature at scaffolding phase. `uv.lock` provides reproducibility.

## Risks / Trade-offs

- **[Risk] Pydantic AI maturity** → Pydantic AI is relatively new and APIs may change. Mitigation: Pin to specific minor version once first working agent is built (Phase 3). Agent interface is abstracted behind `BaseAgent` so implementation changes are contained.

- **[Risk] `uv` availability** → `uv` must be installed on the developer's machine. Mitigation: Document installation in `.env.example` and eventual `README.md`. `uv` is widely available via Homebrew, pip, and standalone installer.

- **[Trade-off] `>=` version specifiers** → Could lead to unexpected breakage from dependency updates. Mitigation: `uv.lock` provides deterministic installs. CI will catch issues. Pin exact versions if breakage occurs.

- **[Trade-off] SQLite for persistence** → Limited concurrent write support. Mitigation: Single-user local tool — concurrent writes are not a concern for v1. Migration path to PostgreSQL is documented in HLD.
