## Purpose

Defines the Piragi RAG integration layer: PiragiManager wrapper, service, API endpoints, database changes, and orchestrator context enrichment for connecting local/remote documents to projects via Piragi.

## ADDED Requirements

### Requirement: Piragi RAG manager
The system SHALL provide `app/rag/__init__.py` with a `PiragiManager` class that manages per-category Piragi `Ragi` instances. Methods: `get_or_create(category: str) -> Ragi`, `query(category: str, query: str, top_k: int = 3) -> list[str]`, `add_documents(category: str, sources: list[str])`, `refresh(category: str)`. The manager SHALL use `piragi.Ragi` (sync) or `piragi.AsyncRagi` (async) with a shared `persist_dir=".piragi"`. Each category maps to a `documents/` subfolder (icp, hooks, narratives, retention, cta, policies, fact_checks).

#### Scenario: Create Ragi instance for a category
- **WHEN** `get_or_create("hooks")` is called for the first time
- **THEN** a `Ragi(sources=["./documents/hooks"], persist_dir=".piragi/hooks")` is created, cached, and returned

#### Scenario: Query returns relevant chunks
- **WHEN** `query("hooks", "What are effective shock hooks for developers?", top_k=3)` is called
- **THEN** up to 3 chunk strings are returned from the hooks document corpus

#### Scenario: Query returns empty list when no documents
- **WHEN** `query("hooks", "any query")` is called and the `documents/hooks/` folder is empty
- **THEN** an empty list `[]` is returned without error

### Requirement: Piragi configuration
The system SHALL provide `app/rag/config.py` with a `STEP_CATEGORY_MAP` dict mapping `StepType` values to document category folder names: `icp→"icp"`, `hook→"hooks"`, `narrative→"narratives"`, `retention→"retention"`, `cta→"cta"`, `factcheck→"fact_checks"`, `policy→"policies"`. It SHALL also provide `PIRAGI_PERSIST_DIR = ".piragi"` and `PIRAGI_DEFAULT_TOP_K = 3`.

#### Scenario: Step type maps to correct category
- **WHEN** `STEP_CATEGORY_MAP[StepType.HOOK]` is accessed
- **THEN** it returns `"hooks"`

### Requirement: Piragi service
The system SHALL provide `app/services/piragi_service.py` with `PiragiService` that wraps `PiragiManager` with DB session handling. Methods: `connect_documents(project_id, document_paths)`, `disconnect_documents(project_id)`, `query_documents(project_id, query, step_type)`, `get_step_context(project_id, step_type)`. `connect_documents` SHALL persist document paths on the project's `piragi_document_paths` column. `disconnect_documents` SHALL set it to `None`. `get_step_context` SHALL look up the category from `STEP_CATEGORY_MAP`, call `PiragiManager.query()`, and return the concatenated chunks as a string. Returns `None` when no documents connected, on Piragi error, or when RAG returns empty results.

#### Scenario: Connect documents to project
- **WHEN** `connect_documents("proj-1", "documents/hooks,documents/icp")` is called
- **THEN** the project's `piragi_document_paths` is set to `"documents/hooks,documents/icp"` and saved to DB

#### Scenario: Disconnect documents from project
- **WHEN** `disconnect_documents("proj-1")` is called
- **THEN** the project's `piragi_document_paths` is set to `None` and saved to DB

#### Scenario: Get step context queries correct category
- **WHEN** `get_step_context("proj-1", StepType.HOOK)` is called with a connected project
- **THEN** `PiragiManager.query("hooks", step_specific_query, top_k=3)` is called and the chunks are joined into a context string

#### Scenario: Get step context returns None when no documents connected
- **WHEN** `get_step_context("proj-1", StepType.HOOK)` is called and no documents are connected
- **THEN** `None` is returned without querying Piragi

#### Scenario: Get step context returns None on Piragi error
- **WHEN** `PiragiManager.query()` raises an exception
- **THEN** the error is logged at WARNING level and `None` is returned — agent execution is not blocked

### Requirement: Piragi API endpoints
The system SHALL expose 4 endpoints: `GET /api/v1/projects/{id}/piragi/documents` (list available document categories and counts), `POST /api/v1/projects/{id}/piragi/connect` (connect document paths to project), `DELETE /api/v1/projects/{id}/piragi/connect` (disconnect), `POST /api/v1/projects/{id}/piragi/query` (query connected documents for insights).

