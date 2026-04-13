# Phase 8: Piragi RAG Integration — Design Document

## Phase Overview

Phase 8 integrates Piragi (a local RAG system) into the Scripts Writer pipeline. This enables users to connect their own documents—research notes, competitor analyses, audience surveys—and query them for relevant context at each pipeline step. The RAG context enriches agent prompts, producing more targeted outputs tailored to the user's specific domain knowledge.

The core value proposition is contextual awareness: instead of relying solely on the LLM's training data, agents can reference the user's connected documents to generate ICP profiles, hooks, narratives, and retention techniques that reflect actual market research and business context.

## Architecture Decisions

### Decision 1: Local RAG vs. Cloud RAG

| Factor | Local RAG (Piragi) | Cloud RAG (NotebookLM) |
|--------|-------------------|------------------------|
| Data privacy | All data stays on user's machine | Data sent to Google Cloud |
| Setup complexity | Requires Piragi installation | Requires Google Cloud credentials |
| Query latency | Local embedding model (fast) | API call to Discovery Engine |
| Cost | Free | Google Cloud API costs |
| Offline support | Works without internet | Requires internet |

**Choice**: Piragi. Rationale: aligns with the project's core value of local-first, private-by-default architecture. Users own their data, no cloud costs, no external dependencies beyond the embedding model.

### Decision 2: Document Categories

We map pipeline step types to document categories. This enables step-specific queries that return relevant context without loading all documents into a single index.

| Step Type | Document Category | Example Files |
|----------|-------------------|---------------|
| ICP | `icp/` | audience_research.json, competitor_analysis.md |
| Hook | `hooks/` | viral_hooks.md, hook_formulas.txt |
| Narrative | `narratives/` | story_templates.md, pas_examples.txt |
| Retention | `retention/` | retention_techniques.md |
| CTA | `cta/` | cta_formulas.md, urgency_examples.txt |
| Writer | (all above) | — |

**Choice**: Category-based separation. Rationale: each agent benefits from different source material. Querying the hooks category for ICP generation would return irrelevant results.

### Decision 3: Context Injection Strategy

We inject RAG context as a prompt section rather than as structured tool calls. This keeps the agent architecture simple and predictable.

```
User prompt:
---
[EXISTING PROMPT CONTENT]

Relevant reference material:
---
{RAG_CONTEXT_CHUNKS}
---
```

**Choice**: Prompt injection. Rationale: works with all LLM providers without requiring function calling support. The LLM naturally attends to the reference material section.

### Decision 4: Graceful Degradation

If Piragi fails (no documents connected, query returns empty, or Piragi service error), the system proceeds without RAG context. Agent prompts work identically to the pre-Piragi baseline.

**Choice**: Fail-open. Rationale: the core pipeline must always work. RAG is an enhancement, not a blocker.

## Data Flow

### Flow 1: Connect Documents to Project

```
Frontend                          Backend                         Piragi
   │                              │                               │
   │ POST /piragi/connect        │                               │
   │ {document_paths: "..."}     │                               │
   │────────────────────────────>│                               │
   │                            │ Validate project_id             │
   │                            │ Parse document_paths          │
   │                            │ ─────────────────────>        │
   │                            │                                │
   │                            │ Update project record:        │
   │                            │ piragi_document_paths = "..."│
   │                            │ ─────────────────────>        │
   │                            │ Save to DB                   │
   │                            │ ─────────────────────>        │
   │                            │                                │
   │ 200 {connected: true}       │                               │
   │<────────────────────────────│                               │
```

**Data persisted**: `projects.piragi_document_paths` = comma-separated document paths relative to project root.

### Flow 2: Query Documents at Pipeline Step

```
Orchestrator                     PiragiService                  Piragi
    │                              │                             │
    │ run_step(project_id, HOOK)   │                             │
    │────────────────────────────>│                             │
    │                            │ Get project.piragi_doc_paths │
    │                            │ ─────────────────────>      │
    │                            │                             │
    │                            │ Check: paths is not None     │
    │                            │ ─────────────────────>      │
    │                            │                             │
    │                            │ Query(                      │
    │                            │   category="hooks",        │
    │                            │   query="effective hooks", │
    │                            │   top_k=3                   │
    │                            │ ─────────────────────>      │
    │                            │                             │
    │                            │            [chunks returned]│
    │                            │<───────────────────────────── │
    │                            │                             │
    │                            │ Join chunks with newlines    │
    │                            │ ─────────────────────>      │
    │ piragi_context = "..."       │                             │
    │<────────────────────────────│                             │
    │                            │                             │
    │ Inject into HookAgentInput   │                             │
    │ piragi_context = "..."     │                             │
    │ ─────────────────────>     │                             │
```

