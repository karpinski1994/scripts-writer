## Context

Phase 6 is complete. The pipeline view renders 10 step cards, the step sidebar provides navigation, and 5 agent panels (ICP, Hook, Narrative, Retention, CTA) handle selection flows. The `AgentPanelWrapper` renders a "coming soon" placeholder for the `writer` step type and all analysis steps.

The backend has a complete Writer agent (`backend/app/agents/writer_agent.py`) that generates `WriterAgentOutput` containing a `ScriptDraft` (content, format, structural_cues, word_count). The `scripts.py` API already supports `GET /scripts` (list versions), `GET /scripts/{version_id}`, `POST /scripts/generate` (run writer + create version), and `PATCH /scripts/{version_id}` (update content). The `ScriptVersion` model stores versioned content with `version_number`.

The `ScriptDraft` type already exists in `frontend/src/types/agents.ts` with fields: `title`, `content`, `word_count`, `notes`. The `ScriptVersion` type exists in `frontend/src/types/script.ts`.

The `pipeline-store.ts` has `DEPENDENCY_MAP` showing `writer` depends on `[icp, hook, narrative, retention, cta]`. The orchestrator already handles writer step execution with full context assembly.

The `AppSettings` in the backend already defines `debounce_save_ms: int = 500` for the editor debounce interval.

## Goals / Non-Goals

**Goals:**
- Zustand editor store with content, version, dirty/saving state, debounced save timer
- Tiptap rich editor component with formatting toolbar, word count, dirty/saving indicators
- Custom Tiptap extension that highlights `[B-ROLL]`, `[TEXT OVERLAY]`, `[PAUSE]` with distinct background colors
- Version history dropdown to switch between script versions
- Writer agent panel in pipeline view with "Generate Script" button
- Dedicated editor page at `/projects/[id]/editor` for full-screen editing
- Debounced auto-save (500ms) via `PATCH /scripts/{version_id}`

**Non-Goals:**
- Real-time collaborative editing (single-user app)
- Inline commenting or annotation system
- Script template system
- Export UI (Phase 9)
- Analysis agent panels (Phase 8)
- Branch/re-run confirmation dialogs (Phase 9)

## Decisions

### 1. Tiptap for rich editing
**Choice:** Use Tiptap (ProseMirror-based) as the rich text editor
**Alternative:** Slate.js, Lexical, or plain textarea
**Rationale:** Tiptap is explicitly listed in the tech stack (dev plan line 56). It has first-class React support, a plugin/extension architecture ideal for structural cue highlighting, and starter-kit provides all needed formatting. ProseMirror foundation ensures robust editing.

### 2. Structural cue highlighting as a custom Tiptap Mark extension
**Choice:** Build a `StructuralCue` Tiptap Mark extension that decorates matched text patterns (`[B-ROLL]`, `[TEXT OVERLAY]`, `[PAUSE]`) with distinct background colors using ProseMirror's decoration system
**Alternative:** Use regex replacement to insert styled HTML nodes, or use Tiptap's Highlight extension with custom classes
**Rationale:** A Mark extension is the idiomatic Tiptap way. It integrates with undo/redo, doesn't break on cursor positioning, and can be toggled. Using ProseMirror decorations via a Plugin would also work but Marks are simpler for inline styling. The extension uses `addInputRules` to detect bracket patterns as they're typed and applies the appropriate mark.

### 3. Debounced auto-save in Zustand store, not in the editor component
**Choice:** The editor store manages the debounce timer. `setContent()` sets `isDirty = true` and resets a 500ms timer. When the timer fires, it calls `PATCH /scripts/{version_id}` with the current content, sets `isSaving = true`, then `isDirty = false` and `isSaving = false` on completion.
**Alternative:** Use `useDebounce` hook in the component, or TanStack Query mutations
**Rationale:** Centralizing save logic in the store avoids race conditions if the component re-renders. The store can cancel pending saves on unmount or version switch. The `debounce_save_ms` from `AppSettings` (backend) is 500ms — we hardcode the same value on the frontend.

### 4. Version history as a dropdown, not a separate page
**Choice:** A dropdown/select component in the editor toolbar area shows version numbers (v1, v2, etc.) with creation timestamps. Selecting a version loads that version's content. Creating a new version happens when the Writer agent generates a script (via `POST /scripts/generate`).
**Alternative:** Full version history page with diff view
**Rationale:** The dev plan (step 7.5) says "version history dropdown." A dropdown is sufficient for the number of versions we expect (1-5 per project). Diff view is overkill for v1. The dedicated editor page can expand this later.

### 5. Writer panel as an agent panel in the pipeline view
**Choice:** When `activeStepType === "writer"`, the `AgentPanelWrapper` renders a `WriterPanel` component. This panel shows: (1) "Generate Script" button if the writer step is pending and dependencies are met, (2) a loading state while the writer agent runs, (3) a preview of the generated script with a "Open in Editor" button after completion, (4) a "Regenerate" option.
**Alternative:** Navigate directly to the editor page on writer step click
**Rationale:** Keeping the writer step in the pipeline view is consistent with other agent panels. Users expect to see the agent's output in the pipeline context first, then navigate to the full editor for detailed editing. The "Open in Editor" button provides the transition.

### 6. Dedicated editor page at `/projects/[id]/editor`
**Choice:** Create `frontend/src/app/projects/[id]/editor/page.tsx` as a full-page editor view with the Tiptap editor, toolbar, version dropdown, and a back-to-pipeline link. This is accessible from the Writer panel's "Open in Editor" button.
**Alternative:** Edit inline in the pipeline view
**Rationale:** The pipeline view is cramped for a full editor experience. A dedicated page gives the editor full screen real estate. The URL is already defined in the dev plan directory structure (line 160).

### 7. Editor content stored as plain text, not HTML
**Choice:** The Tiptap editor loads content as plain text (via `editor.commands.setContent(content)` with `text` mode). On save, it extracts plain text via `editor.getText()`. Formatting is applied via the toolbar but saved as plain text with markdown-like markers (the structural cues like `[B-ROLL]` are already plain text).
**Alternative:** Store content as HTML or Tiptap JSON
**Rationale:** The backend `ScriptVersion.content` is a TEXT field. The writer agent generates plain text with structural cues. Export formats are txt/md. Storing as plain text keeps things simple and compatible. Rich formatting (bold, italic) is for display/editing convenience only and doesn't need to persist across sessions — structural cues are the important markup. If we later need persistent formatting, we can migrate to Tiptap JSON storage.

## Risks / Trade-offs

- **[Risk] Tiptap bundle size** → Mitigation: `@tiptap/starter-kit` includes only essential extensions. Tree-shaking applies. The editor is code-split via Next.js dynamic import on the editor page.

- **[Risk] Structural cue regex performance on large scripts** → Mitigation: Scripts are typically 500-2000 words. The Mark extension's input rules only fire on pattern match at cursor position, not on full-document scan. Initial document decoration uses ProseMirror's efficient decoration reconciliation.

- **[Trade-off] Plain text storage means formatting is ephemeral** → Bold/italic/headings are for editing convenience only and don't persist after page reload. Structural cues DO persist because they're plain text. This is acceptable for v1 — the primary value is the structural cue highlighting, not persistent formatting.

- **[Trade-off] No auto-save conflict resolution** → If the user switches versions while a debounced save is pending, the save is cancelled. This prevents overwriting the wrong version. There's no simultaneous editing scenario in a single-user app.
