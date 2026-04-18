## Why

The Hook Agent currently uses direct file reading to get hook examples, which doesn't leverage semantic search. We need to add global FAISS RAG similar to ICP but for hook examples - allowing retrieval of best-matching hooks based on ICP profile, draft, and subject context.

## What Changes

- Add global FAISS index for hook examples (separate from project-specific ICP index)
- Create ingestion script to load hook documents from `backend/documents/hook/`
- Modify orchestrator to use FAISS search for Hook step (not direct file reading)
- Query composed from: topic + draft excerpt + ICP profile

## Capabilities

### New Capabilities

- `global-hook-rag`: Global FAISS-based retrieval for Hook Agent. Uses pre-loaded hook documents from `backend/documents/hook/`, searches using topic+draft+ICP to find best matching hooks.

### Modified Capabilities

- `hook-generation`: Will now use FAISS-retrieved hook examples instead of direct file reading. Requirements remain the same (generate hooks).

## Impact

Backend:
- New: `backend/scripts/ingest_hook_data.py` - ingestion script
- New: `data/faiss_indexes/global_hooks/` - global FAISS index
- Modified: `backend/app/rag/faiss_service.py` - add global index functions
- Modified: `backend/app/pipeline/orchestrator.py` - use FAISS for Hook step

Frontend: No changes - hooks displayed in hook-panel.tsx (unchanged)