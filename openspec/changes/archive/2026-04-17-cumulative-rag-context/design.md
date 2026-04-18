## Context

The current Piragi RAG integration queries only ONE document category per step based on `STEP_CATEGORY_MAP`. Each step (ICP, Hook, Narrative, etc.) only sees its own category documents, missing cumulative context from earlier steps. The frontend has a global Documents button for uploading documents to any category.

The pipeline flow is:
1. **ICP** - Only sees ICP documents + notes
2. **Hook** - Only sees Hook documents + notes (not ICP)
3. **Narrative** - Only sees Narrative documents + notes (not ICP or Hook)
4. **Retention** - Only sees Retention documents + notes
5. **CTA** - Only sees CTA documents + notes
6. **Writer** - Gets full context from all previous steps

Goal: Each step should get cumulative context from all dependencies.

## Goals / Non-Goals

**Goals:**
- Each pipeline step queries cumulative documents based on step dependencies
- ICP step uses ICP documents only
- Hook step uses ICP + Hook documents
- Narrative/Retention/CTA steps use ICP + Hook + their own documents
- Developer-provided hardcoded templates for Narrative/Retention (no user uploads)
- Frontend: Dropzone only on pending step panel (ICP & Hook), fixed template selection for later steps

**Non-Goals:**
- Changing the existing document upload mechanism at the API level
- Adding new document categories beyond what's defined
- Runtime user template editing (templates are static .txt files)

## Decisions

### 1. STEP_DEPENDENCIES mapping

**Decision:** Define explicit step dependencies in `rag/config.py`.

```python
STEP_DEPENDENCIES: dict[StepType, list[StepType]] = {
    StepType.ICP: [StepType.ICP],
    StepType.HOOK: [StepType.ICP, StepType.HOOK],
    StepType.NARRATIVE: [StepType.ICP, StepType.HOOK],
    StepType.RETENTION: [StepType.ICP, StepType.HOOK],
    StepType.CTA: [StepType.ICP, StepType.HOOK],
    StepType.WRITER: [StepType.ICP, StepType.HOOK, StepType.NARRATIVE, StepType.RETENTION, StepType.CTA],
}
```

**Rationale:** Explicit dependencies are clearer than deriving them. Makes it easy to see exactly what each step gets. Alternative was dynamic derivation but harder to debug.

### 2. DEV_PROVIDED_CATEGORIES for hardcoded templates

**Decision:** Store dev-provided templates in `documents/narrative_patterns/` and `documents/retention_tactics/` as .txt files.

```python
DEV_PROVIDED_CATEGORIES: dict[StepType, list[str]] = {
    StepType.NARRATIVE: ["narrative_patterns"],
    StepType.RETENTION: ["retention_tactics"],
}
```

**Rationale:** Templates live in the same document folder structure as user uploads, making RAG querying uniform. Users can edit .txt files directly if needed.

### 3. Frontend panel design

**Decision:** 
- ICP & Hook panels: Show dropzone for document uploads
- Narrative & Retention panels: Show agent results first, then fixed template options (AIDA/PAS for Narrative; Curiosity Gap/Teasers for Retention)
- CTA panel: Show agent results first, then fixed template options (Subscribe/Buy)
- Each template option includes "why_best" explanation
- Dropzone only appears on the pending step panel, not as a global button

**Rationale:** Users should see agent-generated results first, then optionally choose from curated templates. Each template explains why it's best for specific use cases.

### 4.piragi_service.py get_step_context() changes

**Decision:** Iterate over STEP_DEPENDENCIES and DEV_PROVIDED_CATEGORIES, combining chunks.

```python
async def get_step_context(self, project_id: UUID, step_type: StepType) -> str | None:
    dependencies = STEP_DEPENDENCIES.get(step_type, [step_type])
    all_chunks = []
    for dep_step in dependencies:
        category = STEP_CATEGORY_MAP.get(dep_step, "icp")
        chunks = await piragi_manager.query(category, query, top_k=3)
        all_chunks.extend(chunks)
    if step_type in DEV_PROVIDED_CATEGORIES:
        for dev_category in DEV_PROVIDED_CATEGORIES[step_type]:
            dev_chunks = await piragi_manager.query(dev_category, query, top_k=3)
            all_chunks.extend(dev_chunks)
    return "\n\n".join(all_chunks) if all_chunks else None
```

**Rationale:** Each dependency category is queried separately and results combined. Keeps the query logic simple and maintains backward compatibility.

## Risks / Trade-offs

- **[Risk]** Empty cumulative context if no documents uploaded for earlier steps
  - **Mitigation:** Query returns empty list gracefully, not an error. Agent proceeds with just prompts/notes.

- **[Risk]** Large context payload for Writer step (5 categories × 3 chunks = 15 chunks)
  - **Mitigation:** Keep top_k small (3). Tokens are managed by the LLM client, not truncated here.

- **[Risk]** Templates become stale or don't fit user's niche
  - **Mitigation:** Templates are plain .txt files in `documents/` - users can edit directly.

- **[Risk]** Hardcoded template options limit flexibility
  - **Mitigation:** Start with 2 options per step. Can expand by adding more .txt files to the folder.