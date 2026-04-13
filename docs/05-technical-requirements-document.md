# Technical Requirements Document – Scripts Writer

## System Architecture

### Pattern: Modular Monolith with Agent-Based Pipeline

Scripts Writer uses a **modular monolith** architecture. The backend is a single FastAPI application with clearly separated agent modules, each following Pydantic AI patterns. A monolith is chosen over microservices for the following reasons:

| Factor | Rationale |
|--------|-----------|
| **Single user** | No need for independent scaling of services |
| **Zero budget** | No infrastructure for service mesh, API gateways, or container orchestration |
| **Solo developer** | One deployment unit reduces operational complexity |
| **Local-first** | Single process on a single machine; microservices add unnecessary network overhead |
| **Agent modularity** | Each agent is an independent Python module with well-defined Pydantic I/O — future extraction to microservices is trivial if needed |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ │
│  │Dashboard │ │Pipeline  │ │Agent     │ │Script    │ │Analysis   │ │
│  │          │ │View      │ │Output    │ │Editor    │ │Panel      │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────────┘ │
│              Shadcn/UI + Tailwind CSS + React                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP REST + WebSocket
┌───────────────────────────▼─────────────────────────────────────────┐
│                       FastAPI Backend                                │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    API Layer (FastAPI Routers)               │    │
│  │  /projects  /pipeline  /agents  /export  /settings          │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │                 Pipeline Orchestrator                         │    │
│  │  Sequential agent execution · State management · Branching   │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │ICP     │ │Hook    │ │Narrative│ │Retention│ │CTA     │           │
│  │Agent   │ │Agent   │ │Agent   │ │Agent    │ │Agent   │           │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘           │
│      └──────────┴──────────┴──────────┴──────────┘                │
│                         │                                           │
│  ┌──────────────────────▼──────────────────────┐                   │
│  │            Writer Agent                      │                   │
│  └──────────────────────┬──────────────────────┘                   │
│                         │                                           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                      │
│  │Fact    │ │Read    │ │Copyright│ │Policy  │                      │
│  │Check   │ │ability │ │Agent   │ │Agent   │                      │
│  └────────┘ └────────┘ └────────┘ └────────┘                      │
│                         │                                           │
│  ┌──────────────────────▼──────────────────────┐                   │
│  │           LLM Adapter Layer                  │                   │
│  │  Modal │ Groq │ Gemini │ Ollama              │                   │
│  └─────────────────────────────────────────────┘                   │
│                                                                     │
│  ┌─────────────────────────────────────────────┐                   │
│  │           Persistence Layer                   │                   │
│  │  SQLite + File Storage (projects, exports)   │                   │
│  └─────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
    ┌─────▼─────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  Modal    │   │   Groq /    │   │   Ollama    │
    │  GLM-5.1  │   │   Gemini   │   │  (local)    │
    └───────────┘   └────────────┘   └─────────────┘
