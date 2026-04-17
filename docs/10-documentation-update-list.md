Plan: Add draft as Primary Source to All Creative Agents (except ICP)
Core Principle
Draft is the PRIMARY source of truth — it contains the actual content the user wrote. Everything else (ICP, hook, narrative, etc.) is auxiliary context that shapes and enhances how the draft is used. This needs to be communicated to agents both in:
1. SYSTEM_PROMPT — tells the agent its role and priorities
2. build_prompt() — positions draft FIRST and labels it as primary
Bug: Global Documents Folder Paths
The orchestrator reads playbook references from documents/playbooks/ which doesn't exist. The actual global documents are at:
- documents/hooks/Best headlines .txt (HookAgent)
- documents/narrative_patterns/aida.txt, pas.txt, heroes_journey.txt
- documents/retention_tactics/teasers.txt, curiosity_gap.txt
Currently only the HookAgent reads from the correct global path (after our earlier fix). Narrative and Retention agents still reference playbooks_base / "narratives" and playbooks_base / "retention" which points to a non-existent documents/playbooks/ directory.

so move /Users/karpinski94/projects/scripts-writer/documents/narrative_patterns to /Users/karpinski94/projects/scripts-writer/documents/playbooks/narrative_patterns
  and /Users/karpinski94/projects/scripts-writer/documents/retention_tactics to
/Users/karpinski94/projects/scripts-writer/documents/playbooks/retention_tactics

Step-by-Step Changes
Step 1: backend/app/schemas/agents.py — Add draft field to 4 input schemas
1a. NarrativeAgentInput (line 32-37): Add draft: str | None = None
class NarrativeAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    topic: str
    target_format: str
    draft: str | None = None          # NEW
    piragi_context: str | None = None
1b. RetentionAgentInput (line 51-56): Add draft: str | None = None
class RetentionAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    target_format: str
    draft: str | None = None          # NEW
    piragi_context: str | None = None
1c. CTAAgentInput (line 70-76): Add draft: str | None = None
class CTAAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    content_goal: str | None = None
    cta_purpose: str | None = None
    draft: str | None = None          # NEW
    piragi_context: str | None = None
1d. WriterAgentInput (line 91-101): Add draft: str | None = None alongside existing raw_notes
class WriterAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    selected_retention: RetentionTechnique | list[RetentionTechnique] | None = None
    selected_cta: CTASuggestion
    topic: str
    target_format: str
    content_goal: str | None = None
    draft: str | None = None          # NEW - primary source
    raw_notes: str = ""               # KEEP - auxiliary
    piragi_context: str | None = None
Rationale: WriterAgent keeps both draft and raw_notes because raw_notes is the original user input (shorter, initial), while draft is the refined content from the Subject step. Both are useful but draft is primary.
---
Step 2: backend/app/agents/hook_agent.py — Emphasize draft as primary
2a. SYSTEM_PROMPT (line 14-19): Rewrite to emphasize draft as primary
Change from:
"You are an expert copywriter specializing in attention-grabbing hooks... "
"Given an Ideal Customer Profile (ICP), topic, draft of the content, format, and goal..."
To:
"You are an expert copywriter specializing in attention-grabbing hooks for video and marketing content. "
"The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message and content the user wants to convey. "
"All other data (ICP, topic, format, goal) is auxiliary context to shape HOW hooks are crafted, not WHAT they're about. "
"Generate multiple hook options in JSON format. "
"Output ONLY valid JSON: hooks[hook_type, text, reasoning], confidence (0.0-1.0). "
"Vary the hook types (question, shock, story, statistic, etc.). Hooks must resonate with the draft's core message."
2b. build_prompt() (line 31-43): Position draft FIRST with emphasis label
Change from:
parts = [
    f"ICP Summary:\n{icp.model_dump_json(indent=2)}",
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
]
if input_data.content_goal:
    parts.append(f"Content Goal: {input_data.content_goal}")
