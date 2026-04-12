# Scripts Writer — Development Plan & Progress Tracker

> **Purpose:** This document is the single source of truth for development progress. Any developer, agentic IDE, or AI model can read this file, see exactly what is done and what is next, and pick up work without context loss.
>
> **How to use:** Each phase has numbered steps with a `[ ]` checkbox. When a step is complete, change `[ ]` to `[x]` and fill in the completion date. Before starting any work, read this file top-to-bottom to understand current state.

---

## Current Status

| Item | Value |
|------|-------|
| **Last updated** | 2026-04-12 |
| **Current phase** | Phase 5 — Complete |
| **Backend** | Full creative pipeline (ICP → Hook → Narrative → Retention → CTA → Writer) + export |
| **Frontend** | Dashboard, project CRUD, project detail, settings page (connected to backend) |
| **Database** | Created (SQLite, 5 tables, Alembic migrations) |
| **LLM connectivity** | Provider layer built (tested via scripts, requires API keys) |
| **Working end-to-end?** | Create project in browser → see in dashboard → view detail → configure LLM providers in Settings |

---

## Reference Documents

| Doc | File | Purpose |
|-----|------|---------|
| Business Case & Charter | `docs/01-business-case-project-charter.md` | Why we're building this |
| Business Requirements | `docs/02-business-requirements-document.md` | Business objectives & personas |
| Functional Requirements | `docs/03-functional-requirements-document.md` | What the system must do |
| Software Requirements Spec | `docs/04-software-requirements-specification.md` | Formal requirements + NFRs |
| Technical Requirements | `docs/05-technical-requirements-document.md` | Architecture, tech stack, API spec |
| Technical Design | `docs/06-technical-design-document.md` | Class designs, DB schema, patterns |
| High-Level Design | `docs/07-high-level-design.md` | Data flow, integration, deployment |
| Low-Level Design | `docs/08-low-level-design-document.md` | Component details, pseudocode, tests |

---

## Tech Stack Reference

| Layer | Technology |
|-------|-----------|
| Backend runtime | Python 3.11+ |
| Backend framework | FastAPI 0.110+ |
| Agent framework | Pydantic AI |
| Validation | Pydantic 2.x |
| ORM | SQLAlchemy 2.x (async) |
| Database | SQLite via aiosqlite |
| Migrations | Alembic |
| LLM clients | `openai` (Modal/Groq), `google-generativeai` (Gemini), `ollama` |
| Frontend framework | Next.js 14+ (App Router) |
| UI components | Shadcn/UI |
| Styling | Tailwind CSS 3.x |
| State management | Zustand 4.x |
| Data fetching | TanStack Query 5.x |
| Forms | React Hook Form + Zod |
| Rich editor | Tiptap |
| Icons | Lucide React |
| Python package mgr | `uv` |
| Node package mgr | `npm` or `pnpm` |
| Python linter | `ruff` |
| JS linter | `eslint` + `prettier` |

---

## LLM Provider Configuration

| Provider | Base URL | SDK | Auth |
|----------|----------|-----|------|
| Modal (GLM-5.1) | `https://api.us-west-2.modal.direct/v1` | `openai` (OpenAI-compatible) | API key |
| Groq | `https://api.groq.com/openai/v1` | `openai` (OpenAI-compatible) | API key |
| Google Gemini | Gemini REST API | `google-generativeai` | API key |
| Ollama (local) | `http://localhost:11434` | `ollama` | None |

Provider priority (failover order): Modal → Groq → Gemini → Ollama

---

## Directory Structure

