## Context

Currently the Hook Agent in orchestrator.py reads hook documents directly from filesystem (`docs_base / "hooks"` and `playbooks_base / "hooks"`). This is similar to the old ICP approach - no semantic search, just reading files.

We already have FAISS RAG working for ICP (project-specific). Now we extend it for hooks using a global index (not project-specific).

## Goals / Non-Goals

**Goals:**
- Add global FAISS index for hook examples from `backend/documents/hook/`
- Create ingestion script to build global index (run manually when hooks are updated)
- Replace direct file reading with FAISS search in orchestrator Hook step
- Query using topic + draft + ICP to find best matching hooks

**Non-Goals:**
- No project-specific uploads for hooks (global only)
- No changes to frontend (hook-panel.tsx unchanged)
- No changes to hook generation logic in agent (just better context)

## Decisions

### 1. Global vs Project Index
**Decision:** Use separate global index for hooks
**Rationale:** Hooks are global best practices, not project-specific. Different from ICP which uses uploaded project files.

### 2. Query Composition
**Decision:** Query = `project.topic` + first 200 chars of `project.draft` + ICP summary
**Rationale:** Combines all available context to find most relevant hooks. ICP provides audience, draft provides content, topic provides subject.

### 3. When to Create Index
**Decision:** Manual ingestion script, not automatic
**Rationale:** Hook data changes infrequently. Manual run required when hooks are updated.

### 4. FAISS Service Extension
**Decision:** Add global functions to existing `faiss_service.py`
**Rationale:** Reuse existing TF-IDF + FAISS infrastructure, no new dependencies.

## Technical Details

### Ingestion Script
```python
# backend/scripts/ingest_hook_data.py
from app.rag.faiss_service import create_global_index

DOCS_PATH = "backend/documents/hook"
INDEX_NAME = "global_hooks"

def main():
    create_global_index(DOCS_PATH, INDEX_NAME)
```

### Query in Orchestrator
```python
# In _build_agent_inputs for StepType.hook
query = f"{project.topic} {project.draft[:200]} {icp_summary}"
hooks = search_global_documents("global_hooks", query, k=5)
```

### Data Location
- Source: `backend/documents/hook/` (e.g., "Best headlines .txt")
- Index: `backend/data/faiss_indexes/global_hooks/`

## Risks / Trade-offs

- [Risk] Hook index not created → [Mitigation] Document that script must be run first
- [Risk] Query not matching → [Mitigation] Can tune query composition later
- [Risk] No hooks data exists → [Mitigation] Use fallback to direct file reading if FAISS fails

## Migration Plan

1. Create `backend/scripts/ingest_hook_data.py`
2. Add global functions to `faiss_service.py`
3. Run ingestion script to create global index
4. Modify orchestrator to use FAISS for Hook step
5. Deploy

## Open Questions

1. **Ingestion frequency:** How often should hooks be re-ingested? (manual for now)
2. **Hook directory:** Use only `backend/documents/hook/` or also `documents/playbooks/hooks`?