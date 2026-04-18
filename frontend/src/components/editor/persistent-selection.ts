import { Extension } from "@tiptap/core";
import { Plugin, PluginKey } from "@tiptap/pm/state";
import { Decoration, DecorationSet } from "@tiptap/pm/view";

export interface PersistentSelectionStorage {
  persistedFrom: number | null;
  persistedTo: number | null;
}

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    persistentSelection: {
      setPersistedSelection: (from: number, to: number) => ReturnType;
      clearPersistedSelection: () => ReturnType;
    };
  }
}

const persistentSelectionKey = new PluginKey("persistentSelection");

export const PersistentSelection = Extension.create<any, PersistentSelectionStorage>({
  name: "persistentSelection",

  addStorage() {
    return {
      persistedFrom: null,
      persistedTo: null,
    };
  },

  addCommands() {
    return {
      setPersistedSelection:
        (from: number, to: number) =>
        ({ editor }) => {
          this.storage.persistedFrom = from;
          this.storage.persistedTo = to;
          // Force a view update to render decorations
          editor.view.dispatch(editor.state.tr);
          return true;
        },
      clearPersistedSelection:
        () =>
        ({ editor }) => {
          this.storage.persistedFrom = null;
          this.storage.persistedTo = null;
          editor.view.dispatch(editor.state.tr);
          return true;
        },
    };
  },

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: persistentSelectionKey,
        props: {
          decorations: (state) => {
            const from = this.storage.persistedFrom;
            const to = this.storage.persistedTo;

            if (from === null || to === null || from === to) {
              return DecorationSet.empty;
            }

            // Ensure the selection is within document bounds
            const docSize = state.doc.content.size;
            const safeFrom = Math.max(0, Math.min(from, docSize));
            const safeTo = Math.max(0, Math.min(to, docSize));

            if (safeFrom === safeTo) return DecorationSet.empty;

            return DecorationSet.create(state.doc, [
              Decoration.inline(safeFrom, safeTo, {
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