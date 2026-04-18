# Design: Persist Selection on Focus

## Current Implementation

### Problem Analysis

The current `PersistentSelection` extension renders decorations based on `state.selection`:

```typescript
props: {
  decorations(state: any) {
    const { from, to } = state.selection;
    if (from === to) return DecorationSet.empty;  // ← Fails when editor loses focus
    // ...
  },
}
```

When the user clicks on the BubbleMenu input:
1. Focus moves from editor → input
2. `editor.state.selection` becomes empty (from === to)
3. Extension returns `DecorationSet.empty`
4. Blue highlight disappears

### Desired Behavior

The decoration should render based on STORED selection position from React state, not the live Prosemirror selection.

---

## Design Decision: Bridge React State to Prosemirror

### Option 1: Extend Extension API (Chosen)

Pass the stored selection position to the extension via Tiptap's extension attributes:

```typescript
PersistentSelection.configure({
  persistedFrom: storedSelectionPos?.from,
  persistedTo: storedSelectionPos?.to,
})
```

**Pros**: Clean separation, follows Tiptap patterns
**Cons**: Requires extension reconfiguration on selection change

### Option 2: Global Store

Use a module-level variable to share selection between React and extension:

```typescript
// In persistent-selection.ts
let persistedRange: { from: number; to: number } | null = null;
export function setPersistedRange(range) { persistedRange = range; }
```

**Pros**: Simple, no reconfiguration needed
**Cons**: Not idiomatic, pollutes module scope

### Option 3: Editor Command

Add a custom Tiptap command to set the persisted range:

```typescript
editor.chain().focus().setPersistedSelection(from, to).run()
```

**Pros**: Clean, chainable
**Cons**: More complex to implement

---

## Chosen Approach: Option 1 - Extension Configuration

### Rationale

- Follows Tiptap's existing patterns for passing dynamic data to extensions
- Keeps the extension pure and testable
- No module-level state pollution
- Reconfiguration is cheap (just updates attributes)

---

## Implementation Plan

### 1. Update `persistent-selection.ts`

Modify to accept configuration for persisted range:

```typescript
export const PersistentSelection = Extension.create({
  name: "persistentSelection",
  addOptions() {
    return {
      persistedFrom: null as number | null,
      persistedTo: null as number | null,
    };
  },
  addProseMirrorPlugins() {
    // Use options.persistedFrom / options.persistedTo instead of state.selection
  },
});
```

### 2. Update `script-editor.tsx`

Pass the stored selection position to the extension:

```typescript
const editor = useEditor({
  extensions: [
    // ...other extensions
    PersistentSelection.configure({
      persistedFrom: storedSelectionPos?.from ?? null,
      persistedTo: storedSelectionPos?.to ?? null,
    }),
  ],
});
```

Update the stored selection state to trigger extension reconfiguration:

```typescript
useEffect(() => {
  if (storedSelectionPos && editor) {
    // Force extension to update its configuration
    editor.extensionManager.extensions.find(e => e.name === 'persistentSelection')
      ?.options?.set?.({
        persistedFrom: storedSelectionPos.from,
        persistedTo: storedSelectionPos.to,
      });
  }
}, [storedSelectionPos, editor]);
```

Alternative: Recreate editor when selection changes (simpler but less efficient):

```typescript
// In script-editor.tsx - re-configure when selection stored
useEffect(() => {
  if (!editor || !storedSelectionPos) return;
  
  // The extension reads from options, which we update via editor storage
  editor.storage.persistentSelection.persistedFrom = storedSelectionPos.from;
  editor.storage.persistentSelection.persistedTo = storedSelectionPos.to;
  
  // Force decoration re-render
  editor.view.dispatch(editor.state.tr);
}, [storedSelectionPos]);
```

### 3. Verify CSS

The existing `.persistent-selection` CSS should work:

```css
.persistent-selection {
  background-color: rgba(59, 130, 246, 0.3); /* blue-500 with opacity */
}
```

---

## File Changes Summary

| File | Change |
|------|-------|
| `frontend/src/components/editor/persistent-selection.ts` | Accept config options for persisted range |
| `frontend/src/components/editor/script-editor.tsx` | Pass stored selection to extension |
| `frontend/src/app/globals.css` | Already has `.persistent-selection` (verify) |

---

## Testing Strategy

1. Select text in editor → blue highlight appears
2. Click on BubbleMenu input → highlight persists
3. Clear selection → highlight disappears
4. Rewrite text → highlight clears after replacement

---

**Status**: Ready for implementation

**Complexity**: Medium — requires understanding Tiptap extension options API