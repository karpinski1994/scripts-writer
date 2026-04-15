# High-Level Design – Scripts Writer

## Conceptual Architecture

### Pattern: Layered Pipeline Architecture with Agent Orchestration

Scripts Writer follows a **layered architecture** with a central **pipeline orchestration** layer. Each layer has a single responsibility and communicates only with adjacent layers through well-defined interfaces. The pipeline layer sits between the presentation and domain layers, coordinating the sequential execution of autonomous agents.

**Rationale for this pattern:**

| Factor | Decision Driver |
|--------|----------------|
| Sequential agent workflow | The core domain is a pipeline — agents must execute in order with user decision points |
| Single deployment unit | Layered monolith avoids distributed system complexity for a local, single-user tool |
| Clear separation of concerns | Each layer can be developed, tested, and replaced independently |
| Future extensibility | New agents, LLM providers, or output formats slot into existing layers without structural changes |

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│                   Next.js + Shadcn/UI + Tailwind                │
│  Dashboard · Pipeline View · Agent Panels · Script Editor       │
│  Analysis Panel · Settings · Export                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST + WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                        API LAYER                                 │
│                     FastAPI Routers                               │
│  /projects · /pipeline · /icp · /scripts · /analysis            │
│  /export · /settings · /rag · /notebooklm · /ws/pipeline/{id}   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   ORCHESTRATION LAYER                             │
│          Pipeline Orchestrator · State Machine                   │
│  Sequential execution · User decision points · Parallel analysis │
│  Branching · Re-run · Dependency resolution                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     DOMAIN LAYER                                 │
│                    Agent Modules                                 │
│  ICP · Hook · Narrative · Retention · CTA · Writer              │
│  FactCheck · Readability · Copyright · Policy                   │
│  Each agent: Raw LLM calls with manual JSON parsing             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                            │
│          LLM Adapter · Persistence · External APIs              │
│  Modal · Groq · Gemini · Ollama · SQLite · File Storage         │
│  YouTube Data API · Google LM Notes                              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Alternative Considered | Rationale |
|----------|--------|----------------------|-----------|
| Monolith vs Microservices | Modular monolith | Microservices | Single user, zero budget, solo developer — no need for independent scaling |
| Synchronous vs Event-driven | Synchronous pipeline with async I/O | Event-driven / message queue | Pipeline steps have explicit dependencies and ordering; user waits at decision points |
| Client-side vs Server-side rendering | Hybrid (Next.js SSR + CSR) | SPA only | SSR for initial page loads; CSR for interactive pipeline and streaming |
| Database | SQLite | PostgreSQL | Zero config, file-based, sufficient for single user; easy migration path |
| State management | Server-authoritative with optimistic client | Client-authoritative | Server is source of truth; client optimistically updates for responsiveness |
| Agent execution | In-process (asyncio) | External worker (Celery) | Single user, single process; no queue overhead needed for v1 |

---

## System Decomposition

### Major Modules & Responsibilities