```
scripts-writer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   ├── projects.py
│   │   │   ├── pipeline.py
│   │   │   ├── icp.py
│   │   │   ├── scripts.py
│   │   │   ├── analysis.py
│   │   │   ├── export.py
│   │   │   └── settings.py
│   │   ├── schemas/
│   │   │   ├── project.py
│   │   │   ├── pipeline.py
│   │   │   ├── icp.py
│   │   │   ├── script.py
│   │   │   ├── analysis.py
│   │   │   └── settings.py
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── icp_agent.py
│   │   │   ├── hook_agent.py
│   │   │   ├── narrative_agent.py
│   │   │   ├── retention_agent.py
│   │   │   ├── cta_agent.py
│   │   │   ├── writer_agent.py
│   │   │   ├── factcheck_agent.py
│   │   │   ├── readability_agent.py
│   │   │   ├── copyright_agent.py
│   │   │   └── policy_agent.py
│   │   ├── llm/
│   │   │   ├── base.py
│   │   │   ├── modal_provider.py
│   │   │   ├── groq_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   ├── provider_factory.py
│   │   │   └── cache.py
│   │   ├── pipeline/
│   │   │   ├── orchestrator.py
│   │   │   └── state.py
│   │   ├── services/
│   │   │   ├── project_service.py
│   │   │   ├── pipeline_service.py
│   │   │   ├── export_service.py
│   │   │   └── analysis_service.py
│   │   └── ws/
│   │       └── handlers.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── scripts/
│   │   └── test_llm.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── editor/
│   │   │   │           └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── dashboard/
│   │   │   ├── pipeline/
│   │   │   ├── agents/
│   │   │   ├── editor/
│   │   │   └── shared/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── ws.ts
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   │   ├── use-pipeline.ts
│   │   │   ├── use-websocket.ts
│   │   │   └── use-agent-stream.ts
│   │   ├── stores/
│   │   │   ├── project-store.ts
│   │   │   ├── pipeline-store.ts
│   │   │   ├── editor-store.ts
│   │   │   └── settings-store.ts
│   │   └── types/
│   │       ├── project.ts
│   │       ├── pipeline.ts
│   │       ├── icp.ts
│   │       ├── script.ts
│   │       └── analysis.ts
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── scripts_writer.db
│   └── exports/
├── docs/
│   └── (all 8 design docs + this file)
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Phase 0: Project Scaffolding

**Goal:** Two runnable (but empty) servers and a working dev loop.

**Test criteria for the whole phase:** `uvicorn app.main:app` returns `/health` = `{"status":"ok"}` and `npm run dev` shows a blank page at `localhost:3000`.

### Steps

- [x] **0.1** Initialize `backend/` with `uv init`, install FastAPI + uvicorn + pydantic + pydantic-settings + sqlalchemy + aiosqlite + alembic + openai + google-generativeai + ollama + httpx + structlog + pytest + pytest-asyncio
  - **Verify:** `uv run python -c "import fastapi; print(fastapi.__version__)"` prints version
  - **Date completed:** 2026-04-11

- [x] **0.2** Create `backend/app/main.py` with FastAPI app, `/health` endpoint, CORS middleware (allow localhost:3000), lifespan that prints startup message
  - **Verify:** `uv run uvicorn app.main:app --reload` starts, `curl localhost:8000/health` returns `{"status":"ok"}`
  - **Date completed:** 2026-04-11

- [x] **0.3** Create `backend/app/config.py` with `AppSettings(BaseSettings)` class loading from `.env` (all fields from LLD doc — modal_api_key, groq_api_key, gemini_api_key, ollama_base_url, ollama_enabled, database_url, export_dir, log_level, cache_max_size, cache_ttl_seconds, max_retries, debounce_save_ms)
  - **Verify:** `uv run python -c "from app.config import AppSettings; print(AppSettings())"` prints defaults
  - **Date completed:** 2026-04-11

- [x] **0.4** Initialize `frontend/` with `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir` (App Router, TypeScript, Tailwind, ESLint)
  - **Verify:** `npm run dev` starts, blank page renders at `localhost:3000`
  - **Date completed:** 2026-04-11

- [x] **0.5** Install frontend dependencies: `@tanstack/react-query`, `zustand`, `react-hook-form`, `@hookform/resolvers`, `zod`, `react-markdown`, `lucide-react`
  - **Verify:** `npm ls @tanstack/react-query zustand` shows installed
  - **Date completed:** 2026-04-11

- [x] **0.6** Initialize Shadcn/UI: `npx shadcn@latest init` (Nova style [New York equiv], Zinc/neutral theme, CSS variables)
  - **Verify:** `npx shadcn@latest add button` works, button renders
  - **Date completed:** 2026-04-11

- [x] **0.7** Create `.env.example` at project root with all API key placeholders + database_url + export_dir
  - **Verify:** File exists with all keys documented
  - **Date completed:** 2026-04-11

- [x] **0.8** Create/update `.gitignore` with entries for: `.env`, `data/`, `logs/`, `__pycache__/`, `.next/`, `node_modules/`, `*.db`
  - **Verify:** `git status` does not show secrets or data files
  - **Date completed:** 2026-04-11

- [x] **0.9** Configure `ruff` in `backend/pyproject.toml` (line-length=120, select=["E","F","I","N","W","UP"])
  - **Verify:** `uv run ruff check app/` passes with no errors
  - **Date completed:** 2026-04-11

- [x] **0.10** Configure `eslint` + `prettier` in `frontend/`
  - **Verify:** `npm run lint` passes
  - **Date completed:** 2026-04-11

---

## Phase 1: Backend Foundation

**Goal:** Database, ORM models, full CRUD API for projects — testable via Swagger UI.

**Test criteria for the whole phase:** Full project CRUD via `/docs` Swagger UI, data persisted in SQLite.

### Steps

- [x] **1.1** Create `backend/app/db/database.py` — async SQLAlchemy engine (`create_async_engine`), `async_sessionmaker`, `get_db` dependency
  - **Verify:** `uv run python -c "from app.db.database import engine; print(engine)"` prints engine object
  - **Date completed:** 2026-04-12

- [x] **1.2** Create `backend/app/db/models.py` — SQLAlchemy ORM models for all 5 tables: `Project`, `ICPProfile`, `PipelineStep`, `ScriptVersion`, `AnalysisResult` (match LLD schema exactly — UUID PKs, JSON columns, CHECK constraints, indexes, CASCADE deletes)
  - **Verify:** Models import without error; column types match LLD
  - **Date completed:** 2026-04-12

- [x] **1.3** Initialize Alembic: `uv run alembic init app/db/migrations`, configure `alembic.ini` to use `AppSettings.database_url`, configure `env.py` for async + `Base.metadata`
  - **Verify:** `uv run alembic revision --autogenerate -m "initial"` creates migration with all 5 tables
  - **Date completed:** 2026-04-12

- [x] **1.4** Run initial migration: `uv run alembic upgrade head`
  - **Verify:** `data/scripts_writer.db` file exists; `sqlite3 data/scripts_writer.db ".tables"` shows all 5 tables
  - **Date completed:** 2026-04-12

- [x] **1.5** Create `backend/app/schemas/project.py` — `ProjectCreateRequest` (name, topic, target_format, content_goal?, raw_notes with validation), `ProjectUpdateRequest` (all optional), `ProjectResponse`, `ProjectSummaryResponse`, `ProjectDetailResponse`
  - **Verify:** `ProjectCreateRequest(name="", topic="x", target_format="VSL", raw_notes="x")` raises ValidationError on empty name
  - **Date completed:** 2026-04-12

- [x] **1.6** Create `backend/app/services/project_service.py` — `ProjectService` class with methods: `create`, `list_all`, `get_by_id`, `update`, `delete` (all async, using SQLAlchemy)
  - **Verify:** Unit test creates project, lists it, gets it, updates it, deletes it
  - **Date completed:** 2026-04-12

- [x] **1.7** Create `backend/app/api/projects.py` — FastAPI router with 5 endpoints: `POST /api/v1/projects` (201), `GET /api/v1/projects` (list with pagination), `GET /api/v1/projects/{id}`, `PATCH /api/v1/projects/{id}`, `DELETE /api/v1/projects/{id}`
  - **Verify:** `curl -X POST localhost:8000/api/v1/projects -H "Content-Type: application/json" -d '{"name":"Test","topic":"Python","target_format":"VSL","raw_notes":"test notes"}'` returns 201
  - **Date completed:** 2026-04-12

- [x] **1.8** Create `backend/app/api/router.py` — aggregate all API routers under `/api/v1` prefix
  - **Verify:** Router imports and mounts without circular imports
  - **Date completed:** 2026-04-12

- [x] **1.9** Update `backend/app/main.py` — mount `api.router`, add lifespan for DB table creation (create_all as fallback), add CORS for `localhost:3000`
  - **Verify:** `curl localhost:8000/docs` returns Swagger UI with all project endpoints visible
  - **Date completed:** 2026-04-12

- [x] **1.10** Create `backend/tests/conftest.py` — in-memory SQLite test DB, `async_client` fixture, `db_session` fixture
  - **Verify:** `uv run pytest tests/` runs (no tests yet but fixtures load)
  - **Date completed:** 2026-04-12

- [x] **1.11** Create `backend/tests/unit/test_project_service.py` — test CRUD for ProjectService
  - **Verify:** `uv run pytest tests/unit/test_project_service.py` passes with 5+ tests
  - **Date completed:** 2026-04-12

- [x] **1.12** Create `backend/tests/unit/test_project_api.py` — integration tests for project endpoints via `httpx.AsyncClient`
  - **Verify:** `uv run pytest tests/unit/test_project_api.py` passes with create/list/get/update/delete tests
  - **Date completed:** 2026-04-12

---

## Phase 2: LLM Adapter Layer

**Goal:** One working LLM provider + abstract interface + factory — testable with a script.

**Test criteria for the whole phase:** `python scripts/test_llm.py modal` returns an LLM response. Settings API shows provider status.

### Steps

- [x] **2.1** Create `backend/app/llm/base.py` — `LLMProvider` abstract class with: `provider_name: str`, `model_name: str`, `priority: int`, abstract `generate()`, abstract `stream()`, abstract `health_check()`, `get_identifier()`
  - **Verify:** Cannot instantiate `LLMProvider` directly (abstract)
  - **Date completed:** 2026-04-12

- [x] **2.2** Create `backend/app/llm/modal_provider.py` — `ModalProvider(LLMProvider)` using `openai.OpenAI(api_key, base_url="https://api.us-west-2.modal.direct/v1")`. Implement `generate()` (async via `asyncio.to_thread`), `stream()`, `health_check()`
  - **Verify:** `uv run python -c "from app.llm.modal_provider import ModalProvider; print('ok')"` imports without error
  - **Date completed:** 2026-04-12

- [x] **2.3** Create `backend/app/llm/groq_provider.py` — `GroqProvider(LLMProvider)` using `openai.OpenAI(api_key, base_url="https://api.groq.com/openai/v1")`. Same interface as Modal.
  - **Verify:** Import without error
  - **Date completed:** 2026-04-12

- [x] **2.4** Create `backend/app/llm/gemini_provider.py` — `GeminiProvider(LLMProvider)` using `google-generativeai` SDK
  - **Verify:** Import without error
  - **Date completed:** 2026-04-12

- [x] **2.5** Create `backend/app/llm/ollama_provider.py` — `OllamaProvider(LLMProvider)` using `ollama` SDK, base_url default `http://localhost:11434`
  - **Verify:** Import without error
  - **Date completed:** 2026-04-12