```

---

## Technology Stack

### Backend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python | 3.11+ | Primary language |
| **Framework** | FastAPI | 0.110+ | Async API server with auto OpenAPI docs |
| **Validation** | Pydantic | 2.x | Data models, validation, serialization |
| **Agent Framework** | Pydantic AI | 0.x | Agent definition, structured I/O, tool use |
| **LLM Client** | `openai` (OpenAI-compatible) | 1.x | Unified client for Modal, Groq, Gemini, Ollama |
| **LLM Client** | `google-generativeai` | 0.x | Google Gemini-specific client |
| **LLM Client** | `ollama` | 0.x | Ollama local client |
| **Database** | SQLite (via `aiosqlite`) | 3.x | Project and pipeline state persistence |
| **ORM** | SQLAlchemy | 2.x | Async database models and queries |
| **Migration** | Alembic | 1.x | Database schema migrations |
| **WebSocket** | FastAPI native | — | Real-time agent progress and streaming |
| **HTTP Client** | `httpx` | 0.x | Async HTTP for external APIs (YouTube, Piragi) |
| **Piragi Client** | `piragi` | latest | Local RAG client for document querying and retrieval |
| **Testing** | `pytest` + `pytest-asyncio` | — | Backend unit and integration tests |

### Frontend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | Next.js | 14+ (App Router) | React framework with SSR/SSG |
| **UI Components** | Shadcn/UI | latest | Accessible, composable component library |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **State Management** | Zustand | 4.x | Lightweight global state |
| **Data Fetching** | TanStack Query (React Query) | 5.x | Server state, caching, real-time updates |
| **WebSocket** | Native WebSocket API | — | Real-time streaming from backend |
| **Forms** | React Hook Form + Zod | — | Form handling and client-side validation |
| **Markdown** | `react-markdown` | — | Markdown rendering for script preview/export |
| **Rich Editor** | Tiptap (or Slate.js) | — | Inline script editing with formatting |
| **Icons** | Lucide React | — | Icon library matching Shadcn/UI |
| **Testing** | Vitest + React Testing Library | — | Frontend unit and component tests |

### Dev & Build Tools

| Tool | Purpose |
|------|---------|
| `uv` | Fast Python package management |
| `npm` / `pnpm` | Node.js package management |
| `ruff` | Python linting and formatting |
| `eslint` + `prettier` | JS/TS linting and formatting |
| `docker` + `docker-compose` | Optional containerized deployment |
| `pre-commit` | Git hook management |

---

## Data Design & Schema

### Storage Strategy: SQLite + File System

**Rationale:** SQLite is chosen for structured project data because it requires zero configuration, runs as a file on disk, and handles single-user workloads efficiently. Large text content (notes, scripts) is stored inline in SQLite. File exports are written to the filesystem in a configurable output directory.

### Entity-Relationship Overview

```
Project 1──* PipelineStep
Project 1──1 ICP
Project 1──* ScriptVersion
Project 1──* AnalysisResult
```

### Database Schema

#### `projects`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | UUID | PK | Unique project identifier |
| name | VARCHAR(100) | NOT NULL | Project name |
| topic | VARCHAR(200) | NOT NULL | Content topic/subject |
| target_format | VARCHAR(20) | NOT NULL | VSL, YouTube, Tutorial, Facebook, LinkedIn, Blog |
| content_goal | VARCHAR(20) | NULL | Sell, Educate, Entertain, Build Authority |
| raw_notes | TEXT | NOT NULL | User's original notes |
| status | VARCHAR(20) | NOT NULL DEFAULT 'draft' | draft, in_progress, completed |
| current_step | INTEGER | NOT NULL DEFAULT 0 | Current pipeline step index |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last modification timestamp |

#### `projects` (Piragi extension)

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| piragi_document_paths | VARCHAR(500) | NULL | Connected Piragi document paths (comma-separated) |

#### `icp_profiles`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | UUID | PK | Unique ICP identifier |
| project_id | UUID | FK → projects.id, UNIQUE | One ICP per project |
| demographics | JSON | NOT NULL | Age, gender, location, occupation, income |
| psychographics | JSON | NOT NULL | Values, interests, attitudes, lifestyle |
| pain_points | JSON | NOT NULL | Array of pain point strings |
| desires | JSON | NOT NULL | Array of desire strings |
| objections | JSON | NOT NULL | Array of objection strings |
| language_style | VARCHAR(50) | NOT NULL | casual, professional, technical |
| source | VARCHAR(20) | NOT NULL | generated, uploaded, notebooklm |
| approved | BOOLEAN | NOT NULL DEFAULT FALSE | User has approved the ICP |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last modification timestamp |

#### `pipeline_steps`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | UUID | PK | Step identifier |
| project_id | UUID | FK → projects.id | Parent project |
| step_type | VARCHAR(30) | NOT NULL | icp, hook, narrative, retention, cta, writer, factcheck, readability, copyright, policy |
| step_order | INTEGER | NOT NULL | Execution order within pipeline |
| status | VARCHAR(20) | NOT NULL DEFAULT 'pending' | pending, running, completed, failed |
| input_data | JSON | NOT NULL | Agent input payload |
| output_data | JSON | NULL | Agent output payload |
| selected_option | JSON | NULL | User's selection from agent output |
| llm_provider | VARCHAR(20) | NULL | Provider used for this step |
| token_count | INTEGER | NULL | Tokens consumed |
| duration_ms | INTEGER | NULL | Execution duration in milliseconds |
| error_message | TEXT | NULL | Error details if failed |
| started_at | TIMESTAMP | NULL | Execution start |
| completed_at | TIMESTAMP | NULL | Execution end |

#### `script_versions`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | UUID | PK | Version identifier |
| project_id | UUID | FK → projects.id | Parent project |
| version_number | INTEGER | NOT NULL | Incremental version |
| content | TEXT | NOT NULL | Full script text |
| format | VARCHAR(20) | NOT NULL | Output format |
| hook_text | TEXT | NULL | Selected hook |
| narrative_pattern | VARCHAR(50) | NULL | Selected narrative |
| retention_techniques | JSON | NULL | Selected techniques |
| cta_text | TEXT | NULL | Selected CTA |
| created_at | TIMESTAMP | NOT NULL | Version timestamp |

#### `analysis_results`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | UUID | PK | Result identifier |
| project_id | UUID | FK → projects.id | Parent project |
| script_version_id | UUID | FK → script_versions.id | Analyzed script version |
| agent_type | VARCHAR(20) | NOT NULL | factcheck, readability, copyright, policy |
| findings | JSON | NOT NULL | Array of finding objects: {type, severity, text, suggestion, confidence} |
| overall_score | FLOAT | NULL | Aggregate score (readability index, etc.) |
| created_at | TIMESTAMP | NOT NULL | Analysis timestamp |

### JSON Field Schemas

#### `icp_profiles.demographics`
```json
{
  "age_range": "25-45",
  "gender": "any",
  "location": "global",
  "occupation": ["software engineer", "developer"],
  "income": "mid-to-high"
}
```

#### `pipeline_steps.input_data` / `output_data`
```json
{
  "input": { "notes": "...", "icp": {...}, "topic": "..." },
  "output": { "suggestions": [...], "rankings": [...] }
}
```

#### `analysis_results.findings` (single finding)
```json
{
  "type": "factual_claim",
  "severity": "medium",
  "text": "Python is the most popular language",
  "suggestion": "Add qualifier: 'one of the most popular'",
  "confidence": "low"
}
```

---

## API & Integration Specifications

### REST API Endpoints

#### Projects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects` | List all projects |
| POST | `/api/v1/projects` | Create a new project |
| GET | `/api/v1/projects/{project_id}` | Get project details |
| PATCH | `/api/v1/projects/{project_id}` | Update project metadata |
| DELETE | `/api/v1/projects/{project_id}` | Delete a project |