```
Scripts Writer
├── Frontend (Next.js)
│   ├── Dashboard Module
│   │   ├── Project list with status badges
│   │   └── Create new project flow
│   ├── Pipeline Module
│   │   ├── Pipeline view (step-by-step progress)
│   │   ├── Step sidebar (non-linear navigation)
│   │   └── Pipeline state indicator
│   ├── Agent Interaction Module
│   │   ├── ICP panel (review, edit, approve)
│   │   ├── Hook panel (select, edit, custom)
│   │   ├── Narrative panel (select with descriptions)
│   │   ├── Retention panel (multi-select with placements)
│   │   ├── CTA panel (select, customize, placement)
│   │   └── Writer panel (streaming draft generation)
│   ├── Script Module
│   │   ├── Rich text editor (inline editing)
│   │   ├── Version history viewer
│   │   └── Format preview (per output format)
│   ├── Analysis Module
│   │   ├── Fact-check tab (claims, confidence, suggestions)
│   │   ├── Readability tab (scores, complex sentences, fixes)
│   │   ├── Copyright tab (warnings, acknowledgements)
│   │   └── Policy tab (platform-specific flags)
│   ├── Export Module
│   │   ├── Format selection (txt, md, clipboard)
│   │   └── Download trigger
│   └── Settings Module
│       ├── LLM provider configuration
│       ├── Provider connectivity status
│       └── Default preferences
│
├── Backend (FastAPI)
│   ├── API Module
│   │   ├── Project router (CRUD)
│   │   ├── Pipeline router (run, select, branch)
│   │   ├── ICP router (generate, upload, approve)
│   │   ├── Script router (generate, edit, version)
│   │   ├── Analysis router (run individual agents - no run all)
│   │   ├── Export router (txt, md, clipboard)
│   │   └── Settings router (LLM config, health)
│   ├── Pipeline Module
│   │   ├── Orchestrator (sequential + parallel execution)
│   │   ├── State machine (transitions, dependencies)
│   │   └── Branch manager (project copy from step)
│   ├── Agent Module
│   │   ├── Base agent (template method, caching, failover)
│   │   ├── Creative agents (ICP, Hook, Narrative, Retention, CTA, Writer)
│   │   └── Analysis agents (FactCheck, Readability, Copyright, Policy)
│   ├── LLM Module
│   │   ├── Provider interface (abstract)
│   │   ├── Modal provider (OpenAI-compatible)
│   │   ├── Groq provider (OpenAI-compatible)
│   │   ├── Gemini provider (Google SDK)
│   │   ├── Ollama provider (local HTTP)
│   │   ├── Provider factory (failover chain)
│   │   └── Response cache (LRU)
│   ├── Persistence Module
│   │   ├── Database engine + sessions
│   │   ├── ORM models (SQLAlchemy)
│   │   ├── Migrations (Alembic)
│   │   └── File storage (exports, uploads)
│   ├── Integration Module
│   │   ├── Piragi client (connect, query, disconnect)
│   │   └── Google Drive file reference (optional, future)
```

```
Piragi Panel ──► Piragi Router ──► Piragi Service ──► Local filesystem
```

### Module Dependency Graph

```
Dashboard ──────► Project Router ──────► Project Service ──────► DB Models
    │                                       │
Pipeline View ──► Pipeline Router ─────► Pipeline Service ───► DB Models
    │                                       │
Agent Panels ──► Pipeline Router            ├────► Orchestrator ──► Agent Module
    │                                       │                         │
Script Editor ──► Script Router ──────► Script Service               │
    │                                       │                    LLM Module
Analysis Panel ► Analysis Router ────► Analysis Service              │
    │                                       │                         │
Export ────────► Export Router ──────► Export Service                 │
    │                                                               │
Settings ──────► Settings Router ───► Settings Service ─────► LLM Module
                                                                    │
                                                              Provider Factory
                                                                    │
                                                     ┌───────────┬───┴───┬──────────┐
                                                     │           │       │          │
                                                  Modal      Groq   Gemini    Ollama

NotebookLM Panel ──► NotebookLM Router ──► NotebookLM Service ──► Google Cloud API
```

---

## Data Flow & Communication

### Synchronous vs Asynchronous Communication

| Communication Path | Protocol | Rationale |
|-------------------|----------|-----------|
| Frontend ↔ Backend (CRUD) | HTTP REST | Request-response pattern; standard CRUD semantics |
| Frontend ↔ Backend (agent streaming) | WebSocket | Real-time token streaming; bidirectional for progress updates |
| Backend → LLM Providers | HTTP REST (async) | LLM APIs are request-response; `asyncio` for concurrency |
| Backend → YouTube / LM Notes APIs | HTTP REST (async) | Standard API calls; optional features |
| Backend → SQLite | Async I/O via `aiosqlite` | Non-blocking database access within async event loop |
| Backend → File System | Async I/O via `aiofiles` | Non-blocking file writes for exports |

