## 1. Ingestion Script

- [x] 1.1 Create `backend/scripts/ingest_hook_data.py` script
- [x] 1.2 Import `create_global_index` from faiss_service
- [x] 1.3 Set docs path to `backend/documents/hook/`
- [x] 1.4 Set index name to `global_hooks`
- [x] 1.5 Test script: run `python backend/scripts/ingest_hook_data.py`

## 2. FAISS Service Updates

- [x] 2.1 Add `create_global_index(docs_path, index_name)` function
- [x] 2.2 Add `search_global_documents(index_name, query, k=5)` function
- [x] 2.3 Use same TF-IDF config as ICP (max_features=5000, stop_words="english", ngram_range=(1,2))
- [x] 2.4 Persist to `data/faiss_indexes/{index_name}/`

## 3. Orchestrator Integration

- [x] 3.1 Modify `_build_agent_inputs` for `StepType.hook`
- [x] 3.2 Remove direct file reading from `docs_base / "hooks"`
- [x] 3.3 Add FAISS search using `search_global_documents`
- [x] 3.4 Compose query: topic + draft[:200] + ICP summary
- [x] 3.5 Pass retrieved hooks to agent via context field

## 4. Initial Data

- [x] 4.1 Ensure `backend/documents/hook/` has hook files
- [x] 4.2 Run ingestion script to create global index
- [x] 4.3 Verify `data/faiss_indexes/global_hooks/` created

## 5. Testing

- [ ] 5.1 Manual test: Run Hook agent via UI
- [ ] 5.2 Verify FAISS search logs in orchestrator
- [ ] 5.3 Verify retrieved hooks appear in LLM context
- [ ] 5.4 Verify hooks are generated correctly