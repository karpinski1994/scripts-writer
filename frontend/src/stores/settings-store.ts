import { create } from "zustand";

interface SettingsStore {
  pendingApiKeys: Record<string, string>;
  pendingEnabled: Record<string, boolean>;
  setApiKey: (provider: string, key: string) => void;
  setEnabled: (provider: string, enabled: boolean) => void;
  resetPending: () => void;
}

export const useSettingsStore = create<SettingsStore>((set) => ({
  pendingApiKeys: {},
  pendingEnabled: {},
  setApiKey: (provider, key) =>
    set((s) => ({ pendingApiKeys: { ...s.pendingApiKeys, [provider]: key } })),
  setEnabled: (provider, enabled) =>
    set((s) => ({
      pendingEnabled: { ...s.pendingEnabled, [provider]: enabled },
    })),
  resetPending: () => set({ pendingApiKeys: {}, pendingEnabled: {} }),
}));