### Data Flow: Full Pipeline Execution

```
1. USER SUBMITS NOTES
   Frontend ──POST /projects──► API ──► ProjectService ──► SQLite
   Frontend ◄──201 {project}── API ◄── ProjectService ◄── SQLite

1a. USER ATTACHES PIRAGI DOCUMENTS (OPTIONAL)
   Frontend ──POST /rag/connect──► API ──► Piragi Service ──► Local filesystem
   Store document_paths on project

2. USER TRIGGERS ICP AGENT (If Piragi documents connected, query for ICP-related insights; include in agent prompt)
   Frontend ──POST /pipeline/run/icp──► API ──► Orchestrator
   Orchestrator ──► ICPAgent ──► LLMProvider ──► Modal/Groq/Gemini/Ollama
   LLMProvider ◄──streaming tokens── External
   Orchestrator ──WS: agent_progress──► Frontend (live text)
   Orchestrator ──► SQLite (save step output)
   API ◄──200 {step result}── Orchestrator
   Frontend ◄──200── API (final result)

3. USER REVIEWS ICP & MAKES SELECTION
   Frontend ──PATCH /pipeline/{step_id}──► API ──► PipelineService ──► SQLite
   (selected_option saved; downstream steps invalidated if re-running)

4. STEPS 4–7: HOOK, NARRATIVE, RETENTION, CTA (same pattern as ICP)
   Each: Frontend triggers run → Agent executes → Streaming via WS → User selects → Save

5. WRITER AGENT GENERATES SCRIPT
   Frontend ──POST /pipeline/run/writer──► API ──► Orchestrator
   Orchestrator ──► WriterAgent (assembles all selections into prompt)
   WriterAgent ──► LLMProvider ──► External
   Streaming output via WebSocket to frontend
   New ScriptVersion saved to SQLite

6. ANALYSIS AGENTS RUN INDIVIDUALLY (user clicks each tab to run)
   Frontend ──POST /analysis/{agentType}──► API ──► Orchestrator
   Orchestrator ──► Agent (FactCheck OR Readability OR Copyright OR Policy)
   Agent ──► LLMProvider ──► External
   Result saved to SQLite
   Frontend ◄──200 {analysis result}── API

   Note: run_analysis_parallel() exists but is not exposed via API (no /analysis/all endpoint)

7. USER EXPORTS SCRIPT
   Frontend ──GET /export?format=md──► API ──► ExportService
   ExportService ──► File System (write file)
   Frontend ◄──200 file download── API
```

### Data Flow: WebSocket Streaming

```
Frontend                              Backend
   │
   │  WS connect /ws/pipeline/{id}
   │─────────────────────────────────────►
   │  101 Switching Protocols
   │◄─────────────────────────────────────│
   │
   │  (user triggers agent)
   │
   │  WS: {event: "agent_start",
   │       step_type: "hook"}
   │◄─────────────────────────────────────│
   │
   │  (no streaming tokens - real-time status only)
   │
   │  WS: {event: "agent_complete",
   │       step_type: "hook",
   │       status: "completed",
   │       output: {...}}
   │◄─────────────────────────────────────│
```

---

## Integration Architecture

### External Service Integration Map

```
┌─────────────────────────────────────────────────────────────┐
│                    Scripts Writer Backend                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              LLM Adapter Layer                       │    │
│  │                                                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │    │
│  │  │  Modal   │  │  Groq    │  │  Gemini  │  │Ollama│ │    │
│  │  │  Adapter │  │  Adapter │  │  Adapter │  │Adapter│ │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──┬──┘ │    │
│  └───────┼─────────────┼─────────────┼────────────┼────┘    │
│          │             │             │             │          │
└──────────┼─────────────┼─────────────┼────────────┼──────────┘
           │             │             │             │
           ▼             ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Modal   │  │  Groq    │  │  Google  │  │  Ollama  │
    │  API     │  │  API     │  │  Gemini  │  │  Local   │
    │          │  │          │  │  API     │  │  :11434  │
    │ GLM-5.1  │  │  Free    │  │  Free    │  │  User    │
    │ Free     │  │  Tier    │  │  Tier    │  │  Models  │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘

    ┌──────────────────┐  ┌──────────────────┐
    │  YouTube Data    │  │  Google LM Notes │
    │  API (optional)  │  │  API (optional)  │
    └──────────────────┘  └──────────────────┘
```