#### Scenario: List document categories
- **WHEN** `GET /api/v1/projects/{id}/piragi/documents` is called
- **THEN** a list of document categories with file counts is returned (e.g., `[{"category": "hooks", "file_count": 5}]`)

#### Scenario: Connect documents
- **WHEN** `POST /api/v1/projects/{id}/piragi/connect` is called with `{"document_paths": "documents/hooks,documents/icp"}`
- **THEN** the documents are connected and `{"project_id": "...", "document_paths": "...", "connected": true}` is returned

#### Scenario: Disconnect documents
- **WHEN** `DELETE /api/v1/projects/{id}/piragi/connect` is called
- **THEN** the documents are disconnected and 204 is returned

#### Scenario: Query documents
- **WHEN** `POST /api/v1/projects/{id}/piragi/query` is called with `{"query": "audience insights", "step_type": "hook"}`
- **THEN** the query result chunks and citations are returned

### Requirement: Database migration for Piragi
The system SHALL add a `piragi_document_paths` column (VARCHAR(500), nullable) to the `projects` table, drop the `notebooklm_notebook_id` column, and update the `icp_profiles.source` CHECK constraint to replace `'notebooklm'` with `'piragi'`.

#### Scenario: Migration applies cleanly
- **WHEN** `alembic upgrade head` is run
- **THEN** the `projects` table has a `piragi_document_paths` column, no `notebooklm_notebook_id` column, and `icp_profiles.source` accepts `'piragi'`

### Requirement: AppSettings includes Piragi configuration
The system SHALL add `piragi_persist_dir: str = ".piragi"`, `piragi_default_top_k: int = 3`, `piragi_embedding_model: str = "all-mpnet-base-v2"`, and `piragi_chunk_strategy: str = "semantic"` to `AppSettings` in `app/config.py`. It SHALL remove `google_cloud_project`, `google_cloud_location`, `google_application_credentials`, and `notebooklm_storage_path`.

#### Scenario: Settings loaded from environment
- **WHEN** `PIRAGI_PERSIST_DIR=.piragi` and `PIRAGI_DEFAULT_TOP_K=5` are set in `.env`
- **THEN** `AppSettings.piragi_persist_dir` is `".piragi"` and `piragi_default_top_k` is `5`

### Requirement: Replace notebooklm_context with piragi_context in agent schemas
The system SHALL rename `notebooklm_context: str | None` to `piragi_context: str | None` on all agent input schemas: `ICPAgentInput`, `HookAgentInput`, `NarrativeAgentInput`, `RetentionAgentInput`, `CTAAgentInput`, `WriterAgentInput`.

#### Scenario: Agent input accepts piragi_context
- **WHEN** `HookAgentInput(icp=..., topic="...", target_format="VSL", piragi_context="Relevant hooks: ...")` is constructed
- **THEN** the input is valid and `piragi_context` contains the RAG-derived context

### Requirement: Orchestrator resolves Piragi context
The system SHALL update `PipelineOrchestrator._build_agent_inputs()` to check `project.piragi_document_paths`. If set, call `PiragiService.get_step_context(project_id, step_type)`. Include the result as `piragi_context` in the agent input. On error, log warning and set `piragi_context=None`. The `_resolve_notebooklm_context()` method SHALL be replaced with `_resolve_rag_context()`.

#### Scenario: Piragi context injected for hook step
- **WHEN** `run_step(project_id, StepType.HOOK)` is called and the project has `piragi_document_paths` set
- **THEN** the orchestrator queries Piragi for hook-related context and includes it in `HookAgentInput.piragi_context`

#### Scenario: Piragi unavailable — agent proceeds without context
- **WHEN** Piragi query raises an exception during `run_step`
- **THEN** a warning is logged, `piragi_context=None` is set, and the agent executes with raw notes only

### Requirement: Agent prompts include Piragi context
Each creative agent's `build_prompt()` SHALL include `"Relevant reference material:\n{piragi_context}"` in the prompt when `piragi_context` is not None. This replaces the previous `"Additional research context from NotebookLM:\n{notebooklm_context}"` pattern.

#### Scenario: Hook agent prompt includes RAG context
- **WHEN** `hook_agent.build_prompt(input_with_rag_context)` is called with `piragi_context="Example hooks: 1. What if..."`
- **THEN** the prompt contains "Relevant reference material:" followed by the RAG context

#### Scenario: Agent prompt works without RAG context
- **WHEN** `hook_agent.build_prompt(input_without_rag_context)` is called with `piragi_context=None`
- **THEN** the prompt does not include any RAG reference section — identical to pre-Piragi behavior
