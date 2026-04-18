## ADDED Requirements

### Requirement: Global FAISS index creation for hooks
The system SHALL create a global FAISS vector index for hook examples when ingestion script is run, using TF-IDF vectorization with hook documents from `backend/documents/hook/`.

#### Scenario: Create global hooks index
- **WHEN** admin runs `python backend/scripts/ingest_hook_data.py`
- **THEN** system creates FAISS index in `data/faiss_indexes/global_hooks/`

### Requirement: Hook document ingestion
The system SHALL load all .txt files from `backend/documents/hook/`, chunk them with 1000-character chunks and 200-character overlap, and index using TfidfVectorizer with max_features=5000, stop_words="english", ngram_range=(1,2).

#### Scenario: Ingest multiple hook documents
- **WHEN** ingestion script runs with multiple .txt files in hook directory
- **THEN** all files are loaded, chunked, and indexed into unified FAISS L2 index

### Requirement: Global hook search
The system SHALL search the global FAISS index using semantic similarity (L2 distance) and return the top k most similar hook examples to the query.

#### Scenario: Search global hooks index
- **WHEN** Hook agent runs with query "earn dollars remote work"
- **THEN** system returns top 5 most similar hook examples from global index

### Requirement: Query composition for hooks
The system SHALL compose search query from: project topic + first 200 characters of project draft + ICP profile summary.

#### Scenario: Compose hook query
- **WHEN** orchestrator builds Hook agent input
- **THEN** query combines topic, draft excerpt, and ICP summary for FAISS search

### Requirement: Retrieved hooks to agent
The system SHALL pass the retrieved hook examples (with source metadata and distance score) to the Hook agent as context for generating hooks.

#### Scenario: Pass retrieved hooks context
- **WHEN** FAISS search returns hook chunks
- **THEN** chunks are formatted and passed to Hook agent via context