**Context format**: All returned chunks joined with double newlines, preserving source attribution in the chunk metadata.

### Flow 3: Agent Execution with RAG Context

```
HookAgent                      LLMProvider
    │                            │
    │ build_prompt(inputs)       │
    │  ├─ icp_summary           │
    │  ├─ topic                │
    │  ├─ target_format       │
    │  └─ piragi_context       │─────── INJECTED HERE
    │ ────────────────────>    │
    │                         │
    │ "Generate hooks for      │
    │  {topic} based on       │
    │  {icp_summary}.         │
    │                        │
    │ Relevant reference     │
    │ material:              │
    │ {piragi_context}"      │
    │ ──────────────────────>│
    │                        │
    │ [streaming tokens]    │
    │<───────────────────────│
```

## API Design

### Endpoints Added

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/projects/{id}/piragi/documents` | List available document categories and file counts |
| POST | `/api/v1/projects/{id}/piragi/connect` | Connect document paths to project |
| DELETE | `/api/v1/projects/{id}/piragi/connect` | Disconnect documents from project |
| POST | `/api/v1/projects/{id}/piragi/query` | Query connected documents for insights |

### GET /piragi/documents

**Response (200)**:
```json
{
  "categories": [
    {"category": "icp", "file_count": 3, "path": "documents/icp"},
    {"category": "hooks", "file_count": 5, "path": "documents/hooks"}
  ]
}
```

**Behavior**: Scans the directory structure under each configured category path. Returns file counts for each category found.

### POST /piragi/connect

**Request**:
```json
{
  "document_paths": "documents/icp,documents/hooks"
}
```

**Response (200)**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_paths": "documents/icp,documents/hooks",
  "connected": true
}
```

**Validation**: Paths must be non-empty strings, comma-separated if multiple. Each path must exist in the project directory or be a valid absolute path.

### POST /piragi/query

**Request**:
```json
{
  "query": "audience pain points for mid-level engineers",
  "step_type": "icp"
}
```

**Response (200)**:
```json
{
  "query": "audience pain points for mid-level engineers",
  "results": [
    {"chunk": "Mid-level engineers struggle with...", "source": "documents/icp/survey.md", "relevance": 0.92},
    {"chunk": "They want efficiency over...", "source": "documents/icp/interviews.txt", "relevance": 0.87}
  ]
}
```

**Behavior**: Maps `step_type` to category via `STEP_CATEGORY_MAP`, queries Piragi, returns top results with source and relevance scores.

## Database Changes

### Column Added

```sql
ALTER TABLE projects
ADD COLUMN piragi_document_paths VARCHAR(500);
```

**Rationale**: Stores comma-separated paths to connected document directories. Nullable (null means no documents connected).

### Column Dropped

```sql
ALTER TABLE projects
DROP COLUMN notebooklm_notebook_id;
```

**Rationale**: Replaced by Piragi; NotebookLM integration removed per the migration from NotebookLM to Piragi.

### CHECK Constraint Update

```sql
ALTER TABLE icp_profiles
DROP CONSTRAINT icp_profiles_source_check;

ALTER TABLE icp_profiles
ADD CONSTRAINT icp_profiles_source_check CHECK (
  source IN ('generated', 'uploaded', 'piragi')
);
```

**Rationale**: Replace 'notebooklm' with 'piragi' in allowed ICP source values.

## Integration Points

### Integration 1: Pipeline Orchestrator

The orchestrator's `_build_agent_inputs()` method is updated to resolve RAG context:

```python
async def _build_agent_inputs(self, project_id: UUID, step_type: StepType) -> BaseModel:
    # ... existing input assembly ...

    if self.piragi_service:
        project = await self._get_project(project_id)
        if project.piragi_document_paths:
            piragi_context = await self.piragi_service.get_step_context(
                project_id, step_type
            )
            if piragi_context:
                inputs.piragi_context = piragi_context

    return inputs
```

