## ADDED Requirements

### Requirement: Global Narrative FAISS Index Exists
The system SHALL maintain a FAISS index at `data/faiss_indexes/global_narratives/` containing all narrative templates and copywriting patterns from `backend/documents/narrative/`.

#### Scenario: Index creation
- **WHEN** `python backend/scripts/ingest_narrative_data.py` is executed
- **THEN** a FAISS index is created at `data/faiss_indexes/global_narratives/index.faiss` with metadata at `metadata.pkl`

#### Scenario: Index persistence
- **WHEN** the ingestion script runs multiple times
- **THEN** the index is replaced with updated content, maintaining the same directory structure

---

### Requirement: Narrative Context Retrieved via FAISS
When the Narrative Agent runs, the orchestrator SHALL retrieve narrative templates using FAISS search based on a query composed from project topic, draft excerpt, selected hook, and ICP profile.

#### Scenario: FAISS search retrieves relevant narratives
- **WHEN** user has generated ICP, added subject/draft, and selected a hook
- **AND** user clicks "Run Narrative Agent"
- **THEN** orchestrator constructs query from: topic + draft[:200] + selected_hook.text + ICP summary
- **AND** calls `search_global_documents("global_narratives", query, k=5)`
- **AND** passes retrieved chunks to NarrativeAgent via `piragi_context`

#### Scenario: No selected hook available
- **WHEN** user runs Narrative Agent without selecting a hook
- **THEN** query is composed from topic + draft + ICP summary (without hook text)
- **AND** FAISS search still returns relevant narratives

#### Scenario: No ICP available
- **WHEN** user runs Narrative Agent without generating ICP
- **AND** query is composed from topic + draft + (empty ICP)
- **THEN** FAISS search returns narratives based on topic and draft content

#### Scenario: FAISS index doesn't exist
- **WHEN** `global_narratives` index does not exist
- **THEN** orchestrator logs warning and uses empty narrative context
- **AND** Narrative Agent runs without RAG context

---

### Requirement: Narrative Query Composition
The system SHALL compose the FAISS query using available data from the pipeline context.

#### Scenario: Full query composition
- **WHEN** all data is available (topic, draft, hook, ICP)
- **THEN** query format is: `{topic} {draft[:200]} {hook_text} ICP: age={age}, pain_points={pain_pts}, desires={desires}`

#### Scenario: Partial query composition
- **WHEN** only topic and draft are available (no ICP, no hook)
- **THEN** query is: `{topic} {draft[:200]}`

#### Scenario: Minimal query composition
- **WHEN** only topic is available
- **THEN** query is: `{topic}`