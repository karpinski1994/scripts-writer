## Why

The Script Editor currently only supports manual editing and auto-save. Users who want to improve specific portions of their script must manually rewrite text or regenerate entire scripts through the pipeline. This creates friction for iterative editing—users may try dozens of rewrites before settling on final text, and saving each attempt as a Pipeline Step would bloat the database. Adding inline AI text regeneration via a Tiptap BubbleMenu enables lightweight, exploratory editing directly in the editor without pipeline overhead.

## What Changes

1. **New Backend Agent**: Create `selection_rewrite_agent.py` that takes selected text, full script context, user instruction, and optional ICP summary to produce rewritten text
2. **New API Endpoint**: Add `POST /{project_id}/scripts/rewrite-selection` to the scripts router
3. **New Frontend UI**: Add Tiptap BubbleMenu component to script-editor.tsx with instruction input and rewrite button
4. **State Management**: Add isRewriting and instruction state to editor component

## Capabilities

### New Capabilities
- **selection-rewrite**: Inline AI text regeneration in the script editor via BubbleMenu interface

### Modified Capabilities
- None. This adds a net-new capability that doesn't change existing spec requirements.

## Impact

- **Backend**: New agent module at `backend/app/agents/selection_rewrite_agent.py`, new endpoint in `backend/app/api/scripts.py`
- **Frontend**: Modified `frontend/src/components/editor/script-editor.tsx` to add BubbleMenu
- **Dependencies**: Requires `@tiptap/react` BubbleMenu component (already available in Tiptap)
- **No Breaking Changes**: This is purely additive—no existing APIs or behaviors are modified