### Integration Details

| Integration | Direction | Protocol | Auth | Data Exchanged | Failure Mode |
|------------|-----------|----------|------|----------------|-------------|
| Gemini | Outbound | HTTPS REST (Google SDK) | API key | Same as Modal | Failover to next provider |
| Groq | Outbound | HTTPS REST (OpenAI-compatible) | API key (Bearer) | Same as Modal | Failover to next provider |
| Modal | Outbound | HTTPS REST (OpenAI-compatible) | API key (Bearer) | User notes + ICP + selections → generated text | Failover to next provider |
| Ollama | Outbound | HTTP REST | None | Same as Modal | Prompt user to start Ollama or switch provider |
| YouTube Data | Outbound | HTTPS REST | API key | Video metadata queries | Graceful degradation; analysis proceeds without |
| Piragi RAG | Outbound | Local I/O | Document paths | Step-relevant query → contextual insights | Graceful degradation; agents use raw notes only |

### Integration Resilience

```
Request ──► Gemini
             ├── Success ──► Return result
             └── Failure (429/5xx/timeout)
                  └── Retry (max 3, exponential backoff)
                       └── Still failing ──► Groq
                                             ├── Success ──► Return result
                                             └── Failure ──► Modal
                                                           ├── Success ──► Return result
                                                           └── Failure ──► Ollama
                                                                        ├── Success ──► Return result
                                                                        └── Failure ──► Return error to user
                                                                                        with provider status summary
```

---

## High-Level Data Strategy

### Source of Truth

| Data | Source of Truth | Rationale |
|------|-----------------|-----------|
| Project metadata | SQLite `projects` table | Single authoritative store; server-side |
| ICP profile | SQLite `icp_profiles` table | Generated once, user-approved; server persists |
| Pipeline state | SQLite `pipeline_steps` table | Server tracks step status, inputs, outputs, selections |
| Script content | SQLite `script_versions` table | Versioned on server; client edits are PATCHed |
| Analysis results | SQLite `analysis_results` table | Per script version, per agent; server-owned |
| LLM configuration | `.env` file + SQLite `settings` | Env vars for secrets; DB for non-secret preferences |
| User session | In-memory (single user) | No auth; single browser session |

### Caching Strategy

| Cache Layer | What | TTL | Invalidation |
|-------------|------|-----|-------------|
| LLM Response Cache | Prompt hash → LLM output | 1 hour | LRU eviction (max 128 entries) |
| Frontend Server Cache (TanStack Query) | API responses | 30s staleTime | WebSocket event triggers invalidation |
| Frontend Client State (Zustand) | Streaming output, editor content | Session-only | On agent re-run or project switch |
| Next.js Static Assets | JS bundles, CSS | Build-time | Cache-busting via content hash |

### Data Consistency Model

| Operation | Consistency Level | Mechanism |
|-----------|-------------------|-----------|
| Project CRUD | Strong | SQLite ACID transactions |
| Pipeline step execution | Strong | Step-level DB transactions; auto-save after each agent |
| Script editing | Eventual | Debounced PATCH (500ms); optimistic client updates |
| LLM cache | Eventual | Stale reads acceptable; 1h TTL |
| Analysis results | Strong | Written once per script version; immutable |

### Data Lifecycle