- [x] **2.6** Create `backend/app/llm/provider_factory.py` — `ProviderFactory` that builds providers from `AppSettings`, sorts by priority, has `get_provider()` (returns first healthy), `execute_with_failover()` (retry + failover chain per LLD)
  - **Verify:** `ProviderFactory(settings).get_provider()` returns a provider object
  - **Date completed:** 2026-04-12

- [x] **2.7** Create `backend/app/llm/cache.py` — `LLMCache` with LRU eviction (OrderedDict), TTL, `get()`/`set()` keyed by SHA256(prompt + system_prompt + model)
  - **Verify:** Unit test: set then get returns cached value; expired entry returns None
  - **Date completed:** 2026-04-12

- [x] **2.8** Create `backend/app/schemas/settings.py` — `LLMSettingsResponse`, `LLMSettingsUpdateRequest`, `LLMStatusResponse` (provider name → reachable boolean)
  - **Verify:** Schemas validate correct field types
  - **Date completed:** 2026-04-12

- [x] **2.9** Create `backend/app/api/settings.py` — `GET /api/v1/settings/llm` (masked API keys), `PATCH /api/v1/settings/llm`, `GET /api/v1/settings/llm/status` (runs health_check on each)
  - **Verify:** `curl localhost:8000/api/v1/settings/llm/status` returns provider status JSON
  - **Date completed:** 2026-04-12

