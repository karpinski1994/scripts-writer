"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { PipelineStep } from "@/types/pipeline";
import { usePipelineStore, isStepReady, DEPENDENCY_MAP } from "@/stores/pipeline-store";
import { ICPPanel } from "./icp-panel";
import { HookPanel } from "./hook-panel";
import { NarrativePanel } from "./narrative-panel";
import { RetentionPanel } from "./retention-panel";
import { CTAPanel } from "./cta-panel";
import { WriterPanel } from "./writer-panel";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import type { ICPAgentOutput } from "@/types/agents";
import type { HookAgentOutput, HookSuggestion } from "@/types/agents";
import type { NarrativeAgentOutput, NarrativePattern } from "@/types/agents";
import type { RetentionAgentOutput, RetentionTechnique } from "@/types/agents";
import type { CTAAgentOutput, CTASuggestion } from "@/types/agents";

const STEP_LABELS: Record<string, string> = {
  icp: "ICP Profile",
  hook: "Hook",
  narrative: "Narrative",
  retention: "Retention",
  cta: "CTA",
  writer: "Writer",
  factcheck: "Fact Check",
  readability: "Readability",
  copyright: "Copyright",
  policy: "Policy",
};

interface AgentPanelWrapperProps {
  projectId: string;
  steps: PipelineStep[];
}

function parseOutput<T>(step: PipelineStep): T | null {
  if (!step.output_data) return null;
  try {
    return JSON.parse(step.output_data) as T;
  } catch {
    return null;
  }
}

export function AgentPanelWrapper({ projectId, steps }: AgentPanelWrapperProps) {
  const { activeStepType, isRunning } = usePipelineStore();
  const queryClient = useQueryClient();
  const router = useRouter();

  if (!activeStepType) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Select a step to view details</p>
        </CardContent>
      </Card>
    );
  }

  const step = steps.find((s) => s.step_type === activeStepType);
  const ready = isStepReady(activeStepType, steps);
  const running = isRunning[activeStepType] ?? step?.status === "running";

  if (!ready && step?.status !== "completed" && step?.status !== "running" && step?.status !== "failed") {
    const deps = DEPENDENCY_MAP[activeStepType] ?? [];
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-2 py-12">
          <p className="text-lg font-medium text-muted-foreground">{STEP_LABELS[activeStepType]}</p>
          <p className="text-sm text-muted-foreground">Requires: {deps.join(", ")}</p>
        </CardContent>
      </Card>
    );
  }

  if (running) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
          <Loader2 className="size-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Agent is running...</p>
        </CardContent>
      </Card>
    );
  }

  if (step?.status === "pending" || !step) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
          <p className="text-lg font-medium">{STEP_LABELS[activeStepType]}</p>
          <p className="text-sm text-muted-foreground">This step hasn&apos;t been run yet.</p>
          <Button
            onClick={async () => {
              try {
                await api.post(`/api/v1/projects/${projectId}/pipeline/run/${activeStepType}`, {});
              } catch {
                // error handled by query invalidation
              }
              queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
            }}
          >
            Run Agent
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (step.status === "failed") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
          <p className="text-lg font-medium text-destructive">{STEP_LABELS[activeStepType]} Failed</p>
          {step.error_message && (
            <p className="text-sm text-muted-foreground">{step.error_message}</p>
          )}
          <Button
            onClick={async () => {
              try {
                await api.post(`/api/v1/projects/${projectId}/pipeline/run/${activeStepType}`, {});
              } catch {
                // error handled by query invalidation
              }
              queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
            }}
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (step.status !== "completed" || !step.output_data) {
    return null;
  }

  const runAgent = async () => {
    try {
      await api.post(`/api/v1/projects/${projectId}/pipeline/run/${activeStepType}`, {});
    } catch {
      // error handled by query invalidation
    }
    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
  };

  const selectOption = async (selected: unknown) => {
    await api.patch(`/api/v1/projects/${projectId}/pipeline/${step.id}`, {
      selected_option: selected,
    });
    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
  };

  switch (activeStepType) {
    case "icp": {
      const data = parseOutput<ICPAgentOutput>(step);
      if (!data) return null;
      return (
        <ICPPanel
          data={data}
          onApprove={() => selectOption(data.icp)}
          onRerun={runAgent}
          isRunning={running}
          projectId={projectId}
        />
      );
    }
    case "hook": {
      const data = parseOutput<HookAgentOutput>(step);
      if (!data) return null;
      return (
        <HookPanel
          data={data}
          onContinue={(selected: HookSuggestion) => selectOption(selected)}
          onRerun={runAgent}
          isRunning={running}
          projectId={projectId}
        />
      );
    }
    case "narrative": {
      const data = parseOutput<NarrativeAgentOutput>(step);
      if (!data) return null;
      return (
        <NarrativePanel
          data={data}
          onContinue={(selected: NarrativePattern) => selectOption(selected)}
          onRerun={runAgent}
          isRunning={running}
          projectId={projectId}
        />
      );
    }
    case "retention": {
      const data = parseOutput<RetentionAgentOutput>(step);
      if (!data) return null;
      return (
        <RetentionPanel
          data={data}
          onContinue={(selected: RetentionTechnique[]) => selectOption(selected)}
          onRerun={runAgent}
          isRunning={running}
          projectId={projectId}
        />
      );
    }
    case "cta": {
      const data = parseOutput<CTAAgentOutput>(step);
      if (!data) return null;
      return (
        <CTAPanel
          data={data}
          onContinue={(selected: CTASuggestion) => selectOption(selected)}
          onRerun={runAgent}
          isRunning={running}
          projectId={projectId}
        />
      );
    }
    case "writer": {
      return (
        <WriterPanel
          projectId={projectId}
          step={step}
          onRun={async () => {
            try {
              await api.post(`/api/v1/projects/${projectId}/pipeline/run/writer`, {});
            } catch {
              // error handled by query invalidation
            }
            queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
            queryClient.invalidateQueries({ queryKey: ["scripts", projectId] });
          }}
          onNavigateToEditor={() => router.push(`/projects/${projectId}/editor`)}
        />
      );
    }
    default:
      return (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <p className="text-muted-foreground">{STEP_LABELS[activeStepType]} panel coming soon</p>
          </CardContent>
        </Card>
      );
  }
}