if input_data.draft:
    parts.append(f"Draft/Content Notes:\n{input_data.draft}")
To:
parts = []
if input_data.draft:
    parts.append(
        "=== PRIMARY SOURCE (Draft/Content) — This is your most important reference. "
        "Base hooks on THIS content above all else. ===\n"
        f"{input_data.draft}"
    )
parts.extend([
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
    f"ICP Summary (auxiliary — shapes HOW to hook, not WHAT about):\n{icp.model_dump_json(indent=2)}",
])
if input_data.content_goal:
    parts.append(f"Content Goal: {input_data.content_goal}")
---
Step 3: backend/app/agents/narrative_agent.py — Add draft as primary
3a. SYSTEM_PROMPT (line 14-17): Add draft emphasis
Change to:
"You are an expert storytelling consultant. "
"The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message the user wants to convey. "
"All other data (ICP, hook, topic, format) is auxiliary context to shape which narrative patterns best serve the content. "
"Generate narrative patterns in JSON. "
"Output ONLY valid JSON: patterns[pattern_name, description, structure], confidence(0.0-1.0). "
"Each pattern must align with the draft's core message and naturally carry its content."
3b. build_prompt() (line 29-38): Add draft first
Change from:
parts = [
    f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
]
To:
parts = []
if input_data.draft:
    parts.append(
        "=== PRIMARY SOURCE (Draft/Content) — Base narrative patterns on THIS content above all else. ===\n"
        f"{input_data.draft}"
    )
parts.extend([
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
    f"ICP Summary (auxiliary):\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook (auxiliary):\n{input_data.selected_hook.model_dump_json(indent=2)}",
])
---
Step 4: backend/app/agents/retention_agent.py — Add draft as primary
4a. SYSTEM_PROMPT (line 13-18): Add draft emphasis
Change to:
"You are an expert in audience retention techniques for video and marketing content. "
"The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual content the user wants to deliver. "
"All other data (ICP, hook, narrative, format) is auxiliary context to shape WHERE and HOW to apply retention. "
"Generate retention technique options that will keep the audience engaged throughout. "
"Consider open loops, pattern interrupts, curiosity gaps, and other proven retention methods. "
"Specify where each technique should be placed in the script. "
"Retention techniques must feel natural within the draft's flow, not forced."
4b. build_prompt() (line 31-40): Add draft first
Change from:
parts = [
    f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
    f"Target Format: {input_data.target_format}",
]
To:
parts = []
if input_data.draft:
    parts.append(
        "=== PRIMARY SOURCE (Draft/Content) — Base retention placement on THIS content's flow. ===\n"
        f"{input_data.draft}"
    )
parts.extend([
    f"Target Format: {input_data.target_format}",
    f"ICP Summary (auxiliary):\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook (auxiliary):\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative (auxiliary):\n{input_data.selected_narrative.model_dump_json(indent=2)}",
])
---
Step 5: backend/app/agents/cta_agent.py — Add draft as primary
5a. SYSTEM_PROMPT (line 13-19): Add draft emphasis
Change to:
"You are an expert in calls-to-action (CTAs) for video and marketing content. "
"The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message the user wants to convey. "
"All other data (ICP, hook, narrative, CTA purpose) is auxiliary context to shape the CTA. "
"The CTA purpose is the highest-priority instruction and defines the exact action the audience should take. "
"Every CTA must clearly drive that action and must not substitute a different conversion goal. "
"The CTA should feel like a natural next step after the draft's content, not an interruption. "
"Consider the ICP's objections and motivations. Vary CTA types (direct, soft, urgency, value-driven)."
5b. build_prompt() (line 32-57): Add draft after CTA purpose, before auxiliary data
Change from:
parts = []
if input_data.cta_purpose:
    parts.append("Primary CTA Goal...")
...
parts.extend([
    f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
])
if input_data.content_goal:
    parts.append(f"Content Goal (secondary context): {input_data.content_goal}")
