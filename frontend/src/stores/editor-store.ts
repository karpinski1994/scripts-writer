import { create } from "zustand";
import { api } from "@/lib/api";

const DEBOUNCE_MS = 500;

interface EditorStore {
  content: string;
  versionNumber: number;
  currentVersionId: string | null;
  isDirty: boolean;
  isSaving: boolean;
  debounceTimer: ReturnType<typeof setTimeout> | null;

  setContent: (content: string) => void;
  setVersionNumber: (n: number) => void;
  setCurrentVersionId: (id: string | null) => void;
  setIsSaving: (saving: boolean) => void;
  markClean: () => void;
  cancelPendingSave: () => void;
  reset: () => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  content: "",
  versionNumber: 1,
  currentVersionId: null,
  isDirty: false,
  isSaving: false,
  debounceTimer: null,

  setContent: (content) => {
    const state = get();
    if (state.debounceTimer) {
      clearTimeout(state.debounceTimer);
    }

    const timer = setTimeout(async () => {
      const current = get();
      if (!current.currentVersionId) return;
      set({ isSaving: true });
      try {
        await api.patch(`/api/v1/projects/scripts/${current.currentVersionId}`, {
          content: current.content,
        });
        set({ isDirty: false, isSaving: false });
      } catch {
        set({ isSaving: false });
      }
    }, DEBOUNCE_MS);

    set({ content, isDirty: true, debounceTimer: timer });
  },

  setVersionNumber: (n) => set({ versionNumber: n }),
  setCurrentVersionId: (id) => set({ currentVersionId: id }),
  setIsSaving: (saving) => set({ isSaving: saving }),

  markClean: () => set({ isDirty: false }),

  cancelPendingSave: () => {
    const state = get();
    if (state.debounceTimer) {
      clearTimeout(state.debounceTimer);
    }
    set({ debounceTimer: null, isSaving: false });
  },

  reset: () => {
    const state = get();
    if (state.debounceTimer) {
      clearTimeout(state.debounceTimer);
    }
    set({
      content: "",
      versionNumber: 1,
      currentVersionId: null,
      isDirty: false,
      isSaving: false,
      debounceTimer: null,
    });
  },
}));