| Data Type | Creation | Update | Deletion |
|-----------|----------|--------|----------|
| Project | User creates project | User edits metadata | User deletes project (cascading) |
| ICP | Agent generates or user uploads | User edits/approves | Cascading delete with project |
| Pipeline step | Created on project init (pending) | Agent execution, user selection | Cascading delete with project |
| Script version | Writer agent generates | User inline edits (new version) | Cascading delete with project |
| Analysis results | Analysis agents produce | Not updatable (re-run creates new) | Cascading delete with project |
| LLM cache entries | Agent execution (cache miss) | Never updated (immutable entries) | LRU eviction or TTL expiry |
| Export files | User triggers export | Never updated | Manual cleanup by user |

---

## Infrastructure & Deployment View

### Deployment Topology (Local)

```
┌──────────────────── User's Machine (macOS) ────────────────────┐
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Browser       │  │   Next.js       │  │   FastAPI       │ │
│  │   (Chrome,      │  │   :3000         │  │   :8000         │ │
│  │    Safari, etc) │  │                 │  │                 │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                     │          │
│           └────────────────────┼─────────────────────┘          │
│                                │                                │
│                    ┌───────────▼───────────┐                    │
│                    │      SQLite DB        │                    │
│                    │  ./data/scripts.db    │                    │
│                    └───────────────────────┘                    │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   Ollama         │  │   Exports Dir   │                       │
│  │   :11434         │  │  ./data/exports/ │                       │
│  └─────────────────┘  └─────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                    │
                    │ HTTPS (outbound)
                    ▼
        ┌───────────────────────┐
        │   Cloud LLM Providers │
        │   Modal · Groq ·     │
        │   Gemini              │
        └───────────────────────┘
```

### Deployment Topology (Docker)

