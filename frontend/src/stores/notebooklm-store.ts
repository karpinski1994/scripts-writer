import { create } from "zustand";
import { api } from "@/lib/api";
import type { NotebookSummary, ConnectNotebookResponse, ConnectedNotebook } from "@/types/notebooklm";

interface NotebookLMStore {
  connectedNotebook: ConnectedNotebook | null;
  stepContexts: Record<string, string>;
  isQuerying: boolean;
  isConnecting: boolean;
  notebooks: NotebookSummary[];
  setConnectedNotebook: (notebook: ConnectedNotebook | null) => void;
  setStepContext: (stepType: string, context: string) => void;
  clearStepContexts: () => void;
  fetchNotebooks: (projectId: string) => Promise<NotebookSummary[]>;
  connectNotebook: (projectId: string, notebookId: string) => Promise<ConnectNotebookResponse | null>;
  disconnectNotebook: (projectId: string) => Promise<void>;
  queryNotebook: (projectId: string, query: string) => Promise<string | null>;
  fetchStepContext: (projectId: string, stepType: string) => Promise<string | null>;
  reset: () => void;
}

export const useNotebookLMStore = create<NotebookLMStore>((set, get) => ({
  connectedNotebook: null,
  stepContexts: {},
  isQuerying: false,
  isConnecting: false,
  notebooks: [],

  setConnectedNotebook: (notebook) => set({ connectedNotebook: notebook }),

  setStepContext: (stepType, context) =>
    set((s) => ({ stepContexts: { ...s.stepContexts, [stepType]: context } })),

  clearStepContexts: () => set({ stepContexts: {} }),

  fetchNotebooks: async (projectId) => {
    try {
      const notebooks = await api.get<NotebookSummary[]>(
        `/api/v1/projects/${projectId}/notebooklm/notebooks`
      );
      set({ notebooks });
      return notebooks;
    } catch {
      return [];
    }
  },

  connectNotebook: async (projectId, notebookId) => {
    set({ isConnecting: true });
    try {
      const response = await api.post<ConnectNotebookResponse>(
        `/api/v1/projects/${projectId}/notebooklm/connect`,
        { notebook_id: notebookId }
      );
      set({
        connectedNotebook: {
          notebook_id: response.notebook_id,
          notebook_title: response.notebook_title,
        },
        isConnecting: false,
      });
      get().clearStepContexts();
      return response;
    } catch {
      set({ isConnecting: false });
      return null;
    }
  },

  disconnectNotebook: async (projectId) => {
    try {
      await api.delete(`/api/v1/projects/${projectId}/notebooklm/connect`);
      set({ connectedNotebook: null });
      get().clearStepContexts();
    } catch {
      // error silently
    }
  },

  queryNotebook: async (projectId, query) => {
    try {
      const response = await api.post<{ answer: string }>(
        `/api/v1/projects/${projectId}/notebooklm/query`,
        { query }
      );
      return response.answer;
    } catch {
      return null;
    }
  },

  fetchStepContext: async (projectId, stepType) => {
    const existing = get().stepContexts[stepType];
    if (existing) return existing;
    set({ isQuerying: true });
    try {
      const answer = await get().queryNotebook(projectId, stepType);
      if (answer) {
        get().setStepContext(stepType, answer);
      }
      return answer;
    } finally {
      set({ isQuerying: false });
    }
  },

  reset: () =>
    set({
      connectedNotebook: null,
      stepContexts: {},
      isQuerying: false,
      isConnecting: false,
      notebooks: [],
    }),
}));