**Error handling**: If `get_step_context()` raises an exception, log a warning and set `piragi_context = None`. Do not propagate the error.

### Integration 2: Agent Input Schemas

Each creative agent input schema receives a new optional field:

```python
class HookAgentInput(BaseModel):
    icp: ICPProfile
    topic: str
    target_format: str
    content_goal: str | None = None
    piragi_context: str | None = None  # NEW FIELD
```

**Updated schemas**: ICPAgentInput, HookAgentInput, NarrativeAgentInput, RetentionAgentInput, CTAAgentInput, WriterAgentInput.

### Integration 3: Agent Prompt Templates

Each agent's `build_prompt()` method is updated to conditionally include RAG context:

```python
def build_prompt(self, inputs: HookAgentInput) -> str:
    prompt = f"""Based on the following ICP and topic, generate hooks..."""
    # ... existing prompt content ...

    if inputs.piragi_context:
        prompt += f"\n\nRelevant reference material:\n{inputs.piragi_context}"

    return prompt
```

## Frontend Changes

### New Components

1. **PiragiConnectPanel** (`frontend/src/components/piragi/piragi-connect-panel.tsx`)

   - Document path input with folder picker
   - Connect/Disconnect button
   - Connected documents display with file counts
   - Status indicator (connected/disconnected)

2. **PiragiContextPreview** (`frontend/src/components/piragi/piragi-context-preview.tsx`)

   - Shows "RAG context available" indicator on agent panels
   - Expandable preview of current context chunks
   - "Query for insights" button
   - Checkbox to include/exclude from agent run

3. **PiragiQueryModal** (`frontend/src/components/piragi/piragi-query-modal.tsx`)

   - Query input field
   - Step type selector
   - Results display with source and relevance
   - "Copy to clipboard" button

### Updated Agent Panels

Each agent panel (ICP, Hook, Narrative, Retention, CTA) receives a "RAG Context" section:

```
┌──────────────────────────────────────┐
│  [Existing agent panel content]      │
│──────────────────────────────────────│
│  RAG Context                        │
│  ☑ Include in agent run             │
│  📂 Connected: 3 files            │
│  [Query for insights]              │
│                                    │
│  Preview:                         │
│  • "Mid-level engineers struggle..." │
│  • "They want efficiency..."       │
│──────────────────────────────────────│
│  [Continue / Approve]             │
└──────────────────────────────────────┘
```

### State Management

New Zustand store for Piragi state:

```typescript
interface PiragiStore {
  connectedPaths: string | null;
  stepContexts: Record<string, string>;
  isQuerying: boolean;

  setConnectedPaths: (paths: string | null) => void;
  setStepContext: (stepType: string, context: string) => void;
  clearStepContext: (stepType: string) => void;
  setIsQuerying: (querying: boolean) => void;
}
```

## Sequence Diagram: Full RAG-Enabled Pipeline

```
User         Frontend         Backend         Orchestrator     PiragiService      Piragi       ICPAgent    Modal
  │              │               │               │               │               │             │           │         │
  │  Click "Connect Documents"│            │               │               │             │           │         │
  │─────────────>│               │               │               │               │             │           │         │
  │              │ POST /piragi/connect│             │               │             │           │         │
  │              │─────────────────>│               │               │             │           │         │
  │              │               │ Update DB     │               │             │           │         │
  │              │               │───────────────>│               │             │           │         │
  │              │               │               │               │             │           │         │
  │ 200 {connected: true}        │               │               │             │           │         │
  │<────────────────────────────│               │               │             │           │         │
  │              │               │               │               │             │           │         │
  │  Click "Run ICP"             │               │               │             │           │         │
  │─────────────>│               │               │               │             │           │         │
  │              │ POST /pipeline/run/icp       │               │             │           │         │
  │              │─────────────────>│           │               │             │           │         │
  │              │               │─────────────>│               │             │           │         │
  │              │               │               │ Get step context             │           │         │
  │              │               │               │─────────────────────────────>│           │         │
  │              │               │               │               │ Query("icp", "ICP insights"│           │         │
  │              │               │               │               │───────────────────────>│           │
  │              │               │               │               │              [chunks]    │           │
  │              │               │               │               │<───────────────────────│           │
  │              │               │               │ Join chunks   │               │             │           │
  │              │               │               │─────────────────────────────>│           │         │
  │              │               │               │ Build input with context     │           │         │
  │              │               │               │─────────────────────────────>│           │         │
  │              │               │               │               │              execute() │           │
  │              │               │               │               │───────────────────────>│           │
  │              │               │               │               │              "Generate ICP│
  │              │               │               │               │                  with ref..."│          │
  │              │               │               │               │─────────────────────────────────>│         │
  │  WS: streaming│               │               │               │              [tokens]  │           │
  │<────────────────────────────│               │               │               │<───────────────────────│           │
  │              │               │               │               │               │             │           │         │
  │  ICP displayed with RAG context│            │               │               │             │           │         │
  │<─────────────│               │               │               │             │           │         │
```

