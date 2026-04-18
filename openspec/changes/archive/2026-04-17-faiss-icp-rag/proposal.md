## Why

The current ICP agent in the pipeline (orchestrator.py) uses a simplistic "read only the first text file" approach when building input context from uploaded ICP documents. This misses valuable information from multiple uploaded files and provides poor context to the LLM, resulting in lower quality ICP profiles. Additionally, we have a custom FAISS-based RAG pipeline in `dummyfiles/` that we should integrate into the main application.

## What Changes

- Create new `backend/app/rag/faiss_service.py` implementing FAISS ingestion and retrieval per project
- Integrate FAISS retriever into orchestrator.py for ICP step (replacing first-file logic)
- Trigger FAISS ingestion when ICP generation is requested (per project, stored in `data/faiss_indexes/{project_id}/`)
- Remove Piragi completely from ICP pipeline. Add new `faiss_context` field to ICPAgentInput.
- Add FAISS index management functions: clear all, clear single project, list projects (for testing)

## Capabilities

### New Capabilities

- `faiss-icp-rag`: Custom FAISS-based RAG for ICP generation using TF-IDF vectorization. Per-project indexes stored in `data/faiss_indexes/{project_id}/`. Replaces simplistic first-file reading in orchestrator with semantic search over all uploaded documents.

### Modified Capabilities

- `icp-generation`: The existing ICP generation capability will now use FAISS-retrieved context instead of raw first-file reading. Requirements remain the same (generate ICP from context).

## Impact

Backend:
- New dependencies: `faiss-cpu`, `sklearn` (via uv)
- New module: `backend/app/rag/faiss_service.py`
- New field: `faiss_context` in `ICPAgentInput` (replace piragi_context)
- Modified: `backend/app/api/icp.py` (trigger ingestion on generate)
- Modified: `backend/app/pipeline/orchestrator.py` (use FAISS search)
- Remove: Piragi dependencies and references from ICP pipeline

Frontend: No changes required - existing ICP panel works with API response

Storage: New `data/faiss_indexes/{project_id}/` directory containing `.faiss` index and `.pkl` metadata