- [x] **2.10** Create `backend/scripts/test_llm.py` — CLI script that takes provider name as arg, sends "Say hello in one sentence", prints response
  - **Verify:** `uv run python scripts/test_llm.py modal` prints an LLM-generated greeting
  - **Date completed:** 2026-04-12

- [x] **2.11** Create `backend/tests/unit/test_llm_providers.py` — tests with `MockLLMProvider` (controllable success/failure) for: successful generation, rate limit retry, failover, cache hit/miss
  - **Verify:** `uv run pytest tests/unit/test_llm_providers.py` passes
  - **Date completed:** 2026-04-12

---

## Phase 3: First Agent End-to-End (ICP)

**Goal:** Run the ICP agent through the API, get structured output — testable via Swagger.

**Test criteria for the whole phase:** Create project → `POST /pipeline/run/icp` → ICP profile in response → approve → step saved.

### Steps

- [x] **3.1** Create `backend/app/agents/base.py` — `BaseAgent(ABC, Generic[InputT, OutputT])` with: `name`, `step_type`, abstract `_build_agent()`, abstract `build_prompt()`, `execute()` (cache check → failover run → cache write), `_compute_cache_key()`
  - **Verify:** Cannot instantiate `BaseAgent` directly
  - **Date completed:** 2026-04-12

- [x] **3.2** Create `backend/app/agents/icp_agent.py` — `ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput])` with Pydantic AI agent, system prompt for ICP generation, `build_prompt()` including notes + topic + format + goal
  - **Verify:** `agent.build_prompt(test_input)` contains raw_notes text and topic
  - **Date completed:** 2026-04-12

- [x] **3.3** Create `backend/app/pipeline/state.py` — `StepType` enum, `StepStatus` enum, `PipelineState` with `TRANSITIONS` dict, `can_transition()`, `validate_step_ready()`, `DEPENDENCY_MAP`
  - **Verify:** `can_transition(PENDING, RUNNING) == True`; `validate_step_ready` raises `DependencyNotMetError` for Hook without ICP
  - **Date completed:** 2026-04-12

- [x] **3.4** Create `backend/app/pipeline/orchestrator.py` — `PipelineOrchestrator` with `STEP_ORDER`, `run_step()` (check deps → set RUNNING → execute agent → set COMPLETED → save), `_build_agent_inputs()` for ICP case, `_get_or_create_step()`
  - **Verify:** Unit test: `run_step(project_id, StepType.ICP)` completes and saves output_data
  - **Date completed:** 2026-04-12

- [x] **3.5** Create `backend/app/services/pipeline_service.py` — thin service wrapping orchestrator, handling DB session
  - **Verify:** Service calls orchestrator and persists results
  - **Date completed:** 2026-04-12

- [x] **3.6** Create `backend/app/schemas/pipeline.py` — `PipelineStepResponse`, `StepUpdateRequest`, `PipelineResponse`
  - **Verify:** Schemas validate correctly
  - **Date completed:** 2026-04-12

