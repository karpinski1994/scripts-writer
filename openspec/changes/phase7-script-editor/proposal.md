## Why

Phase 6 built the complete pipeline UX — agent panels, WebSocket streaming, step navigation. Users can run ICP through CTA and make selections, but the Writer agent result is only shown as raw JSON in a placeholder panel. There is no way to edit the generated script, see structural cues highlighted, browse version history, or trigger script generation from the pipeline view. The core value proposition — producing an editable, versioned script — is missing.

Phase 7 adds the Tiptap-based rich script editor with debounced auto-save, structural cue highlighting, version history switching, and writer agent integration into the pipeline view. This is the first time users can actually work with their generated script.

## What Changes

- Add `editor-store.ts` — Zustand store tracking editor content, version number, dirty/saving state, and debounced save timer
- Install Tiptap (`@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-highlight`) and build `script-editor.tsx` — rich editor with toolbar (bold, italic, headings, lists, undo/redo), word count, dirty indicator, debounced 500ms auto-save via `PATCH /scripts/{version_id}`
- Add custom Tiptap extension `structural-cue` — scans text for `[B-ROLL]`, `[TEXT OVERLAY]`, `[PAUSE]` patterns and applies distinct background highlights (amber for B-ROLL, blue for TEXT OVERLAY, purple for PAUSE)
- Add version history dropdown to editor — fetches `GET /scripts` for the project, renders dropdown of version numbers with timestamps, switching loads that version's content into the editor
- Integrate writer agent into pipeline view — when `activeStepType === "writer"`, show a Writer panel with "Generate Script" button that calls `POST /pipeline/run/writer`, streams output, then loads the result into the script editor
- Create dedicated editor route at `/projects/[id]/editor` — full-page editor with version history sidebar, accessible from the Writer step panel or via direct navigation

## Capabilities

### New Capabilities
- `script-editor`: Tiptap rich editor component with toolbar, structural cue highlighting, debounced auto-save, word count, dirty indicator, and version history switching
- `writer-integration`: Writer agent panel in pipeline view, script generation trigger, streaming output to editor, navigation to dedicated editor page

### Modified Capabilities
- `pipeline-ui`: Writer step now shows Writer panel instead of "coming soon" placeholder
- `agent-panels`: `agent-panel-wrapper.tsx` handles the "writer" case, rendering the Writer panel with generate button

## Impact

- **New files**: `frontend/src/stores/editor-store.ts`, `frontend/src/components/editor/script-editor.tsx`, `frontend/src/components/editor/toolbar.tsx`, `frontend/src/components/editor/structural-cue-extension.ts`, `frontend/src/components/editor/version-dropdown.tsx`, `frontend/src/components/agents/writer-panel.tsx`, `frontend/src/app/projects/[id]/editor/page.tsx`
- **Modified files**: `frontend/package.json` (add Tiptap deps), `frontend/src/components/agents/agent-panel-wrapper.tsx` (add writer case), `frontend/src/stores/pipeline-store.ts` (add writer step completion handler), `frontend/src/types/agents.ts` (ensure ScriptDraft type is complete)
