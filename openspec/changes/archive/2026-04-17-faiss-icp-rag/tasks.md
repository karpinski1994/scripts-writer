## 1. Dependencies

- [x] 1.1 Install faiss-cpu: `uv add faiss-cpu`
- [x] 1.2 Install sklearn: `uv add scikit-learn`

## 2. Remove Piragi from ICP

- [x] 2.1 Remove piragi_context field from ICPAgentInput in `schemas/agents.py`
- [x] 2.2 Add faiss_context field to ICPAgentInput
- [x] 2.3 Remove piragi_service imports/calls from orchestrator.py (ICP step)
- [x] 2.4 Remove Piragi-related logic from ICP agent code

## 3. FAISS Service Module

- [x] 3.1 Create `backend/app/rag/faiss_service.py` with functions from dummyfiles:
  - `load_documents(docs_path: str)` - load all .txt files
  - `split_text(text, chunk_size=1000, chunk_overlap=200)` - chunk text
  - `create_index(documents, project_id: str)` - TF-IDF + FAISS index
  - `load_index(project_id: str)` - load persisted index
  - `search_project_documents(project_id: str, query: str, k=5)` - search
- [x] 3.2 Define `ICP_QUERY` constant from answer_generation.py
- [x] 3.3 Add persistence to `data/faiss_indexes/{project_id}/`
- [x] 3.4 Add index management functions:
  - `clear_index(project_id: str)` - delete single project index
  - `clear_all_indexes()` - delete all indexes
  - `list_indexed_projects()` - list projects with indexes

## 4. API Integration

- [x] 4.1 Modify `backend/app/api/icp.py` - `generate_icp` endpoint
- [x] 4.2 Handle case when index already exists (skip rebuild)

## 5. Orchestrator Integration

- [x] 5.1 Modify `backend/app/pipeline/orchestrator.py` - `_build_agent_inputs` for StepType.icp
- [x] 5.2 Add error handling - fallback to raw_notes if FAISS fails
- [x] 5.3 Import `faiss_service` module

## 6. Testing

- [ ] 6.1 Manual test: Upload ICP files via frontend
- [ ] 6.2 Manual test: Run ICP generation, verify FAISS index created
- [ ] 6.3 Verify retrieved chunks appear in LLM context
- [ ] 6.4 Verify ICP profile is generated correctly

## 7. Cleanup (optional)

- [ ] 7.1 Add explicit `/icp/ingest` endpoint for manual rebuild