## Why

When a user selects text in the Script Editor and clicks on the BubbleMenu input field to type an instruction, the text selection is lost. This makes it difficult for users to see exactly which text they're rewriting, reducing confidence in the feature.

## What Changes

1. **Store selection state**: Capture and preserve the selected text and cursor position when the BubbleMenu is activated
2. **Display selected text**: Show the selected text in the BubbleMenu UI so users can see what's being rewritten
3. **Maintain selection on focus**: Prevent selection from being cleared when input receives focus

## Capabilities

### New Capabilities
None - this is a bug fix to existing selection-rewrite feature.

### Modified Capabilities
- `selection-rewrite`: Fix behavior where selection disappears when user clicks BubbleMenu input field

## Impact

- **Frontend**: Modify `frontend/src/components/editor/script-editor.tsx` to preserve selection state and display selected text