- [x] **3.7** Create `backend/app/api/pipeline.py` — `GET /api/v1/projects/{id}/pipeline`, `POST /api/v1/projects/{id}/pipeline/run/{step_type}`, `PATCH /api/v1/projects/{id}/pipeline/{step_id}`
  - **Verify:** `curl -X POST localhost:8000/api/v1/projects/{id}/pipeline/run/icp` returns ICP profile in output_data
  - **Date completed:** 2026-04-12

- [x] **3.8** Create `backend/app/schemas/icp.py` — `ICPProfileResponse`, `ICPUpdateRequest`
  - **Verify:** Schemas match LLD ICP model
  - **Date completed:** 2026-04-12

- [x] **3.9** Create `backend/app/api/icp.py` — `POST /api/v1/projects/{id}/icp/generate`, `GET /api/v1/projects/{id}/icp`, `PATCH /api/v1/projects/{id}/icp`, `POST /api/v1/projects/{id}/icp/upload`
  - **Verify:** Generate → get → edit → approve flow works in Swagger
  - **Date completed:** 2026-04-12

- [x] **3.10** On project creation, create 10 `pipeline_steps` rows (icp, hook, narrative, retention, cta, writer, factcheck, readability, copyright, policy) all with status=pending and correct step_order
  - **Verify:** After creating a project, `GET /pipeline` returns 10 pending steps
  - **Date completed:** 2026-04-12

- [x] **3.11** Create `backend/tests/unit/test_pipeline_state.py` — state transition tests, dependency validation tests
  - **Verify:** `uv run pytest tests/unit/test_pipeline_state.py` passes
  - **Date completed:** 2026-04-12

- [x] **3.12** Create `backend/tests/unit/test_icp_agent.py` — prompt construction tests
  - **Verify:** `uv run pytest tests/unit/test_icp_agent.py` passes
  - **Date completed:** 2026-04-12

---

## Phase 4: Remaining Creative Agents

**Goal:** Full creative pipeline ICP → Hook → Narrative → Retention → CTA → Writer → Export.

**Test criteria for the whole phase:** Via Swagger: create project → run ICP → approve → run Hook → select → run Narrative → select → run Retention → select → run CTA → select → run Writer → get script → export as .md.

### Steps

- [x] **4.1** Create `backend/app/agents/hook_agent.py` — 5+ ranked hook suggestions with effectiveness scores
  - **Verify:** After approving ICP, `POST /pipeline/run/hook` returns 5 hooks with rank + rationale
  - **Date completed:** 2026-04-12

- [x] **4.2** Create `backend/app/agents/narrative_agent.py` — 4+ narrative patterns with fit scores, recommendation
  - **Verify:** After selecting hook, `POST /pipeline/run/narrative` returns patterns with recommended_index
  - **Date completed:** 2026-04-12

- [x] **4.3** Create `backend/app/agents/retention_agent.py` — technique suggestions with placements
  - **Verify:** After selecting narrative, `POST /pipeline/run/retention` returns techniques with placement info
  - **Date completed:** 2026-04-12

- [x] **4.4** Create `backend/app/agents/cta_agent.py` — CTA suggestions with wording + placement options
  - **Verify:** After selecting retention, `POST /pipeline/run/cta` returns CTA suggestions
  - **Date completed:** 2026-04-12

