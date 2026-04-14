import { create } from "zustand";
import type { PipelineStep } from "@/types/pipeline";

export const DEPENDENCY_MAP: Record<string, string[]> = {
  icp: [],
  hook: ["icp"],
  narrative: ["icp", "hook"],
  retention: ["icp", "narrative"],
  cta: ["icp", "hook", "narrative"],
  writer: ["icp", "hook", "narrative", "retention", "cta"],
  analysis: ["writer"],
  factcheck: ["writer"],
  readability: ["writer"],
  copyright: ["writer"],
  policy: ["writer"],
};

export const ANALYSIS_STEPS = ["factcheck", "readability", "copyright", "policy"];

interface PipelineStore {
  activeStepType: string | null;
  steps: PipelineStep[];
  streamingOutput: Record<string, string>;
  isRunning: Record<string, boolean>;
  setActiveStepType: (stepType: string | null) => void;
  setSteps: (steps: PipelineStep[]) => void;
  setStepRunning: (stepType: string) => void;
  setStepCompleted: (stepType: string, outputData: unknown) => void;
  setStepFailed: (stepType: string) => void;
  setStreamingOutput: (stepType: string, output: string) => void;
  reset: () => void;
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  activeStepType: null,
  steps: [],
  streamingOutput: {},
  isRunning: {},

  setActiveStepType: (stepType) => set({ activeStepType: stepType }),
  setSteps: (steps) => set({ steps }),
  setStepRunning: (stepType) =>
    set((s) => ({
      isRunning: { ...s.isRunning, [stepType]: true },
      steps: s.steps.map((st) =>
        st.step_type === stepType ? { ...st, status: "running" } : st
      ),
    })),
  setStepCompleted: (stepType, outputData) =>
    set((s) => ({
      isRunning: { ...s.isRunning, [stepType]: false },
      steps: s.steps.map((st) =>
        st.step_type === stepType
          ? { ...st, status: "completed", output_data: JSON.stringify(outputData) }
          : st
      ),
    })),
  setStepFailed: (stepType) =>
    set((s) => ({
      isRunning: { ...s.isRunning, [stepType]: false },
      steps: s.steps.map((st) =>
        st.step_type === stepType ? { ...st, status: "failed" } : st
      ),
    })),
  setStreamingOutput: (stepType, output) =>
    set((s) => ({
      streamingOutput: { ...s.streamingOutput, [stepType]: output },
    })),
  reset: () =>
    set({
      activeStepType: null,
      steps: [],
      streamingOutput: {},
      isRunning: {},
    }),
}));

export function isStepReady(stepType: string, steps: PipelineStep[]): boolean {
  const deps = DEPENDENCY_MAP[stepType] ?? [];
  return deps.every((dep) =>
    steps.some((s) => s.step_type === dep && s.status === "completed")
  );
}