To:
parts = []
if input_data.cta_purpose:
    parts.append("Primary CTA Goal (most important instruction)...")
else:
    parts.append("Primary CTA Goal (most important instruction)...")
if input_data.draft:
    parts.append(
        "=== PRIMARY SOURCE (Draft/Content) — The CTA must feel like a natural next step from THIS content. ===\n"
        f"{input_data.draft}"
    )
parts.extend([
    f"ICP Summary (auxiliary):\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook (auxiliary):\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative (auxiliary):\n{input_data.selected_narrative.model_dump_json(indent=2)}",
])
if input_data.content_goal:
    parts.append(f"Content Goal (secondary context): {input_data.content_goal}")
---
Step 6: backend/app/agents/writer_agent.py — Add draft as primary, demote raw_notes
6a. SYSTEM_PROMPT (line 13-20): Rewrite to emphasize draft
Change from:
"You are an expert scriptwriter... "
"Given an ICP, selected hook, narrative pattern, retention techniques, and CTA, "
"write a complete script... "
"Include the raw notes as source material to incorporate key details."
To:
"You are an expert scriptwriter for video and marketing content. "
"The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message and content the user wants in the script. "
"All other data (ICP, hook, narrative, retention, CTA) is auxiliary — it shapes HOW the script is structured and styled, "
"but the draft's content MUST be the foundation. "
"Write a complete script that weaves all elements together into a compelling piece. "
"The script should feel natural and persuasive, not formulaic. "
"Adapt the tone and language style to the ICP profile. "
"The draft's key points and message must be preserved and enhanced, not replaced."
6b. build_prompt() (line 32-56): Position draft FIRST
Change from:
parts = [
    f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
    f"Selected Retention Technique(s):\n{retention_json}",
    f"Selected CTA:\n{input_data.selected_cta.model_dump_json(indent=2)}",
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
]
if input_data.content_goal:
    parts.append(f"Content Goal: {input_data.content_goal}")
if input_data.raw_notes:
    parts.append(f"Raw Notes:\n{input_data.raw_notes}")
To:
parts = []
if input_data.draft:
    parts.append(
        "=== PRIMARY SOURCE (Draft/Content) — This is the MOST IMPORTANT input. "
        "The script MUST be built on this content. All other data shapes HOW, not WHAT. ===\n"
        f"{input_data.draft}"
    )
parts.extend([
    f"Topic: {input_data.topic}",
    f"Target Format: {input_data.target_format}",
    f"ICP Summary (auxiliary — shapes tone and style):\n{input_data.icp.model_dump_json(indent=2)}",
    f"Selected Hook (auxiliary):\n{input_data.selected_hook.model_dump_json(indent=2)}",
    f"Selected Narrative (auxiliary):\n{input_data.selected_narrative.model_dump_json(indent=2)}",
    f"Selected Retention Technique(s) (auxiliary):\n{retention_json}",
    f"Selected CTA (auxiliary):\n{input_data.selected_cta.model_dump_json(indent=2)}",
])
if input_data.content_goal:
    parts.append(f"Content Goal: {input_data.content_goal}")
if input_data.raw_notes:
    parts.append(f"Raw Notes (supplementary):\n{input_data.raw_notes}")
