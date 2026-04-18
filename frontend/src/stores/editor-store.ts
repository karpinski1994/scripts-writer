import { create } from "zustand";
import { api } from "@/lib/api";

const AUTO_SAVE_INTERVAL_MS = 30000;

interface EditorStore {
  content: string;
  versionNumber: number;
  currentVersionId: string | null;
  isDirty: boolean;
  isSaving: boolean;
  autoSaveTimer: ReturnType<typeof setInterval> | null;

  projectId: string | null;
  setProjectId: (id: string | null) => void;
  setContent: (content: string) => void;
  setVersionNumber: (n: number) => void;
  setCurrentVersionId: (id: string | null) => void;
  setIsSaving: (saving: boolean) => void;
  markClean: () => void;
  save: () => Promise<void>;
  startAutoSave: () => void;
  stopAutoSave: () => void;
  reset: () => void;
}

export const useEditorStore = create<EditorStore>((set, get) => ({
  content: "",
  versionNumber: 1,
  currentVersionId: null,
  isDirty: false,
  isSaving: false,
  autoSaveTimer: null,

  projectId: null,
  setProjectId: (id) => set({ projectId: id }),
  setContent: (content) => {
    const currentContent = get().content;
    if (content !== currentContent) {
      set({ content, isDirty: true });
    }
  },

  setVersionNumber: (n) => set({ versionNumber: n }),
  setCurrentVersionId: (id) => set({ currentVersionId: id }),
  setIsSaving: (saving) => set({ isSaving: saving }),

  markClean: () => set({ isDirty: false }),

  save: async () => {
    const state = get();
    if (!state.currentVersionId || !state.isDirty || state.isSaving) {
      return;
    }

    set({ isSaving: true });
    
    // Optimistically update pipeline store to keep WriterPanel in sync immediately
    try {
      const { usePipelineStore } = await import("./pipeline-store");
      usePipelineStore.getState().updateStepContent("writer", state.content);
    } catch (e) {
      console.warn("Optimistic sync failed:", e);
    }

    try {
      await api.patch(`/api/v1/projects/scripts/${state.currentVersionId}`, {
        content: state.content,
      });
      
      const { toast } = await import("sonner");
      toast.success("Changes saved");
      
      set({ isDirty: false, isSaving: false });

      // Invalidate queries to ensure fresh data on navigation
      if (state.projectId) {
        const { queryClient } = await import("@/lib/query-client");
        queryClient.invalidateQueries({ queryKey: ["scripts", state.projectId] });
        queryClient.invalidateQueries({ queryKey: ["pipeline", state.projectId] });
      }
    } catch (e) {
      console.error("Save failed:", e);
      const { toast } = await import("sonner");
      toast.error("Failed to save changes");
      set({ isSaving: false });
    }
  },

  startAutoSave: () => {
    const state = get();
    if (state.autoSaveTimer) {
      return;
    }
    const timer = setInterval(async () => {
      const current = get();
      if (current.isDirty && current.currentVersionId && !current.isSaving) {
        await get().save();
      }
    }, AUTO_SAVE_INTERVAL_MS);
    set({ autoSaveTimer: timer });
  },

  stopAutoSave: () => {
    const state = get();
    if (state.autoSaveTimer) {
      clearInterval(state.autoSaveTimer);
      set({ autoSaveTimer: null });
    }
  },

  reset: () => {
    const state = get();
    if (state.autoSaveTimer) {
      clearInterval(state.autoSaveTimer);
    }
    set({
      content: "",
      versionNumber: 1,
      currentVersionId: null,
      projectId: null,
      isDirty: false,
      isSaving: false,
      autoSaveTimer: null,
    });
  },
}));