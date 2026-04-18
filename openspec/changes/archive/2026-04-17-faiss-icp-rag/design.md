## Context

The Scripts Writer backend has an ICP generation pipeline step. Currently in `orchestrator.py` `_build_agent_inputs` for `StepType.icp`, the code reads only the first file from project ICP documents (`files[:1]`) - this is a simplistic approach that misses information from multiple files.

We have a working FAISS RAG pipeline in `backend/dummyfiles/ingestion_pipeline.py` using TF-IDF vectorization that we should integrate.

## Goals / Non-Goals

**Goals:**
- Integrate FAISS RAG pipeline from dummyfiles into main app for ICP document retrieval
- Replace "first file only" logic with semantic search over ALL uploaded documents
- Per-project FAISS indexes stored in `data/faiss_indexes/{project_id}/`
- No frontend changes needed - existing API contract maintained

**Non-Goals:**
- Do NOT keep Piragi in ICP pipeline - we're removing it completely
- Do NOT add new database tables - flat file storage for FAISS indexes

## Decisions

### 1. Remove Piragi Completely
**Decision:** Remove all Piragi references from ICP pipeline.
**Rationale:** We're replacing the first-file approach with FAISS. No need for two retrieval systems. Add `faiss_context` field to replace `piragi_context`.

### 2. FAISS Service Location
**Decision:** Create `backend/app/rag/faiss_service.py` (not in existing `rag/` module)
**Rationale:** Keeps FAISS-specific logic separate from existing Piragi integration. New module avoids confusion between Piragi and FAISS.

### 2. When to Ingest
**Decision:** Ingest on `/icp/generate` request (not on every file upload)
**Rationale:** Uploads happen per-file. Ingesting every upload would rebuild index repeatedly. On-demand ingestion is simpler.

### 3. Query Strategy
**Decision:** Use exact query from `backend/dummyfiles/answer_generation.py`
**Rationale:** This query was crafted for ICP generation. Using the same query ensures consistent retrieval behavior.

### 4. Remove Piragi, Use FAISS Only
**Decision:** Completely remove Piragi from the project. Use FAISS as the ONLY retrieval system.
**Rationale:** We're replacing the simplistic first-file approach with FAISS RAG. Piragi is a separate system that we're not using for ICP. We will NOT keep piragi_context - we will add a new field or rename to be clear this is FAISS retrieval.

### 5. Storage Location
**Decision:** `backend/data/faiss_indexes/{project_id}/`
**Rationale:** Follows existing app pattern (data/ in backend). Separate from documents/ which holds user Uploaded files.

## Technical Details

### Dependencies
- `faiss-cpu` - FAISS without GPU support
- `sklearn` - Scikit-learn for TfidfVectorizer

### FAISS Service Functions
```python
def create_index(docs_path: str, project_id: str) -> None:
    """Load all .txt files, chunk, TF-IDF vectorize, create FAISS L2 index."""

def search_project_documents(project_id: str, query: str, k: int = 5) -> list[tuple]:
    """Load index, transform query, search, return top k chunks with metadata and distance."""
```

### Configuration (matching dummyfiles)
- `TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))`
- `chunk_size=1000`, `chunk_overlap=200`
- `faiss.IndexFlatL2`

### ICP Query
```
"form an icp (ideal customer profile) from all the documents take most common lead awarness levels, identities, pain points, goals, dreams, desires, internal conficts, doubts, enemies, external barriers, failed attempts, what did not work, the emotional drivers - why now, and what makes them buy and give me detailed report with quotes based on that"
```

### Index Management (for testing)
Add helper functions to manage FAISS indexes:
```python
def clear_index(project_id: str) -> None:
    """Delete FAISS index for a specific project."""

def clear_all_indexes() -> None:
    """Delete all FAISS indexes (testing)."""

def list_indexed_projects() -> list[str]:
    """List all projects with existing FAISS indexes."""
```

CLI aliases for convenience:
```bash
alias faiss-clear-all='rm -rf /Users/karpinski94/projects/scripts-writer/backend/data/faiss_indexes/'
alias faiss-clear-project='rm -rf /Users/karpinski94/projects/scripts-writer/backend/data/faiss_indexes/{project_id}/'
```

## Risks / Trade-offs

- [Risk] Index rebuild on every generate → [Mitigation] Check if index exists before creating; only rebuild if docs changed (future enhancement)
- [Risk] No index yet exists on first generate → [Mitigation] Create index on first generate, fallback to raw_notes if fails

## Open Questions

1. Should we add explicit `/icp/ingest` endpoint for manual rebuild?