#### Pipeline

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/pipeline` | Get full pipeline state (all steps) |
| POST | `/api/v1/projects/{project_id}/pipeline/run/{step_type}` | Run a specific agent |
| POST | `/api/v1/projects/{project_id}/pipeline/run-all` | Run all pending agents sequentially |
| PATCH | `/api/v1/projects/{project_id}/pipeline/{step_id}` | Update step (user selection, approval) |

#### ICP

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/icp` | Get ICP profile |
| POST | `/api/v1/projects/{project_id}/icp/generate` | Generate ICP from notes |
| PATCH | `/api/v1/projects/{project_id}/icp` | Update/approve ICP |
| POST | `/api/v1/projects/{project_id}/icp/upload` | Upload existing ICP file |

#### Script

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/scripts` | List script versions |
| GET | `/api/v1/projects/{project_id}/scripts/{version_id}` | Get specific version |
| POST | `/api/v1/projects/{project_id}/scripts/generate` | Generate script from pipeline selections |
| PATCH | `/api/v1/projects/{project_id}/scripts/{version_id}` | Edit script content |

#### Analysis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/{project_id}/analyze/{agent_type}` | Run a specific analysis agent |
| POST | `/api/v1/projects/{project_id}/analyze/all` | Run all analysis agents in parallel |
| GET | `/api/v1/projects/{project_id}/analysis` | Get analysis results |

#### Export

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/export?format=txt` | Export as plain text |
| GET | `/api/v1/projects/{project_id}/export?format=md` | Export as Markdown |
| POST | `/api/v1/projects/{project_id}/export/clipboard` | Copy to clipboard |

#### Piragi

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{project_id}/piragi/documents` | List available Piragi documents |
| POST | `/api/v1/projects/{project_id}/piragi/connect` | Connect documents to the project |
| DELETE | `/api/v1/projects/{project_id}/piragi/connect` | Disconnect documents from project |
| POST | `/api/v1/projects/{project_id}/piragi/query` | Query connected documents for insights |
| POST | `/api/v1/projects/{project_id}/pipeline/run/{step_type}` | (Modified) Accepts optional `piragi_context` field |

#### Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/settings/llm` | Get LLM provider configuration |
| PATCH | `/api/v1/settings/llm` | Update LLM provider configuration |
| GET | `/api/v1/settings/llm/status` | Check connectivity to configured providers |

### WebSocket Endpoint

| Path | Description |
|------|-------------|
| `ws://localhost:8000/ws/pipeline/{project_id}` | Real-time pipeline events: agent start, progress, completion, streaming tokens |

**WebSocket Message Format:**
```json
{
  "event": "agent_progress",
  "step_type": "hook",
  "status": "running",
  "progress": 0.5,
  "streaming_token": "compelling"
}
```

