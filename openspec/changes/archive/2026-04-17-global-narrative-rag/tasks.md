## 1. Prepare Narrative Source Data

- [x] 1.1 Create directory `backend/documents/narrative/` if it doesn't exist
- [x] 1.2 Copy narrative templates from `documents/playbooks/narrative_patterns/*.txt` to `backend/documents/narrative/`
- [x] 1.3 Verify files exist: aida.txt, pas.txt, heroes_journey.txt

## 2. Create Ingestion Script

- [x] 2.1 Create `backend/scripts/ingest_narrative_data.py` based on existing `ingest_hook_data.py` pattern
- [x] 2.2 Use source path: `backend/documents/narrative/`
- [x] 2.3 Use index name: `global_narratives`
- [x] 2.4 Set index output: `data/faiss_indexes/global_narratives/`

## 3. Run Ingestion

- [x] 3.1 Execute `python backend/scripts/ingest_narrative_data.py`
- [x] 3.2 Verify index created at `data/faiss_indexes/global_narratives/index.faiss`
- [x] 3.3 Verify metadata at `data/faiss_indexes/global_narratives/metadata.pkl`

## 4. Update Orchestrator

- [x] 4.1 Locate `StepType.narrative` block in `backend/app/pipeline/orchestrator.py`
- [x] 4.2 Replace file reading logic with FAISS search using `search_global_documents`
- [x] 4.3 Implement query composition: topic + draft[:200] + selected_hook.text + ICP summary
- [x] 4.4 Pass retrieved chunks to `NarrativeAgentInput` via `piragi_context`
- [x] 4.5 Handle edge cases: no hook selected, no ICP, index not found

## 5. Testing

- [x] 5.1 Verify orchestrator imports `search_global_documents` correctly
- [x] 5.2 Run backend and test Narrative agent execution via API
- [x] 5.3 Check logs for FAISS retrieval (should show "FAISS retrieved X narrative examples")
- [x] 5.4 Verify generated narratives include context from retrieved templates