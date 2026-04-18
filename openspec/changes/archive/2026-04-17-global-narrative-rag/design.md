## Context

The Narrative Agent needs to retrieve narrative templates and copywriting patterns based on the user's context. Currently, the orchestrator reads files directly from `playbooks_base / "narrative_patterns"`. This doesn't provide intelligent matching - it just reads all files.

The goal is to implement a FAISS-based RAG system similar to what was done for the Hook Agent:
- Data is pre-loaded via ingestion script (no user uploads)
- Query is composed from: topic + draft + selected_hook.text + ICP demographics
- FAISS search returns the most relevant narrative templates

**Current State:**
- Hook Agent uses FAISS (global_hooks index) ✓
- Narrative Agent uses file reading ✗
- Source narrative files exist at `documents/playbooks/narrative_patterns/` (aida.txt, pas.txt, heroes_journey.txt)
- Need to create `backend/documents/narrative/` and copy templates

**Constraints:**
- Must use existing FAISS service (`backend/app/rag/faiss_service.py`) - already has `create_global_index` and `search_global_documents`
- Same chunking strategy as Hook (1000 chars, 200 overlap)
- Same TF-IDF vectorizer settings (5000 features, english stopwords, ngram 1-2)

## Goals / Non-Goals

**Goals:**
- Create global FAISS index for narrative documents at `data/faiss_indexes/global_narratives/`
- Modify orchestrator to use FAISS search instead of file reading for Narrative step
- Query composed from: project.topic + project.draft[:200] + selected_hook.text + ICP summary

**Non-Goals:**
- Do NOT modify NarrativeAgentInput schema (already has piragi_context)
- Do NOT create new API endpoints - ingestion is script-based only
- Do NOT add user upload functionality for narratives

## Decisions

1. **Source Directory**: Create `backend/documents/narrative/` and copy files from `documents/playbooks/narrative_patterns/`
   - Rationale: Keeps consistent pattern with hook (source in backend/documents/)

2. **Index Name**: `global_narratives`
   - Rationale: Consistent with `global_hooks` naming convention

3. **Query Composition**: Include selected_hook.text in addition to topic/draft/ICP
   - Rationale: The hook shapes how the narrative should flow - a provocative hook suggests different narrative structures than a story-based hook

4. **Chunk Size**: 1000 chars with 200 overlap (same as Hook)
   - Rationale: Narrative templates are longer documents, 1000 chars provides good context while maintaining relevance

## Risks / Trade-offs

- **[Risk]** Narrative templates might be too long for effective chunking → **Mitigation**: Adjust chunk size to 1500 if 1000 proves too small for template structures
- **[Risk]** ICP demographics might be empty (user didn't generate ICP) → **Mitigation**: Query works with partial data, FAISS will search with whatever is available
- **[Risk]** Selected hook might be None (user hasn't selected yet) → **Mitigation**: Handle None gracefully, use empty string in query