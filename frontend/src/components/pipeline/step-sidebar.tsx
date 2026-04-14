"use client";

import { cn } from "@/lib/utils";
import type { PipelineStep } from "@/types/pipeline";
import { usePipelineStore, isStepReady, DEPENDENCY_MAP, ANALYSIS_STEPS } from "@/stores/pipeline-store";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const STEP_LABELS: Record<string, string> = {
  icp: "ICP Profile",
  subject: "Subject",
  hook: "Hook",
  narrative: "Narrative",
  retention: "Retention",
  cta: "CTA",
  writer: "Writer",
  analysis: "Analysis",
};

const STEP_ORDER = ["icp", "subject", "hook", "narrative", "retention", "cta", "writer", "analysis"];

const VIDEO_FORMATS = new Set(["short_video", "long_video", "vsl", "Short-form Video", "Long-form Video", "VSL"]);

function hasRetention(targetFormat: string | undefined): boolean {
  return targetFormat ? VIDEO_FORMATS.has(targetFormat) : false;
}

interface StepSidebarProps {
  steps: PipelineStep[];
  targetFormat?: string;
}

function getAnalysisStatus(steps: PipelineStep[]): string {
  const statuses = ANALYSIS_STEPS.map((type) => steps.find((s) => s.step_type === type)?.status ?? "pending");
  if (statuses.some((s) => s === "running")) return "running";
  if (statuses.some((s) => s === "failed")) return "failed";
  if (statuses.every((s) => s === "completed")) return "completed";
  return "pending";
}

function StatusIcon({ status }: { status: string }) {
  if (status === "completed") return <span className="size-2 rounded-full bg-green-500" />;
  if (status === "running") return <span className="size-2 rounded-full bg-blue-500 animate-pulse" />;
  if (status === "failed") return <span className="size-2 rounded-full bg-red-500" />;
  return <span className="size-2 rounded-full bg-muted-foreground/30" />;
}

export function StepSidebar({ steps, targetFormat }: StepSidebarProps) {
  const { activeStepType, setActiveStepType } = usePipelineStore();

  const showRetention = hasRetention(targetFormat);

  const getDependencies = (stepType: string): string[] => {
    if (!showRetention && (stepType === "cta" || stepType === "writer")) {
      return DEPENDENCY_MAP[stepType].filter((d) => d !== "retention");
    }
    return DEPENDENCY_MAP[stepType] ?? [];
  };

  const visibleStepTypes = showRetention
    ? STEP_ORDER
    : STEP_ORDER.filter((s) => s !== "retention");

  return (
    <div className="w-48 shrink-0 space-y-1">
      {visibleStepTypes.map((stepType) => {
        const step = steps.find((s) => s.step_type === stepType);
        let status = step?.status ?? "pending";
        
        if (stepType === "analysis") {
          status = getAnalysisStatus(steps);
        }
        
        const ready = isStepReady(stepType, steps, getDependencies(stepType));
        const isActive = activeStepType === stepType;
        const isLocked = !ready && status !== "completed" && status !== "running" && status !== "failed";

        const button = (
          <button
            onClick={() => !isLocked && setActiveStepType(stepType)}
            disabled={isLocked}
            className={cn(
              "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors text-left",
              isActive && "bg-primary/10 text-primary font-medium",
              !isActive && !isLocked && "hover:bg-muted text-foreground",
              isLocked && "text-muted-foreground/50 cursor-not-allowed"
            )}
          >
            <StatusIcon status={isLocked ? "locked" : status} />
            <span>{STEP_LABELS[stepType]}</span>
          </button>
        );

        if (isLocked) {
          const deps = getDependencies(stepType);
          return (
            <Tooltip key={stepType}>
              <TooltipTrigger render={button} />
              <TooltipContent>
                Requires: {deps.join(", ")}
              </TooltipContent>
            </Tooltip>
          );
        }

        return <div key={stepType}>{button}</div>;
      })}
    </div>
  );
}
