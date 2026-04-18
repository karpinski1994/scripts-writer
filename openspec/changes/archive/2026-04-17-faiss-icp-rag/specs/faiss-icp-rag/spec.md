## ADDED Requirements

### Requirement: FAISS index creation per project
The system SHALL create a FAISS vector index per project when ICP generation is requested, using TF-IDF vectorization with the project's uploaded ICP documents.

#### Scenario: First-time ICP generation
- **WHEN** user triggers ICP generation for a project with uploaded documents and no existing FAISS index
- **THEN** the system creates a new FAISS index in `data/faiss_indexes/{project_id}/` containing all uploaded .txt documents

#### Scenario: Subsequent ICP generation
- **WHEN** user triggers ICP generation for a project with an existing FAISS index
- **THEN** the system uses the existing index (no rebuild) and retrieves relevant chunks

### Requirement: FAISS document ingestion
The system SHALL load all .txt files from the project's ICP documents directory, chunk them with 1000-character chunks and 200-character overlap, and index them using TfidfVectorizer with max_features=5000, stop_words="english", ngram_range=(1,2).

#### Scenario: Ingest multiple documents
- **WHEN** project has multiple uploaded .txt files in its ICP documents folder
- **THEN** all files are loaded, chunked, and indexed into a unified FAISS L2 index

### Requirement: FAISS similarity search
The system SHALL search the FAISS index using semantic similarity (L2 distance) and return the top k most similar document chunks to the query.

#### Scenario: Search with default k
- **WHEN** user triggers ICP generation without specifying k
- **THEN** the system returns the top 5 most similar chunks

#### Scenario: Search with custom k
- **WHEN** user triggers ICP generation with k=3
- **THEN** the system returns the top 3 most similar chunks

### Requirement: ICP query retrieval
The system SHALL use the exact retrieval query: "form an icp (ideal customer profile) from all the documents take most common lead awarness levels, identities, pain points, goals, dreams, desires, internal conficts, doubts, enemies, external barriers, failed attempts, what did not work, the emotional drivers - why now, and what makes them buy and give me detailed report with quotes based on that"

#### Scenario: Execute ICP query
- **WHEN** ICP generation is triggered
- **THEN** the system searches using the above query and returns relevant chunks

### Requirement: FAISS context to ICP agent
The system SHALL pass the retrieved document chunks (with source metadata and distance score) to the ICP agent via a new `faiss_context` field for generating the ICP profile.

#### Scenario: Pass FAISS context
- **WHEN** FAISS search returns chunks
- **THEN** chunks are formatted and passed via `faiss_context` field to the ICP agent

### Requirement: Clear single project index
The system SHALL allow deletion of a FAISS index for a specific project.

#### Scenario: Clear single project
- **WHEN** user requests to clear index for project "abc-123"
- **THEN** `data/faiss_indexes/abc-123/` is deleted

### Requirement: Clear all indexes
The system SHALL allow deletion of all FAISS indexes (for testing).

#### Scenario: Clear all indexes
- **WHEN** user requests to clear all indexes
- **THEN** `data/faiss_indexes/` directory is emptied

### Requirement: List indexed projects
The system SHALL list all projects that have existing FAISS indexes.

#### Scenario: List projects
- **WHEN** user requests list of indexed projects
- **THEN** system returns list of project IDs with indexes

### Requirement: Remove Piragi from ICP
The system SHALL remove all Piragi references from the ICP pipeline and replace with FAISS.

#### Scenario: No Piragi in ICP context
- **WHEN** ICP generation runs
- **THEN** No Piragi-related data is passed to the agent