```json
{
  "event": "agent_complete",
  "step_type": "hook",
  "status": "completed",
  "output": { "suggestions": [...] }
}
```

### External API Integrations

#### Modal LLM API (Primary)

| Property | Value |
|----------|-------|
| Base URL | `https://api.us-west-2.modal.direct/v1` |
| Protocol | HTTPS, OpenAI-compatible REST |
| Auth | API key via `Authorization: Bearer` header |
| Models | GLM-5.1 |
| Rate Limits | Per free-tier policy |
| SDK | `openai` Python package (OpenAI-compatible mode) |

#### Groq API

| Property | Value |
|----------|-------|
| Base URL | `https://api.groq.com/openai/v1` |
| Protocol | HTTPS, OpenAI-compatible REST |
| Auth | API key via `Authorization: Bearer` header |
| Models | Per Groq free-tier availability |
| SDK | `openai` Python package |

#### Google Gemini API

| Property | Value |
|----------|-------|
| Base URL | Gemini REST API |
| Protocol | HTTPS |
| Auth | API key |
| SDK | `google-generativeai` Python package |

#### Ollama (Local)

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:11434` |
| Protocol | HTTP REST |
| Auth | None |
| Models | User-installed models |
| SDK | `ollama` Python package |

#### YouTube Data API (Optional)

| Property | Value |
|----------|-------|
| Protocol | HTTPS REST |
| Auth | API key |
| Purpose | Video metadata for policy context |
| SDK | `google-api-python-client` |

#### Piragi RAG (Optional)

| Property | Value |
|----------|-------|
| Base URL | Local filesystem or remote storage (S3, GCS, Azure) |
| Protocol | Local file I/O or HTTPS |
| Auth | None (local) or storage-specific |
| Purpose | Document context integration — list documents, query insights |
| SDK | `piragi` Python package |

---

## Infrastructure & Deployment

### Local Development

| Component | Detail |
|-----------|--------|
| **Backend** | `uvicorn` dev server on `localhost:8000` with hot reload |
| **Frontend** | `next dev` on `localhost:3000` with hot reload |
| **Database** | SQLite file in `./data/scripts_writer.db` |
| **Exports** | `./data/exports/` directory |
| **Environment** | `.env` file for API keys and configuration |

### Production (Self-Hosted)

| Component | Detail |
|-----------|--------|
| **Backend** | `uvicorn` behind `gunicorn` with Uvicorn workers (or Docker) |
| **Frontend** | `next build` + `next start`, or static export served by backend |
| **Database** | SQLite file in persistent volume |
| **Reverse Proxy** | Optional: Caddy or Nginx for TLS termination |
| **Containerization** | Docker + `docker-compose.yml` for one-command deployment |

### Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env:ro
    environment:
      - DATABASE_URL=sqlite:///data/scripts_writer.db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

### CI/CD

| Pipeline | Tool | Purpose |
|----------|------|---------|
| Lint | `ruff` (Python) + `eslint` (JS) | Code quality |
| Type Check | `mypy` (Python) + `tsc` (TS) | Type safety |
| Test | `pytest` + `vitest` | Unit and integration tests |
| Build | Docker | Production image |
| Deploy | Manual / Git push to server | Self-hosted deployment |

### Environments

| Environment | Purpose | Config |
|-------------|---------|--------|
| **Development** | Local development with hot reload | `.env.development` |
| **Production** | Self-hosted single-instance | `.env.production` |

---

## Security Architecture

### Authentication & Authorization

| Aspect | v1 Implementation |
|--------|------------------|
| **User Auth** | None — single-user local tool; no login required |
| **API Auth** | None — backend bound to `localhost`; not exposed to network |
| **Future** | JWT-based auth if multi-user support is added |

### API Key Management

| Requirement | Implementation |
|------------|----------------|
| Storage | `.env` file (git-ignored); OS environment variables |
| Access | Loaded via `pydantic-settings` Settings class at startup |
| Masking | API keys masked in `/settings` API responses (show last 4 chars only) |
| Validation | Startup check verifies each configured key is non-empty |
| Piragi credentials | Document paths configured in `.env` |

### AppSettings (Pydantic Settings Model)

```python
class AppSettings(BaseSettings):
    # ... existing LLM provider fields ...
    google_cloud_project: str
    google_cloud_location: str = "us"
    google_application_credentials: str = ""
