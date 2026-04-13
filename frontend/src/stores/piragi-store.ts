import { create } from "zustand";
import { api } from "@/lib/api";
import type {
  DocumentSummary,
  ConnectDocumentsResponse,
  ConnectedDocuments,
  PiragiQueryResponse,
  PiragiDocumentsResponse,
  UploadDocumentResponse,
} from "@/types/piragi";

interface PiragiStore {
  connectedDocuments: ConnectedDocuments | null;
  stepContexts: Record<string, string>;
  isQuerying: boolean;
  isConnecting: boolean;
  isUploading: boolean;
  categories: DocumentSummary[];
  setConnectedDocuments: (docs: ConnectedDocuments | null) => void;
  setStepContext: (stepType: string, context: string) => void;
  clearStepContexts: () => void;
  fetchCategories: (projectId: string) => Promise<DocumentSummary[]>;
  connectDocuments: (
    projectId: string,
    documentPaths: string
  ) => Promise<ConnectDocumentsResponse | null>;
  disconnectDocuments: (projectId: string) => Promise<void>;
  uploadDocument: (
    projectId: string,
    category: string,
    file: File
  ) => Promise<UploadDocumentResponse | null>;
  queryDocuments: (
    projectId: string,
    query: string,
    stepType: string
  ) => Promise<PiragiQueryResponse | null>;
  reset: () => void;
}

export const usePiragiStore = create<PiragiStore>((set, get) => ({
  connectedDocuments: null,
  stepContexts: {},
  isQuerying: false,
  isConnecting: false,
  isUploading: false,
  categories: [],

  setConnectedDocuments: (docs) => set({ connectedDocuments: docs }),

  setStepContext: (stepType, context) =>
    set((s) => ({ stepContexts: { ...s.stepContexts, [stepType]: context } })),

  clearStepContexts: () => set({ stepContexts: {} }),

  fetchCategories: async (projectId) => {
    try {
      const response = await api.get<PiragiDocumentsResponse>(
        `/api/v1/projects/${projectId}/rag/documents`
      );
      set({ categories: response.categories });
      return response.categories;
    } catch {
      return [];
    }
  },

  connectDocuments: async (projectId, documentPaths) => {
    set({ isConnecting: true });
    try {
      const response = await api.post<ConnectDocumentsResponse>(
        `/api/v1/projects/${projectId}/rag/connect`,
        { document_paths: documentPaths }
      );
      set({
        connectedDocuments: { document_paths: response.document_paths },
        isConnecting: false,
      });
      get().clearStepContexts();
      return response;
    } catch {
      set({ isConnecting: false });
      return null;
    }
  },

  disconnectDocuments: async (projectId) => {
    try {
      await api.delete(`/api/v1/projects/${projectId}/rag/connect`);
      set({ connectedDocuments: null });
      get().clearStepContexts();
    } catch {
      // error silently
    }
  },

  uploadDocument: async (projectId, stepType, file) => {
    set({ isUploading: true });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/projects/${projectId}/rag/upload?step_type=${stepType}`;
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });
      const data = await res.json() as UploadDocumentResponse;
      set({ isUploading: false });
      return data;
    } catch {
      set({ isUploading: false });
      return null;
    }
  },

  queryDocuments: async (projectId, query, stepType) => {
    set({ isQuerying: true });
    try {
      const response = await api.post<PiragiQueryResponse>(
        `/api/v1/projects/${projectId}/rag/query`,
        { query, step_type: stepType }
      );
      set({ isQuerying: false });
      return response;
    } catch {
      set({ isQuerying: false });
      return null;
    }
  },

  reset: () =>
    set({
      connectedDocuments: null,
      stepContexts: {},
      isQuerying: false,
      isConnecting: false,
      isUploading: false,
      categories: [],
    }),
}));