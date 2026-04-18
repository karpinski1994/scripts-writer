## Context

The BubbleMenu in the Script Editor appears when text is selected, but when the user clicks on the input field to type an instruction, the selection is lost. This is a common issue with contentEditable elements and browser selection handling.

**Current Behavior:**
1. User selects text in editor
2. BubbleMenu appears
3. User clicks on input field
4. Selection disappears (browser focus moves to input)

**Constraints:**
- Must work with Tiptap's BubbleMenu component
- Must not break existing rewrite functionality
- Simple fix - no major refactoring

## Goals / Non-Goals

**Goals:**
- Preserve the visual selection highlight while BubbleMenu is visible
- Display selected text in the BubbleMenu for clarity

**Non-Goals:**
- Complex selection state management
- Multi-selection handling
- Cross-browser selection polyfills

## Decisions

### Approach: Capture Selection on BubbleMenu Open
**Decision:** Capture and store the selected text when BubbleMenu renders, display it as a visual indicator in the BubbleMenu UI.

**Implementation:**
1. Use Tiptap's `editor.state.selection` to get current selection when BubbleMenu renders
2. Store selected text in component state
3. Display selected text preview in BubbleMenu (truncated if long)
4. Use stored selection for API call instead of re-querying

**Alternative Considered:** Restore selection on input focus - more complex and can cause flickering

**Why This Approach:** Simple, maintains visual feedback, no flicker

## Risks / Trade-offs

**[Risk]** Selection might change while BubbleMenu is open (user clicks elsewhere in editor)
→ **Mitigation:** Accept this limitation - user can re-select if needed

**[Risk]** Long selections might clutter UI
→ **Mitigation:** Truncate display to ~50 chars with ellipsis