- [x] **4.5** Extend `orchestrator._build_agent_inputs()` to assemble context for Hook, Narrative, Retention, CTA, Writer (pull from previous steps' selected_option)
  - **Verify:** Each agent receives correct upstream data in its input
  - **Date completed:** 2026-04-12

- [x] **4.6** Implement `orchestrator._invalidate_downstream()` — reset downstream steps to PENDING when a completed step is re-run
  - **Verify:** Re-running ICP resets Hook+Narrative+Retention+CTA+Writer to PENDING
  - **Date completed:** 2026-04-12

- [x] **4.7** Create `backend/app/agents/writer_agent.py` — full script generation incorporating all selections
  - **Verify:** After all selections, `POST /pipeline/run/writer` returns complete script in ScriptDraft format
  - **Date completed:** 2026-04-12

- [x] **4.8** Create `backend/app/schemas/script.py` — `ScriptVersionResponse`, `ScriptUpdateRequest`
  - **Verify:** Schemas validate correctly
  - **Date completed:** 2026-04-12

- [x] **4.9** Create `backend/app/services/export_service.py` — `export_txt()`, `export_md()`, `_format_as_markdown()`, `_slugify()`
  - **Verify:** Unit test: export creates .md file with correct format
  - **Date completed:** 2026-04-12

- [x] **4.10** Create `backend/app/api/scripts.py` — `GET /scripts`, `GET /scripts/{version_id}`, `POST /scripts/generate`, `PATCH /scripts/{version_id}`
  - **Verify:** Script generation creates a version; edit updates content
  - **Date completed:** 2026-04-12

- [x] **4.11** Create `backend/app/api/export.py` — `GET /export?format=txt|md`
  - **Verify:** `curl localhost:8000/api/v1/projects/{id}/export?format=md` downloads a .md file
  - **Date completed:** 2026-04-12

- [x] **4.12** Create `backend/tests/unit/test_agents.py` — prompt construction tests for all creative agents
  - **Verify:** `uv run pytest tests/unit/test_agents.py` passes
  - **Date completed:** 2026-04-12

---

## Phase 5: Frontend Shell

**Goal:** Next.js connects to backend — dashboard, project CRUD, settings.

**Test criteria for the whole phase:** Create a project in the browser, see it in the list, configure LLM provider in settings.

### Steps

- [x] **5.1** Create `frontend/src/lib/api.ts` — typed API client with `api.get()`, `api.post()`, `api.patch()`, `api.delete()` wrapping fetch, base URL from env `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)
  - **Verify:** `api.get('/api/v1/projects')` returns data from backend
  - **Date completed:** 2026-04-12

- [x] **5.2** Create `frontend/src/types/*.ts` — TypeScript interfaces for Project, PipelineStep, ICPProfile, ScriptVersion, AnalysisResult, LLMConfig matching backend schemas
  - **Verify:** TypeScript compiles without errors
  - **Date completed:** 2026-04-12

- [x] **5.3** Create `frontend/src/stores/project-store.ts` — Zustand store for project list + active project
  - **Verify:** Store initializes, actions work in isolation
  - **Date completed:** 2026-04-12

- [x] **5.4** Create `frontend/src/stores/settings-store.ts` — Zustand store for LLM config
  - **Verify:** Store initializes, actions work
  - **Date completed:** 2026-04-12

- [x] **5.5** Create `frontend/src/app/layout.tsx` — root layout with TanStack Query provider, sidebar navigation (Dashboard, Settings), Shadcn/UI Sidebar component
  - **Verify:** Layout renders with sidebar navigation
  - **Date completed:** 2026-04-12

- [x] **5.6** Create `frontend/src/app/page.tsx` — Dashboard: project list (cards with name, format badge, status badge, updated_at), "New Project" button, empty state
  - **Verify:** Dashboard shows projects from backend (or empty state)
  - **Date completed:** 2026-04-12

- [x] **5.7** Create `frontend/src/components/dashboard/create-project-dialog.tsx` — dialog with form (name, topic, target_format, content_goal, raw_notes) validated with Zod
  - **Verify:** Fill form → submit → project appears in dashboard list
  - **Date completed:** 2026-04-12

- [x] **5.8** Create `frontend/src/app/projects/[id]/page.tsx` — project detail: show metadata, raw notes
  - **Verify:** Click project card → navigate to detail page with data
  - **Date completed:** 2026-04-12

- [x] **5.9** Create `frontend/src/app/settings/page.tsx` — LLM provider config: API key inputs (masked), enable/disable toggles, "Test Connection" button, "Save" button
  - **Verify:** Enter Modal API key → test → green checkmark; save persists
  - **Date completed:** 2026-04-12

---

## Phase 6: Frontend Pipeline + WebSocket

**Goal:** Agent panels, pipeline view, real-time streaming — the core UX.

**Test criteria for the whole phase:** Click through ICP → Hook → Narrative → Retention → CTA in the browser with live agent output.

### Steps

- [ ] **6.1** Create `frontend/src/stores/pipeline-store.ts` — Zustand store: activeProjectId, steps, streamingOutput, isRunning, actions (setStepOutput, appendStreamingToken, clearStreaming, etc.)
  - **Verify:** Store initializes, actions update state correctly
  - **Date completed:** ___

- [ ] **6.2** Create `frontend/src/hooks/use-websocket.ts` — WebSocket hook with auto-reconnect (exponential backoff), connects to `ws://localhost:8000/ws/pipeline/{projectId}`
  - **Verify:** Hook connects to backend WebSocket endpoint
  - **Date completed:** ___

- [ ] **6.3** Create `frontend/src/hooks/use-agent-stream.ts` — processes WS events (agent_start, agent_progress, agent_complete) into pipeline store
  - **Verify:** Streaming tokens accumulate in pipeline store
  - **Date completed:** ___

- [ ] **6.4** Create `backend/app/ws/handlers.py` — WebSocket endpoint at `/ws/pipeline/{project_id}`, ConnectionManager, broadcast agent events (start, progress tokens, complete)
  - **Verify:** `websocat ws://localhost:8000/ws/pipeline/{id}` receives events when agent runs
  - **Date completed:** ___

- [ ] **6.5** Create `frontend/src/components/pipeline/pipeline-view.tsx` — horizontal step cards with status indicators (✓ completed, ● running, ○ pending, ✗ failed)
  - **Verify:** Step cards render with correct status from pipeline data
  - **Date completed:** ___

- [ ] **6.6** Create `frontend/src/components/pipeline/step-sidebar.tsx` — vertical sidebar with step list, clickable for navigation, locked steps grayed out
  - **Verify:** Sidebar renders, clicking navigates to step
  - **Date completed:** ___

- [ ] **6.7** Create `frontend/src/components/agents/icp-panel.tsx` — display ICP fields, edit toggle, approve button, re-run button
  - **Verify:** Run ICP → see profile → edit → approve → auto-navigate to Hook step
  - **Date completed:** ___

- [ ] **6.8** Create `frontend/src/components/agents/hook-panel.tsx` — ranked hook list, select one, custom hook input, edit, continue
  - **Verify:** See 5 hooks → select → continue to Narrative
  - **Date completed:** ___

- [ ] **6.9** Create `frontend/src/components/agents/narrative-panel.tsx` — pattern list with descriptions, recommendation badge, select, continue
  - **Verify:** See patterns → select → continue
  - **Date completed:** ___

- [ ] **6.10** Create `frontend/src/components/agents/retention-panel.tsx` — technique checkboxes with placements, multi-select, continue
  - **Verify:** Select 2 techniques → continue
  - **Date completed:** ___

- [ ] **6.11** Create `frontend/src/components/agents/cta-panel.tsx` — CTA type radio, suggested wording, customize input, placement radio, continue
  - **Verify:** Choose "Buy" → customize → select placement → continue
  - **Date completed:** ___

- [ ] **6.12** Create `frontend/src/components/shared/streaming-text.tsx` — renders streaming token output from pipeline store
  - **Verify:** Watch text appear token-by-token during agent execution
  - **Date completed:** ___

---

## Phase 7: Script Editor + Versioning

**Goal:** Tiptap editor, version history, debounced save.

**Test criteria for the whole phase:** Generate script, edit in rich editor, see version history, auto-saves.

### Steps

- [ ] **7.1** Create `frontend/src/stores/editor-store.ts` — Zustand store: content, versionNumber, isDirty, isSaving, setContent, markClean
  - **Verify:** Store actions work correctly
  - **Date completed:** ___

- [ ] **7.2** Install Tiptap: `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-highlight`
  - **Verify:** Basic Tiptap editor renders in a test component
  - **Date completed:** ___

- [ ] **7.3** Create `frontend/src/components/editor/script-editor.tsx` — Tiptap with toolbar (bold, italic, headings, lists, undo/redo), debounced auto-save (500ms → PATCH), word count, dirty indicator
  - **Verify:** Type text → see "Unsaved" indicator → wait 500ms → "Saved" indicator
  - **Date completed:** ___

- [ ] **7.4** Add custom Tiptap extension for structural cues: highlight `[B-ROLL]`, `[TEXT OVERLAY]`, `[PAUSE]` with distinct background color
  - **Verify:** Type `[B-ROLL]` → text highlighted in distinct color
  - **Date completed:** ___

- [ ] **7.5** Add version history dropdown to editor — switch between script versions, load content on switch
  - **Verify:** Generate script v1 → regenerate v2 → dropdown shows v1 and v2 → switching loads content
  - **Date completed:** ___

- [ ] **7.6** Integrate writer agent into pipeline view — "Generate Script" button triggers `POST /pipeline/run/writer`, streaming output appears in editor
  - **Verify:** Click generate → streaming text fills editor → complete
  - **Date completed:** ___

---

## Phase 8: Analysis Agents + UI

**Goal:** 4 analysis agents run in parallel, results in tabbed panel.

**Test criteria for the whole phase:** Generate script → "Analyze All" → 4 tabs populate with findings.

### Steps

- [ ] **8.1** Create `backend/app/agents/factcheck_agent.py` — identifies factual claims, flags unverifiable/questionable, confidence levels
  - **Verify:** `POST /analyze/factcheck` returns findings list
  - **Date completed:** ___

- [ ] **8.2** Create `backend/app/agents/readability_agent.py` — FK + GF scores, flagged complex sentences, suggestions
  - **Verify:** `POST /analyze/readability` returns scores + findings
  - **Date completed:** ___

- [ ] **8.3** Create `backend/app/agents/copyright_agent.py` — flags potential copyright/trademark issues, advisory warnings
  - **Verify:** `POST /analyze/copyright` returns findings
  - **Date completed:** ___

- [ ] **8.4** Create `backend/app/agents/policy_agent.py` — checks against YouTube/Facebook/LinkedIn policies
  - **Verify:** `POST /analyze/policy` returns platform-specific findings
  - **Date completed:** ___

- [ ] **8.5** Extend orchestrator with `run_analysis_parallel()` using `asyncio.gather` for 4 analysis agents
  - **Verify:** `POST /analyze/all` returns 4 results concurrently
  - **Date completed:** ___

- [ ] **8.6** Create `backend/app/schemas/analysis.py` — `AnalysisResultResponse`, `FindingResponse`
  - **Verify:** Schemas match LLD Finding model
  - **Date completed:** ___

- [ ] **8.7** Create `backend/app/api/analysis.py` — `POST /analyze/{agent_type}`, `POST /analyze/all`, `GET /analysis`
  - **Verify:** All analysis endpoints work in Swagger
  - **Date completed:** ___

- [ ] **8.8** Create `backend/app/services/analysis_service.py` — aggregation and persistence of analysis results
  - **Verify:** Results saved to DB and retrievable
  - **Date completed:** ___

- [ ] **8.9** Create `frontend/src/components/agents/analysis-panel.tsx` — tabbed panel (FactCheck, Readability, Copyright, Policy), findings cards with severity badges, confidence, suggestion, dismiss/apply buttons
  - **Verify:** Click "Analyze All" → 4 tabs populate with findings
  - **Date completed:** ___

---

## Phase 9: Export, Polish & Edge Cases

**Goal:** Complete feature set — export, clipboard, branching, re-run, error handling.

**Test criteria for the whole phase:** Export to file, copy to clipboard, branch project, re-run agents, graceful errors.

### Steps

- [ ] **9.1** Create export panel component — format selector (txt, md), download button, copy-to-clipboard button
  - **Verify:** Download .txt and .md; clipboard copy works
  - **Date completed:** ___

- [ ] **9.2** Add re-run functionality to pipeline sidebar — click completed step → warning about downstream invalidation → confirm → re-run agent
  - **Verify:** Re-run ICP → warning modal → confirm → new ICP generated, downstream reset
  - **Date completed:** ___

- [ ] **9.3** Add branch project — "Branch" button on pipeline view → creates copy with steps up to selected step
  - **Verify:** Branch from Narrative → new project appears in dashboard with ICP+Hook+Narrative completed
  - **Date completed:** ___

- [ ] **9.4** Add ICP file upload to frontend — file input accepting .json and .txt, parses and submits
  - **Verify:** Upload .json ICP file → parsed and displayed in ICP panel
  - **Date completed:** ___

- [ ] **9.5** Add error handling UI — toast notifications for API errors, error boundary component wrapping pipeline
  - **Verify:** Kill LLM provider → toast shows error, app doesn't crash
  - **Date completed:** ___

- [ ] **9.6** Add loading states — skeleton screens for project list, spinners for agent execution, progress indicators
  - **Verify:** Agent running → spinner + streaming text visible
  - **Date completed:** ___

- [ ] **9.7** Add empty states — "Create your first project" CTA on empty dashboard, "Run ICP to start" on empty pipeline
  - **Verify:** Fresh app shows helpful empty states
  - **Date completed:** ___

- [ ] **9.8** Configure `structlog` in backend — JSON structured logging per module, log to stdout + `./logs/` files
  - **Verify:** Run agent → `./logs/agents.log` shows JSON entry with agent name, duration, provider, status
  - **Date completed:** ___

- [ ] **9.9** Add remaining Gemini and Ollama providers (if not already done in Phase 2)
  - **Verify:** Settings page shows all 4 providers with test buttons
  - **Date completed:** ___

---

## Phase 10: Docker & Deployment

**Goal:** One-command deployment.

**Test criteria for the whole phase:** `docker-compose up` → working app at localhost:3000.

### Steps

- [ ] **10.1** Create `backend/Dockerfile` — Python 3.11 slim, install uv, copy files, install deps, expose 8000, CMD uvicorn
  - **Verify:** `docker build backend/` succeeds
  - **Date completed:** ___

- [ ] **10.2** Create `frontend/Dockerfile` — Node 20, install deps, build, expose 3000, CMD next start
  - **Verify:** `docker build frontend/` succeeds
  - **Date completed:** ___

- [ ] **10.3** Create `docker-compose.yml` — backend + frontend services, volume for `data/`, env file, health checks
  - **Verify:** `docker-compose up` starts both services, app is usable
  - **Date completed:** ___

- [ ] **10.4** Create `README.md` — setup instructions, prerequisites, quickstart (local dev + Docker), environment variables, project structure overview
  - **Verify:** Fresh clone → follow README → app runs
  - **Date completed:** ___

---

## How to Pick Up Work

1. **Read this file** (`docs/09-development-plan.md`) top to bottom
2. **Find the first unchecked `[ ]`** — that is your next step
3. **Read the referenced design docs** if you need context (linked above)
4. **Implement the step** following the description and verify criteria
5. **Mark the step complete** by changing `[ ]` to `[x]` and filling in the date
6. **Update "Current Status"** at the top of this file
7. **Run existing tests** before moving to the next step to ensure nothing is broken

### Pre-Step Checklist

Before starting any step, verify:
- [ ] All previous steps in the current phase are `[x]`
- [ ] `uv run pytest` (backend) passes
- [ ] `npm run lint && npm run build` (frontend) passes
- [ ] Both servers start without errors

### If You Get Stuck

- Re-read the relevant design doc (04–08) for the component you're building
- Check the LLD (`docs/08-low-level-design.md`) for class diagrams, API specs, and pseudocode
- Check the TRD (`docs/05-technical-requirements-document.md`) for architecture and tech stack details
- Check the SRS (`docs/04-software-requirements-specification.md`) for exact requirement IDs and acceptance criteria