## Error Handling

### Error Scenario 1: No Documents Connected

When `project.piragi_document_paths` is null, skip all RAG operations:

```python
async def get_step_context(self, project_id: UUID, step_type: StepType) -> str | None:
    project = await self._get_project(project_id)
    if not project.piragi_document_paths:
        return None
    # ... proceed with query ...
```

### Error Scenario 2: Category Directory Empty

When a category folder has no files, return empty list without error:

```python
async def query(self, category: str, query: str, top_k: int = 3) -> list[str]:
    category_path = self.persist_dir / category
    if not category_path.exists() or not list(category_path.iterdir()):
        return []
    # ... proceed with embedding and search ...
```

### Error Scenario 3: Piragi Service Failure

Catch all exceptions, log warning, return None:

```python
async def get_step_context(self, project_id: UUID, step_type: StepType) -> str | None:
    try:
        # ... query logic ...
    except Exception as e:
        logger.warning(
            "piragi_query_failed",
            project_id=str(project_id),
            step_type=step_type.value,
            error=str(e)
        )
        return None
```

**Rationale**: Pipeline must never fail due to RAG issues. The user can still generate content without RAG context.

## Testing Strategy

### Unit Tests

1. **PiragiService.connect_documents()**

   - Test: persists document paths to project
   - Test: updates existing paths
   - Test: handles empty paths

2. **PiragiService.get_step_context()**

   - Test: returns None when no paths connected
   - Test: returns None when category empty
   - Test: returns joined chunks
   - Test: returns None on Piragi error

3. **Orchestrator with RAG**

   - Test: injects context when documents connected
   - Test: skips context when no documents
   - Test: handles Piragi error gracefully

### Integration Tests

1. **Full RAG flow**

   - Create project → connect documents → run ICP → verify output includes RAG-derived content

2. **Query endpoint**

   - POST /piragi/query → verify results format

3. **Disconnect flow**

   - Connect documents → disconnect → verify paths cleared → run agent works without RAG

## Security Considerations

### Data Exposure

RAG queries operate on user-provided documents stored locally. No data leaves the user's machine. The embedding model runs locally via Piragi.

### Path Validation

Document paths must be validated to prevent directory traversal attacks:

```python
def validate_path(path: str) -> bool:
    resolved = Path(path).resolve()
    # Block paths outside project root or absolute paths to sensitive locations
    return not resolved.is_absolute() or resolved.exists()
```

### API Access

Piragi endpoints inherit the same access controls as other project endpoints. No additional authentication required (single-user app).

## Performance Considerations

### Embedding Latency

Local embedding models (e.g., all-MiniLM-L6-v2) process documents in milliseconds. Query latency is dominated by disk I/O for loading the FAISS index.

### Caching Strategy

We do not cache RAG query results. Each pipeline step may benefit from different queries, and the document corpus changes infrequently. Users can reconnect documents to force re-indexing.

### Index Size

For typical user document volumes (MB-scale), the FAISS index fits in memory. No special optimization required for v1.

## Migration from NotebookLM

The Phase 8 design explicitly replaces the NotebookLM integration documented in the archive. This migration involves:

1. Dropping `notebooklm_notebook_id` from projects
2. Adding `piragi_document_paths` to projects
3. Replacing 'notebooklm' with 'piragi' in ICP source CHECK constraint
4. Updating frontend components to show Piragi instead of NotebookLM
5. Updating orchestrator to resolve Piragi context instead of NotebookLM context

Existing projects with NotebookLM connections will have their connections cleared during migration. Users must reconnect via Piragi.