```
┌──────────────────── Docker Host ────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  docker-compose                                           │  │
│  │                                                           │  │
│  │  ┌─────────────────┐    ┌─────────────────┐              │  │
│  │  │  frontend        │    │  backend         │              │  │
│  │  │  Next.js :3000   │    │  FastAPI :8000   │              │  │
│  │  └─────────────────┘    └────────┬─────────┘              │  │
│  │                                  │                         │  │
│  │                    ┌─────────────▼──────────────┐          │  │
│  │                    │  Volume: ./data             │          │  │
│  │                    │  ├── scripts_writer.db     │          │  │
│  │                    │  └── exports/              │          │  │
│  │                    └────────────────────────────┘          │  │
│  │                                                           │  │
│  │  ┌─────────────────┐                                      │  │
│  │  │  .env (read-only)│                                      │  │
│  │  └─────────────────┘                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Network Architecture

| Path | Protocol | Port | Direction |
|------|----------|------|-----------|
| Browser → Next.js | HTTP | 3000 | Inbound |
| Next.js → FastAPI | HTTP/WS | 8000 | Outbound |
| FastAPI → Modal | HTTPS | 443 | Outbound |
| FastAPI → Groq | HTTPS | 443 | Outbound |
| FastAPI → Gemini | HTTPS | 443 | Outbound |
| FastAPI → Ollama | HTTP | 11434 | Outbound (localhost) |
| FastAPI → YouTube API | HTTPS | 443 | Outbound (optional) |
| FastAPI → LM Notes API | HTTPS | 443 | Outbound (optional) |

---

## Cross-Cutting Concerns

### Security

| Concern | Implementation | Enforcement Point |
|---------|---------------|-------------------|
| API key protection | `.env` file (git-ignored); masked in API responses | Config module; Settings router |
| Transport encryption | HTTPS for all cloud LLM calls | LLM adapter layer |
| Input validation | Pydantic schemas on all API inputs | API layer (FastAPI auto-validation) |
| Output sanitization | Strip markdown/HTML from LLM output before rendering | Agent output processing |
| No telemetry | Zero analytics or tracking code | Architecture-level decision |
| Local-only data | No external persistence; all data on user's machine | Persistence layer |

### Observability

| Concern | Implementation | Scope |
|---------|---------------|-------|
| Structured logging | `structlog` JSON output per module | All backend modules |
| Agent execution metrics | Duration, token count, provider, status logged per step | Agent module |
| LLM call logging | Request/response metadata (not full content) at DEBUG level | LLM module |
| Health checks | `/health` endpoint; `/settings/llm/status` for provider connectivity | API layer |
| Frontend errors | Error boundary components; console logging | Frontend components |

### Scalability

| Concern | v1 Approach | Future Path |
|---------|-------------|-------------|
| LLM throughput | Provider failover + response caching | Request queue with priority |
| Agent parallelism | `asyncio.gather` for analysis agents | Distributed task queue |
| Data volume | SQLite (handles GB-scale for single user) | PostgreSQL for multi-user |
| Concurrent users | Single user | Session management + per-user isolation |

### Error Handling

| Concern | Implementation | Scope |
|---------|---------------|-------|
| LLM failures | Retry + failover chain across providers | LLM adapter layer |
| Agent execution failures | Step marked as `failed`; user can retry | Orchestrator |
| Database failures | Transaction rollback; auto-save per step | Persistence layer |
| WebSocket disconnects | Client auto-reconnect; server resumes | WebSocket module |
| Frontend errors | Error boundary; toast notifications | React components |

### Configuration Management

| Concern | Implementation |
|---------|---------------|
| Environment config | `pydantic-settings` Settings class; `.env` file |
| LLM provider config | Database-backed settings (non-secret); env vars (secrets) |
| Default preferences | Hardcoded defaults in Settings class; overridable via UI |
| Frontend config | `NEXT_PUBLIC_*` env vars at build time |

---

## Component Interaction Diagrams

### Path of a Request: Creating and Running a Project

```
Browser          Next.js            FastAPI           Orchestrator       ICPAgent        ModalProvider
  │                 │                  │                   │                │                │
  │ 1. Navigate     │                  │                   │                │                │
  │ to dashboard   │                  │                   │                │                │
  │────────────────>│                  │                   │                │                │
  │                 │ SSR: GET /api/v1/projects           │                │                │
  │                 │─────────────────>│                   │                │                │
  │                 │ 200 {projects[]} │                   │                │                │
  │                 │<─────────────────│                   │                │                │
  │  Render list    │                  │                   │                │                │
  │<────────────────│                  │                   │                │                │
  │                 │                  │                   │                │                │
  │ 2. Click "New" │                  │                   │                │                │
  │────────────────>│                  │                   │                │                │
  │                 │ POST /api/v1/projects                │                │                │
  │                 │─────────────────>│ ProjectService    │                │                │
  │                 │                  │──insert DB──>     │                │                │
  │                 │ 201 {project}    │                   │                │                │
  │                 │<─────────────────│                   │                │                │
  │  Show pipeline  │                  │                   │                │                │
  │<────────────────│                  │                   │                │                │
  │                 │                  │                   │                │                │
  │ 3. Enter notes  │                  │                   │                │                │
  │────────────────>│ PATCH /projects/1│                   │                │                │
  │                 │─────────────────>│──update DB──>     │                │                │
  │                 │                  │                   │                │                │
  │ 4. Click "Run  │                  │                   │                │                │
  │    ICP Agent"  │                  │                   │                │                │
  │────────────────>│ POST /pipeline/run/icp               │                │                │
  │                 │─────────────────>│──run_step(ICP)──>│                │                │
  │                 │                  │                   │ execute()      │                │
  │                 │                  │                   │───────────────>│                │
  │                 │                  │                   │                │ generate()     │
  │                 │                  │                   │                │───────────────>│
  │                 │ WS: streaming    │                   │                │  <tokens>      │
  │  <live text>    │<─────────────────│<──WS broadcast───│<──────────────│<───────────────│
  │                 │                  │                   │                │                │
  │ 5. Review ICP  │                  │                   │                │                │
  │────────────────>│                  │                   │                │                │
  │                 │ PATCH /pipeline/{step}               │                │                │
  │                 │─────────────────>│──save selection──>│                │                │
  │                 │                  │                   │                │                │
  │ 6. Continue to  │                  │                   │                │                │
  │    Hook Agent  │                  │                   │                │                │
  │────────────────>│  (repeat pattern for each agent)    │                │                │