---
Step 7: backend/app/pipeline/orchestrator.py — Pass draft to all agents + fix doc paths
7a. NarrativeAgent (line ~359-366): Add draft=project.draft
Change NarrativeAgentInput(...) to include draft=project.draft:
input_data = NarrativeAgentInput(
    icp=icp,
    selected_hook=selected_hook,
    topic=project.topic,
    target_format=project.target_format,
    draft=project.draft,                    # NEW
    piragi_context=narrative_context or piragi_context,
)
7b. RetentionAgent (line ~397-405): Add draft=project.draft
Change RetentionAgentInput(...) to include draft=project.draft:
input_data = RetentionAgentInput(
    icp=icp,
    selected_hook=selected_hook,
    selected_narrative=selected_narrative,
    target_format=project.target_format,
    content_goal=project.content_goal,
    draft=project.draft,                    # NEW
    piragi_context=retention_context or piragi_context,
)
7c. CTAAgent (line ~421-429): Add draft=project.draft
Change CTAAgentInput(...) to include draft=project.draft:
input_data = CTAAgentInput(
    icp=icp,
    selected_hook=selected_hook,
    selected_narrative=selected_narrative,
    content_goal=project.content_goal,
    cta_purpose=project.cta_purpose,
    draft=project.draft,                    # NEW
    piragi_context=piragi_context,
)
7d. WriterAgent (line ~441-452): Add draft=project.draft
Change WriterAgentInput(...) to include draft=project.draft:
input_data = WriterAgentInput(
    icp=icp,
    selected_hook=selected_hook,
    selected_narrative=selected_narrative,
    selected_retention=selected_retention,
    selected_cta=selected_cta,
    topic=project.topic,
    target_format=project.target_format,
    content_goal=project.content_goal,
    draft=project.draft,                    # NEW - primary
    raw_notes=project.raw_notes,            # KEEP - supplementary
    piragi_context=piragi_context,
)
7e. Fix Narrative global doc path (line ~349-357): Change playbooks_base / "narratives" to point to actual folder
Change:
playbook_narrative_dir = playbooks_base / "narratives"
To:
global_narrative_dir = Path("/Users/karpinski94/projects/scripts-writer/documents/narrative_patterns")
And update the surrounding code to use global_narrative_dir instead of playbook_narrative_dir.
7f. Fix Retention global doc path (line ~387-395): Change playbooks_base / "retention" to point to actual folder
Change:
playbook_retention_dir = playbooks_base / "retention"
To:
global_retention_dir = Path("/Users/karpinski94/projects/scripts-writer/documents/retention_tactics")
And update the surrounding code to use global_retention_dir instead of playbook_retention_dir.
Also fix narrative and retention to read ALL files from the global folder (not just [:1]), since there are multiple reference files (aida.txt, pas.txt, heroes_journey.txt for narratives; teasers.txt, curiosity_gap.txt for retention).
---
Step 8: backend/tests/unit/test_agents.py — Update tests
Update HookAgentInput test construction at line 45 and 55 to match new schema if needed (draft is optional so existing tests should still pass).
Add a test for hook agent that verifies draft appears in prompt when provided.
---
Summary of All Files Changed
File	Changes
backend/app/schemas/agents.py	Add draft field to NarrativeAgentInput, RetentionAgentInput, CTAAgentInput, WriterAgentInput
backend/app/agents/hook_agent.py	Rewrite SYSTEM_PROMPT + reorder build_prompt() to emphasize draft as primary
backend/app/agents/narrative_agent.py	Rewrite SYSTEM_PROMPT + add draft to build_prompt() as primary
backend/app/agents/retention_agent.py	Rewrite SYSTEM_PROMPT + add draft to build_prompt() as primary
backend/app/agents/cta_agent.py	Rewrite SYSTEM_PROMPT + add draft to build_prompt() as primary
backend/app/agents/writer_agent.py	Rewrite SYSTEM_PROMPT + add draft to build_prompt() as primary, demote raw_notes
backend/app/pipeline/orchestrator.py	Pass draft=project.draft to 4 agents + fix global doc paths for narrative/retention
backend/tests/unit/test_agents.py	Optionally add draft-specific test

---

# New: Implement Project-Specific FAISS RAG for ICP Generation

## Overview

This plan implements a custom FAISS-based RAG pipeline that integrates with the ICP upload workflow. The pipeline follows the exact logic from `backend/dummyfiles/ingestion_pipeline.py` and `backend/dummyfiles/answer_generation.py`.

