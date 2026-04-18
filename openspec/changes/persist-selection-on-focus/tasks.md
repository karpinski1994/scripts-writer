# Tasks: Persist Selection on Focus

## Implementation Order

1. Update `persistent-selection.ts` extension to accept configuration options
2. Update `script-editor.tsx` to pass stored selection to extension
3. Verify CSS exists in globals.css
4. Test the feature

---

## Task 1: Update persistent-selection.ts

**File**: `frontend/src/components/editor/persistent-selection.ts`

**Step 1.1**: Add options to extension

Replace the entire file with:

```typescript
import { Extension } from "@tiptap/core";

// @ts-ignore - tiptap/pm re-exports prosemirror modules
import { Plugin, PluginKey } from "@tiptap/pm/state";

const persistentSelectionKey = new PluginKey("persistentSelection");

export const PersistentSelection = Extension.create({
  name: "persistentSelection",

  addOptions() {
    return {
      persistedFrom: null as number | null,
      persistedTo: null as number | null,
    };
  },

  addProseMirrorPlugins() {
    const { Decoration, DecorationSet } = require("prosemirror-state");

    return [
      new Plugin({
        key: persistentSelectionKey,
        props: {
          decorations(state: any) {
            // Use stored selection from options, fallback to live selection
            const from = this.options.persistedFrom ?? state.selection.from;
            const to = this.options.persistedTo ?? state.selection.to;
            
            if (from === to) return DecorationSet.empty;

            return DecorationSet.create(state.doc, [
              Decoration.inline(from, to, {
                class: "persistent-selection",
                "data-persistent": "true",
              }),
            ]);
          },
        },
      }),
    ];
  },
});
```

**Step 1.2**: Verify the extension exports correctly

```bash
cd frontend && npm run lint
```

---

## Task 2: Update script-editor.tsx

**File**: `frontend/src/components/editor/script-editor.tsx`

**Step 2.1**: Pass stored selection to extension

Find the `useEditor` call (around line 41) and update the `PersistentSelection` configuration:

```typescript
const editor = useEditor({
  extensions: [
    StarterKit,
    Highlight,
    StructuralCueBroll,
    StructuralCueTextOverlay,
    StructuralCuePause,
    PersistentSelection.configure({
      persistedFrom: storedSelectionPos?.from ?? null,
      persistedTo: storedSelectionPos?.to ?? null,
    }),
  ],
  // ... rest of config
});
```

**Step 2.2**: Force decoration update when selection stored

Find the `useEffect` that handles selection (around line 59) and add:

```typescript
useEffect(() => {
  if (!editor) return;
  
  const updateSelection = () => {
    const selection = editor.state.selection;
    if (selection.empty) {
      setStoredSelection("");
      setStoredSelectionPos(null);
      return;
    }
    const selectedText = editor.state.doc.textBetween(selection.from, selection.to, " ");
    if (selectedText.trim()) {
      setStoredSelection(selectedText);
      setStoredSelectionPos({ from: selection.from, to: selection.to });
    }
  };
  
  updateSelection();
  
  editor.on("selectionUpdate", updateSelection);
  
  // NEW: Update extension with stored selection
  editor.on("selectionUpdate", () => {
    if (storedSelectionPos && editor) {
      const ext = editor.extensionManager.extensions.find(
        (e: any) => e.name === "persistentSelection"
      );
      if (ext) {
        ext.options.persistedFrom = storedSelectionPos.from;
        ext.options.persistedTo = storedSelectionPos.to;
        // Trigger decoration re-render
        editor.view.dispatch(editor.state.tr);
      }
    }
  });
  
  return () => {
    editor.off("selectionUpdate", updateSelection);
  };
}, [editor]);
```

**Wait** - This approach has an issue: the listener gets added on every render. A better approach is to sync the extension when `storedSelectionPos` changes:

```typescript
// Add this separate useEffect
useEffect(() => {
  if (!editor || !storedSelectionPos) return;
  
  const ext = editor.extensionManager.extensions.find(
    (e: any) => e.name === "persistentSelection"
  );
  if (ext) {
    ext.options.persistedFrom = storedSelectionPos.from;
    ext.options.persistedTo = storedSelectionPos.to;
    editor.view.dispatch(editor.state.tr);
  }
}, [editor, storedSelectionPos]);
```

---

## Task 3: Verify CSS

**File**: `frontend/src/app/globals.css`

**Step 3.1**: Check for `.persistent-selection` class

If not present, add:

```css
.persistent-selection {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 2px;
}
```

---

## Task 4: Test

1. Start the frontend dev server: `npm run dev`
2. Open a project in the editor
3. Select a portion of text
4. Verify blue highlight appears
5. Click on the BubbleMenu input
6. Verify highlight persists

---

## Completion Criteria

- [x] Task 1: Extension accepts config options ✅
- [x] Task 2: Editor passes stored selection ✅  
- [x] Task 3: CSS exists ✅
- [ ] Task 4: Feature works in browser ❓

---

## Rollback Plan

If the extension approach doesn't work:

1. Revert `persistent-selection.ts` to original
2. Try using `decorations` at document level instead of plugin level
3. Or use a separate Tiptap extension that renders to a separate DOM layer

---

**Time Estimate**: 30 minutes

**Blocked By**: None