```

### Path of a Request: Parallel Analysis Execution

```
Browser          Next.js           FastAPI          Orchestrator     FactCheck     Readability   Copyright    Policy
  │                 │                  │                  │               │             │            │           │
  │ Click "Run      │                  │                  │               │             │            │           │
  │ Fact Check"     │                  │                  │               │             │            │           │
  │────────────────>│                  │                  │               │             │            │           │
  │                 │ POST /analysis/factcheck            │               │             │            │           │
  │                 │─────────────────>│                  │               │             │            │           │
  │                 │                  │ run_step(FACTCHECK)            │             │            │           │
  │                 │                  │─────────────────>│               │             │            │           │
  │                 │                  │                  │ execute()     │             │            │           │
  │                 │                  │                  │──────────────>│             │            │           │
  │                 │                  │                  │               │ generate() │            │           │
  │                 │                  │                  │               │───────────>│            │           │
  │                 │                  │                  │               │  <result>  │            │           │
  │                 │                  │                  │               │<───────────│            │           │
  │                 │                  │                  │<──────────────│             │            │           │
  │                 │                  │                  │               │             │            │           │
  │ WS: factcheck   │                  │                  │  <results>   │             │            │           │
  │  result         │<─────────────────│<──WS broadcast───│<──────────────│             │            │           │
  │<────────────────│                  │                  │               │             │            │           │
  │                 │                  │ 200 {result}     │               │             │            │           │
  │                 │<─────────────────│<─────────────────│               │             │            │           │
  │<────────────────│                  │                  │               │             │            │           │
  │                 │                  │                  │               │             │            │           │
  │ (user repeats for readability, copyright, policy tabs as needed)              │             │            │           │
```

### Path of a Request: LLM Provider Failover

```
Orchestrator     ProviderFactory     ModalProvider      GroqProvider      GeminiProvider
     │                 │                  │                  │                  │
     │ run_step(HOOK)  │                  │                  │                  │
     │────────────────>│                  │                  │                  │
     │                 │ execute_with_    │                  │                  │
     │                 │ failover()      │                  │                  │
     │                 │─────────────────>│                  │                  │
     │                 │                  │ POST /v1/chat    │                  │
     │                 │                  │─────────────────────────────────────────────────>Modal API
     │                 │                  │  429 Rate Limit  │                  │
     │                 │                  │<─────────────────────────────────────────────────│
     │                 │  RateLimitError  │                  │                  │
     │                 │<─────────────────│                  │                  │
     │                 │                  │                  │                  │
     │                 │ retry #1 ───────>│                  │                  │
     │                 │                  │─────────────────────────────────────────────────>Modal API
     │                 │                  │  429 Rate Limit  │                  │
     │                 │                  │<─────────────────────────────────────────────────│
     │                 │  RateLimitError  │                  │                  │
     │                 │<─────────────────│                  │                  │
     │                 │                  │                  │                  │
     │                 │ retry #2 ───────>│                  │                  │
     │                 │                  │─────────────────────────────────────────────────>Modal API
     │                 │                  │  429 Rate Limit  │                  │
     │                 │                  │<─────────────────────────────────────────────────│
     │                 │  exhausted       │                  │                  │
     │                 │<─────────────────│                  │                  │
     │                 │                  │                  │                  │
     │                 │ failover ─────────────────────────>│                  │
     │                 │                  │                  │                  │
     │                 │                  │                  │ POST /v1/chat    │
     │                 │                  │                  │─────────────────>│
     │                 │                  │                  │  200 OK          │
     │                 │  result          │                  │<─────────────────│
     │<────────────────│<──────────────────────────────────│                  │
     │                 │                  │                  │                  │
```