## Workflow

```
1. User uploads ICP files via /icp/upload
         ↓
2. Files saved to documents/{project_slug}/icp/
         ↓
3. On EVERY upload → trigger FAISS ingestion (per project)
         ↓
4. User clicks "Run ICP Agent"
         ↓
5. Orchestrator calls FAISS search with ICP query
         ↓
6. Retrieved chunks passed to ICP agent via FAISS retriever (not piragi_context)
         ↓
7. ICP agent generates profile using retrieved context
         ↓
8. ICP displayed in frontend ICP panel
```

## Dependencies (backend)

- Using `faiss-cpu` and `sklearn` (imported from `sklearn`) as shown in `dummyfiles/`.
- Install via: `uv add faiss-cpu sklearn`

## Backend Changes

### 1. [NEW] `backend/app/rag/faiss_service.py`

Implementation exactly as in `backend/dummyfiles/ingestion_pipeline.py`:

```python
# Functions:
def load_documents(docs_path: str) -> list[dict]:
    """Load all .txt files from directory."""

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""

def create_index(documents: list[dict], project_id: str) -> None:
    """Create FAISS index with TF-IDF for a project.
    - Saves to data/faiss_indexes/{project_id}/index.faiss
    - Saves metadata.pkl with texts, metadatas, vectorizer
    """
    
def load_index(project_id: str):
    """Load FAISS index from disk."""

def search_project_documents(project_id: str, query: str, k: int = 5) -> list[tuple]:
    """Search indexed documents, return top k chunks with metadata and distance."""
```

**Configuration (matching dummyfiles):**
- `TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))`
- `chunk_size=1000`, `chunk_overlap=200`
- `faiss.IndexFlatL2(dimension)`
- Persistence:  `data/faiss_indexes/{project_id}/`

**ICP Query (exact from answer_generation.py):**
```python
ICP_QUERY = "form an icp (ideal customer profile) from all the documents take most common lead awarness levels, identities, pain points, goals, dreams, desires, internal conficts, doubts, enemies, external barriers, failed attempts, what did not work, the emotional drivers - why now, and what makes them buy and give me detailed report with quotes based on that"
```

### 2. [MODIFY] `backend/app/api/icp.py`

In `upload_icp` endpoint (around line 118):

**Change 1:** After saving file with aiofiles, trigger ingestion:
```python
# After line 132 (after aiofiles save)
from app.rag.faiss_service import create_index

project_slug = project.name.lower().replace(" ", "-")
docs_dir = Path(DOCUMENTS_DIR_BASE) / project_slug / "icp"
create_index_function = create_index  # or make async
create_index(str(docs_dir), project_id)  # Ingest all files for this project
```

**Actually**, we should add a NEW endpoint to explicitly trigger ingestion, because uploading happens per file and we want to ingest ALL files after all uploads complete. Add:

```python
@router.post("/ingest", response_model=dict)
async def ingest_icp_documents(project_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger FAISS ingestion for all uploaded ICP documents."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    project_slug = project.name.lower().replace(" ", "-")
    docs_dir = Path(DOCUMENTS_DIR_BASE) / project_slug / "icp"
    
    from app.rag.faiss_service import create_index
    create_index(str(docs_dir), project_id)
    
    return {"status": "ingested", "project_id": project_id}
```

Or better: Trigger ingestion automatically when generating ICP (not on every upload), so we don't rebuild index on each file upload.

**MODIFIED:** In `generate_icp` endpoint, call ingestion before running agent:

```python
@router.post("/generate", response_model=ICPProfileResponse)
async def generate_icp(project_id: str, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)
    
    # NEW: Ensure FAISS index exists before running agent
    project = await project_service.get_by_id(project_id)
    project_slug = project.name.lower().replace(" ", "-")
    docs_dir = Path(DOCUMENTS_DIR_BASE) / project_slug / "icp"
    
    if docs_dir.exists():
        from app.rag.faiss_service import create_index
        create_index(str(docs_dir), project_id)  # Ingest all docs
    
    # Continue with existing pipeline
    pipeline_service = PipelineService(db)
    await pipeline_service.run_step(project_id, StepType.icp)
    ...
```