```

### Data Protection

| Requirement | Implementation |
|------------|----------------|
| Data at rest | No encryption — local SQLite file on user's machine; OS-level security applies |
| Data in transit | HTTPS/TLS for all cloud LLM API calls |
| Data retention | All data stored locally; user controls deletion via project management |
| Data external | Notes and scripts are sent to LLM providers for inference; subject to provider privacy policies |

### Input Validation

| Layer | Mechanism |
|-------|-----------|
| API | Pydantic models validate all request bodies, query params, path params |
| Agent | Pydantic AI validates agent inputs/outputs with structured schemas |
| Frontend | Zod schemas for form validation; server-side validation as ground truth |

---

## Performance & Scalability

### Caching Strategy

| Cache | Purpose | Implementation |
|-------|---------|----------------|
| LLM Response Cache | Avoid re-generating identical prompts | In-memory LRU cache keyed by prompt hash + model + provider |
| Project State Cache | Reduce DB reads for active project | In-memory cache, invalidated on write |
| Static Assets | Frontend performance | Next.js built-in static optimization, CDN if deployed |

### Performance Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| Individual agent execution | ≤ 60s | Prompt optimization; streaming to reduce perceived latency |
| Full pipeline compute | ≤ 3 min | Parallel execution of analysis agents; efficient prompt design |
| API response (non-LLM) | ≤ 200ms | Async FastAPI + SQLite with proper indexing |
| Frontend page load | ≤ 2s | Next.js SSR/SSG, code splitting, lazy loading |
| WebSocket message latency | ≤ 100ms | Local network; no external relay |

### Scaling Considerations

| Dimension | v1 Approach | Future Path |
|-----------|-------------|-------------|
| Concurrent users | Single user | Multi-user via session management and per-user DB |
| LLM throughput | Provider failover + retry queue | Request queuing with priority levels |
| Agent parallelism | `asyncio.gather` for analysis agents | Distributed task queue (Celery/RQ) |
| Data volume | SQLite file | PostgreSQL for multi-user |

### LLM Provider Failover

```
Request → Provider 1 (Modal)
         ↓ rate limit / error
         → Provider 2 (Groq) — retry with backoff
         ↓ rate limit / error
         → Provider 3 (Gemini) — retry with backoff
         ↓ rate limit / error
         → Provider 4 (Ollama) — local fallback
         ↓ all failed
         → Return error to user with provider status summary
```

Provider order is user-configurable. The system attempts each configured provider in sequence before failing.

---

## Error Handling & Logging

### Error Handling Strategy

| Error Category | Handling |
|----------------|----------|
| **LLM API errors (rate limit, 429)** | Exponential backoff (1s, 2s, 4s); max 3 retries; then failover to next provider |
| **LLM API errors (5xx, timeout)** | Retry up to 2 times; then failover; log full error |
| **LLM API errors (4xx, auth)** | No retry; return error to user with configuration guidance |
| **LLM malformed output** | Retry with restructured prompt (max 2 retries); then present raw output with warning |
| **Database errors** | Log error; return 500 to client; auto-save should prevent data loss |
| **Validation errors** | Return 422 with Pydantic error details; frontend shows field-level errors |
| **File I/O errors** | Log error; return 500; ensure export directory exists before write |
| **Ollama not running** | Detect connection refused; return specific error prompting user to start Ollama or switch provider |
| **WebSocket disconnect** | Client auto-reconnects with exponential backoff; server resumes streaming on reconnect |

### Logging

| Component | Framework | Level | Output |
|-----------|-----------|-------|--------|
| FastAPI | `structlog` | INFO (prod), DEBUG (dev) | Stdout + `./logs/app.log` |
| Agents | `structlog` | INFO | Stdout + `./logs/agents.log` |
| LLM calls | `structlog` | DEBUG | Stdout + `./logs/llm.log` |

### Log Format (Structured JSON)

```json
{
  "timestamp": "2026-04-11T10:30:00.000Z",
  "level": "info",
  "event": "agent_execution",
  "agent": "hook",
  "project_id": "abc-123",
  "provider": "modal",
  "duration_ms": 4500,
  "token_count": 850,
  "status": "completed"
}
```

### Health Check

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Returns `{"status": "ok"}` if backend is running |
| `GET /api/v1/settings/llm/status` | Returns connectivity status for each configured LLM provider |

### Monitoring (Optional, Future)

| Tool | Purpose |
|------|---------|
| Prometheus metrics | Request counts, latency histograms, LLM token usage |
| Grafana dashboard | Visualization of system performance |
| Alerting | Notify if all LLM providers are unreachable |
