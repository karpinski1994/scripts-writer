import { create } from "zustand";

interface ProjectStore {
  activeProjectId: string | null;
  setActiveProject: (id: string | null) => void;
  reset: () => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  activeProjectId: null,
  setActiveProject: (id) => set({ activeProjectId: id }),
  reset: () => set({ activeProjectId: null }),
}));