### 3. [MODIFY] `backend/app/pipeline/orchestrator.py`

In `_build_agent_inputs` for `StepType.icp` (lines 245-289):

**REMOVE** existing "read only first file" logic (lines 250-276):
```python
# REMOVE THIS:
project_icp_dir = docs_base / "icp"
if project_icp_dir.exists():
    files = list(project_icp_dir.glob("*"))
    if files:
        doc_content = []
        for f in files[:1]:  # <-- ONLY FIRST FILE!
            ...
```

**REPLACE** with FAISS retrieval:
```python
# NEW: Use FAISS to retrieve relevant chunks
from app.rag.faiss_service import search_project_documents, ICP_QUERY

if project_icp_dir.exists():
    # Use FAISS search instead of reading first file
    try:
        results = search_project_documents(project_id, ICP_QUERY, k=5)
        if results:
            retrieved_chunks = "\n\n".join([text for text, meta, dist in results])
            raw_notes = (
                f"Retrieved context from project documents:\n{retrieved_chunks}\n\n"
                f"Original notes: {raw_notes}"
            )
            logger.debug(f"[ORCHESTRATOR] FAISS retrieved {len(results)} chunks")
    except Exception as e:
        logger.warning(f"[ORCHESTRATOR] FAISS search failed: {e}, using raw_notes only")
```

Also need to add `project_id` parameter to `_build_agent_inputs` - check current signature.

### 4. [NO CHANGE NEEDED] `backend/app/agents/icp_agent.py`

The agent already has `piragi_context` field. We can pass FAISS-retrieved chunks via this field, but conceptually it's different from Piragi RAG. For clarity, we may want to rename to `retrieved_context` in a future step, but for now it's fine to reuse the field - the key difference is HOW the context is retrieved (FAISS search, not Piragi).

Frontend: No changes required - the existing ICP panel displays the generated profile from the API response.

## Database/Storage Changes

No new database tables needed. The FAISS index files are stored in:
- `backend/data/faiss_indexes/{project_id}/index.faiss` (FAISS index)
- `backend/data/faiss_indexes/{project_id}/metadata.pkl` (texts + vectorizer)

Ensure the `backend/data/faiss_indexes/` directory exists.

## API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/{project_id}/icp/upload` | (Unchanged) Saves file, no ingestion trigger yet |
| POST | `/api/v1/projects/{project_id}/icp/generate` | (Modified) Triggers FAISS ingestion before running ICP agent |
| GET | `/api/v1/projects/{project_id}/icp` | (Unchanged) Returns ICP profile |

Optionally add explicit ingestion endpoint:
| POST | `/api/v1/projects/{project_id}/icp/ingest` | Manual trigger to rebuild FAISS index |

## Testing Plan

1. **Unit test faiss_service**: Test chunking, indexing, search
2. **Integration test**: Upload files → generate ICP → verify FAISS index created
3. **Manual test**: Frontend ICP panel - upload files, generate ICP, verify context used

## Files Summary

| File | Change |
|------|--------|
| `backend/app/rag/faiss_service.py` | NEW - FAISS ingestion and search |
| `backend/app/api/icp.py` | MODIFIED - trigger ingestion on generate |
| `backend/app/pipeline/orchestrator.py` | MODIFIED - use FAISS search instead of first-file logic |
| `backend/data/faiss_indexes/` | NEW - created at runtime for each project |

---

Open Questions (from implementation plan):
1. **Embedding Stack:** Using TF-IDF (dummyfiles). Could upgrade to sentence-transformers later.
2. **Persistence Location:** Using `backend/data/faiss_indexes/` - confirm in docs? Yes, documented.