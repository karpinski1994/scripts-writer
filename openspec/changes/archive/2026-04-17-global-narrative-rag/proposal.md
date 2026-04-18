## Why

The Narrative Agent currently relies on static file reading from playbook directories to get narrative templates and copywriting patterns. This doesn't allow for intelligent retrieval based on the user's specific context (ICP, draft, selected hook). We need a FAISS-based RAG system for the Narrative step that retrieves the most relevant narrative templates and examples based on the generated script's characteristics.

## What Changes

1. **Create narrative source directory**: Set up `backend/documents/narrative/` with narrative templates (copy from `documents/playbooks/narrative_patterns/`)
2. **Create ingestion script**: `backend/scripts/ingest_narrative_data.py` to build FAISS index from narrative documents
3. **Update orchestrator**: Replace file-based narrative context retrieval with FAISS search using query composed from topic, draft, selected hook, and ICP
4. **Run ingestion**: Execute script to create `data/faiss_indexes/global_narratives/` index

## Capabilities

### New Capabilities
- `global-narrative-rag`: Global FAISS RAG system for Narrative Agent that retrieves best-matching narrative templates and copywriting patterns based on ICP profile, draft content, and selected hook

### Modified Capabilities
- None - this extends the existing FAISS integration pattern (similar to global-hook-rag)

## Impact

- **New Files**: `backend/scripts/ingest_narrative_data.py`, `backend/documents/narrative/*.txt`
- **Modified Files**: `backend/app/pipeline/orchestrator.py` (narrative step)
- **Data Location**: `backend/data/faiss_indexes/global_narratives/`
- **Dependencies**: Requires `faiss-cpu`, `scikit-learn` (already installed for hook RAG)