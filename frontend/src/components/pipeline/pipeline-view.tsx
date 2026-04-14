"use client";

import { cn } from "@/lib/utils";
import type { PipelineStep } from "@/types/pipeline";
import { usePipelineStore, isStepReady, ANALYSIS_STEPS } from "@/stores/pipeline-store";

const CREATIVE_STEPS = ["icp", "hook", "narrative", "retention", "cta", "writer"];
const ANALYSIS_STEP = "analysis";

const STEP_LABELS: Record<string, string> = {
  icp: "ICP",
  hook: "Hook",
  narrative: "Narrative",
  retention: "Retention",
  cta: "CTA",
  writer: "Writer",
  analysis: "Analysis",
};

function getAnalysisStatus(steps: PipelineStep[]): string {
  const statuses = ANALYSIS_STEPS.map((type) => steps.find((s) => s.step_type === type)?.status ?? "pending");
  if (statuses.some((s) => s === "running")) return "running";
  if (statuses.some((s) => s === "failed")) return "failed";
  if (statuses.every((s) => s === "completed")) return "completed";
  return "pending";
}

function StatusIcon({ status }: { status: string }) {
  if (status === "completed") return <span className="text-green-500">✓</span>;
  if (status === "running") return <span className="text-blue-500 animate-pulse">●</span>;
  if (status === "failed") return <span className="text-red-500">✗</span>;
  return <span className="text-muted-foreground">○</span>;
}

interface PipelineViewProps {
  steps: PipelineStep[];
}

export function PipelineView({ steps }: PipelineViewProps) {
  const { activeStepType, setActiveStepType } = usePipelineStore();

  function getStepStatus(stepType: string): string {
    const step = steps.find((s) => s.step_type === stepType);
    if (!step) return "pending";
    if (step.status === "running") return "running";
    if (step.status === "completed") return "completed";
    if (step.status === "failed") return "failed";
    if (isStepReady(stepType, steps)) return "pending";
    return "locked";
  }

  function getAnalysisStepStatus(): string {
    return getAnalysisStatus(steps);
  }

  function renderRow(stepTypes: string[], label: string) {
    return (
      <div className="space-y-1.5">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <div className="flex items-center gap-1.5">
          {stepTypes.map((stepType, i) => {
            let status: string;
            let isLocked: boolean;
            
            if (stepType === ANALYSIS_STEP) {
              status = getAnalysisStepStatus();
              isLocked = !isStepReady("analysis", steps) && status !== "completed" && status !== "running" && status !== "failed";
            } else {
              status = getStepStatus(stepType);
              isLocked = status === "locked";
            }
            
            const isActive = activeStepType === stepType || 
              (stepType === ANALYSIS_STEP && (activeStepType === "factcheck" || activeStepType === "readability" || activeStepType === "copyright" || activeStepType === "policy"));
            
            return (
              <div key={stepType} className="flex items-center gap-1.5">
                {i > 0 && (
                  <div
                    className={cn(
                      "h-px w-4",
                      isLocked ? "bg-muted" : "bg-border"
                    )}
                  />
                )}
                <button
                  onClick={() => !isLocked && setActiveStepType(stepType)}
                  disabled={isLocked}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
                    isActive && "border-primary bg-primary/10 text-primary",
                    !isActive && status === "completed" && "border-green-500/30 bg-green-500/5 text-green-700 dark:text-green-400",
                    !isActive && status === "running" && "border-blue-500/30 bg-blue-500/5 text-blue-700 dark:text-blue-400",
                    !isActive && status === "failed" && "border-red-500/30 bg-red-500/5 text-red-700 dark:text-red-400",
                    !isActive && status === "pending" && "border-border bg-background text-foreground hover:bg-muted",
                    isLocked && "cursor-not-allowed opacity-40"
                  )}
                >
                  <StatusIcon status={status} />
                  {STEP_LABELS[stepType]}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {renderRow(CREATIVE_STEPS, "Creative")}
      {renderRow([ANALYSIS_STEP], "Analysis")}
    </div>
  );
}
