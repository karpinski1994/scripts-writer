## Context

Phases 0–7 built the full pipeline: backend with all creative agents (ICP, Hook, Narrative, Retention, CTA, Writer), orchestrator with dependency resolution and downstream invalidation, WebSocket events, frontend with dashboard, agent panels, script editor, and export. The orchestrator's `_build_agent_inputs()` assembles context from upstream steps (e.g., ICP profile for Hook agent). There is no external data source integration — agents operate solely on user-provided raw notes and pipeline selections.

The existing `app/integrations/` directory does not exist. The `app/config.py` has `AppSettings` with LLM provider keys and general settings. The `Project` model in `app/db/models.py` has no `notebooklm_notebook_id` field. The `ICPProfile.source` CHECK constraint allows only `'generated'` and `'uploaded'`. Agent input schemas in `app/schemas/agents.py` have no `notebooklm_context` field.

## Goals / Non-Goals

**Goals:**
- Google Cloud Discovery Engine API client for NotebookLM operations
- Connect/disconnect NotebookLM notebooks to projects
- Query notebooks for step-relevant context before agent execution
- Inject NotebookLM context into creative agent prompts
- Frontend UI for notebook connection and context preview per step
- Graceful degradation when NotebookLM is unavailable

**Non-Goals:**
- Google Drive file browsing (future enhancement)
- NotebookLM notebook creation from within Scripts Writer
- Uploading sources to NotebookLM notebooks
- Caching NotebookLM query results (deferred)
- Analysis agents receiving NotebookLM context (Phase 9)
- OAuth browser-based auth flow (use service account key for v1)

## Decisions

### 1. Use official Google Cloud Discovery Engine API directly
**Choice:** Use `google-auth` for authentication and `httpx` for HTTP calls to the Discovery Engine API endpoint
**Alternative:** Use unofficial `notebooklm-py` library
**Rationale:** The official API is stable, documented, and supported by Google. Unofficial libraries may break. `google-auth` handles service account credentials natively. `httpx` is already available (used by LLM providers). Direct REST calls give us full control over error handling and don't add an extra dependency layer.

### 2. Service account authentication (not OAuth browser flow)
**Choice:** User provides a Google Cloud service account key file path in `.env`. The backend authenticates as the service account.
**Alternative:** OAuth 2.0 browser-based user authentication
**Rationale:** Single-user local app. Service account is simpler — no redirect URIs, no token refresh, no browser popup. The user creates a service account, grants it NotebookLM access, and provides the key file path. This matches the existing pattern of API keys in `.env`.

### 3. NotebookLM context as optional `notebooklm_context` field on agent inputs
**Choice:** Add `notebooklm_context: str | None = None` to each creative agent input schema. The orchestrator resolves it before building the prompt. The agent's `build_prompt()` includes it when present.
**Alternative:** Inject NotebookLM context into `raw_notes` field
**Rationale:** Explicit field is clearer. It separates the user's notes from external research. Agents can format the prompt differently for each source. When `None`, agents work exactly as before — zero breaking change.

### 4. Store notebook_id on project, not per step
**Choice:** A single `notebooklm_notebook_id` column on the `projects` table. One notebook per project.
**Alternative:** Allow different notebooks per pipeline step
**Rationale:** Simpler for v1. One notebook covers all research for a project. If the user wants different notebooks, they create different projects. Per-step notebook assignment can be added later without schema changes (just move the field to pipeline_steps).

### 5. Query NotebookLM synchronously during `_build_agent_inputs()`
**Choice:** The orchestrator queries the NotebookLM API synchronously (await) when building agent inputs. The query is step-specific (e.g., "What audience insights are relevant for an ICP profile about {topic}?").
**Alternative:** Pre-fetch all context on notebook connect
**Rationale:** Step-specific queries are more targeted and produce better context than a single bulk fetch. The query takes ~1-2 seconds which is negligible compared to LLM generation time (10-30s). Pre-fetching would be wasteful for steps the user may never run.

### 6. Frontend context section is collapsible within each agent panel
**Choice:** Each agent panel gets a collapsible "NotebookLM Context" section showing: connected notebook name, "Query for {step} insights" button, context preview text, "Include in generation" checkbox (default: checked).
**Alternative:** Separate NotebookLM panel alongside agent panels
**Rationale:** Context is per-step and per-agent. Showing it inline within the agent panel keeps the UX coherent. A separate panel would require switching context.

### 7. Graceful degradation — agents proceed without NotebookLM context
**Choice:** If NotebookLM is not connected, unavailable, or returns an error, the orchestrator sets `notebooklm_context = None` and agents proceed with raw notes only. No agent execution is blocked by NotebookLM failures.
**Alternative:** Block agent execution until NotebookLM query succeeds
**Rationale:** NotebookLM is an enhancement, not a requirement. The core pipeline must work without it. Network issues, API changes, or credential problems should never prevent script generation.

## Risks / Trade-offs

- **[Risk] Google Cloud Discovery Engine API is in Preview (Pre-GA)** → Mitigation: The API may change. Wrap all calls in `NotebookLMService` with clear error handling. Log API failures at WARNING level. The service layer abstraction makes it easy to adapt to API changes.

- **[Risk] Service account setup complexity for users** → Mitigation: Provide clear setup instructions in the settings UI. Link to Google Cloud console. The feature is entirely optional — users can skip it and use raw notes.

- **[Trade-off] Single notebook per project** → Limits flexibility but keeps schema and UX simple. Users with multiple notebooks can merge sources in NotebookLM before connecting.

- **[Trade-off] No query result caching** → Each agent run queries NotebookLM fresh. If the user re-runs an agent, it queries again. Caching could be added later but introduces staleness concerns.

- **[Trade-off] No streaming from NotebookLM** → The query endpoint returns a complete response, not streamed tokens. The context is injected into the agent prompt before LLM generation starts.
