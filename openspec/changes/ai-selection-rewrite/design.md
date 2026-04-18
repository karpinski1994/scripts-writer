## Context

The Script Editor (Tiptap) currently supports manual text editing with debounced auto-save. Users need a lightweight way to regenerate specific text selections without going through the full pipeline. This feature adds inline AI text regeneration via a floating BubbleMenu that appears on text selection.

**Current State:**
- Editor at `frontend/src/components/editor/script-editor.tsx` uses Tiptap
- Backend has existing agent infrastructure in `backend/app/agents/`
- Scripts API at `backend/app/api/scripts.py` handles version CRUD

**Constraints:**
- Must work with existing auto-save mechanism
- Latency target < 3 seconds per rewrite
- No pipeline step creation - stateless per rewrite
- Must preserve surrounding context for tone consistency

## Goals / Non-Goals

**Goals:**
- Add BubbleMenu UI to script editor that appears on text selection
- Create backend endpoint for stateless text rewriting
- Integrate with existing LLM provider infrastructure
- Maintain auto-save after replacement

**Non-Goals:**
- Caching rewrite results (each rewrite is fresh LLM call)
- Multi-turn conversation with editor (stateless per rewrite)
- Version history for individual rewrites (handled by global script versioning)
- Saving rewrites as Pipeline Steps

## Decisions

### 1. Agent Implementation: Lightweight Direct Call vs BaseAgent
**Decision:** Create standalone agent `selection_rewrite_agent.py` using direct LLM call, not BaseAgent

**Rationale:** BaseAgent includes caching, state management, and complex output parsing. Selection rewrite is a stateless, single-purpose operation. Direct LLM call with simple string output is more appropriate and avoids unnecessary overhead.

**Alternative Considered:** Reuse BaseAgent - adds complexity for no benefit in this use case.

### 2. API Integration: New Endpoint vs Extension
**Decision:** Add `POST /{project_id}/scripts/rewrite-selection` to existing scripts.py router

**Rationale:** Keep related script operations in one place. The endpoint is clearly namespaced under scripts and doesn't warrant a separate router.

### 3. Context Passing: Surrounding Text vs Full Script
**Decision:** Pass full script content (up to 10k chars) as context

**Rationale:** The rewrite needs to maintain tone consistency with the surrounding text. Passing the full content ensures the LLM understands context. The prompt optimization can truncate if needed, but simpler to pass full content for now.

**Alternative Considered:** Pass ±500 chars around selection - adds complexity for marginal benefit; can optimize later if latency is an issue.

### 4. Frontend State: Local Component State vs Global Store
**Decision:** Local component state for `isRewriting` and `instruction`

**Rationale:** This is ephemeral UI state that doesn't need to persist or be shared across components. Local state is simpler and appropriate.

## Risks / Trade-offs

**[Risk]** Latency could exceed 3s target on slow LLM providers
→ **Mitigation:** Use fastest available provider (Gemini first in failover chain); lighter prompts than full script generation should keep it fast

**[Risk]** Replace operation could conflict with auto-save
→ **Mitigation:** The replace happens synchronously in the editor, auto-save debounces at 500ms - this should be fine

**[Risk]** User could lose selection if they click away during rewrite
→ **Mitigation:** Disable input during rewrite, show loading state

## Open Questions

1. **Token efficiency:** Should we truncate the full script if > 10k chars? For now, pass full content; optimize if needed based on latency.

2. **Error handling:** What happens if the LLM returns invalid output (not raw text)? For now, return the raw output as-is; user can undo if needed.

3. **ICP integration:** Should we always fetch ICP for tone context, or make it optional? Fetch if available, otherwise skip - keeps endpoint simple.