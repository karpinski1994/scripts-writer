"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { PipelineStep } from "@/types/pipeline";
import type { AnalysisResult } from "@/types/analysis";
import type { AgentType } from "@/types/analysis";
import { usePipelineStore, isStepReady, DEPENDENCY_MAP, ANALYSIS_STEPS } from "@/stores/pipeline-store";
import { ICPPanel } from "./icp-panel";
import { HookPanel } from "./hook-panel";
import { NarrativePanel } from "./narrative-panel";
import { RetentionPanel } from "./retention-panel";
import { CTAPanel } from "./cta-panel";
import { WriterPanel } from "./writer-panel";
import { AnalysisPanel } from "./analysis-panel";
import { StepDocumentDropzone } from "@/components/piragi/step-document-dropzone";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Loader2, TriangleAlert } from "lucide-react";
import type { ICPAgentOutput } from "@/types/agents";
import type { HookAgentOutput, HookSuggestion } from "@/types/agents";
import type { NarrativeAgentOutput, NarrativePattern } from "@/types/agents";
import type { RetentionAgentOutput, RetentionTechnique } from "@/types/agents";
import type { CTAAgentOutput, CTASuggestion } from "@/types/agents";
import type { ProjectDetail } from "@/types/project";

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

const STEP_ORDER_LIST = [
  "icp", "hook", "narrative", "retention", "cta", "writer",
  "factcheck", "readability", "copyright", "policy",
];

function getDownstreamSteps(stepType: string, steps: PipelineStep[]): string[] {
  const idx = STEP_ORDER_LIST.indexOf(stepType);
  if (idx === -1) return [];
  return STEP_ORDER_LIST.slice(idx + 1)
    .filter((st) => steps.some((s) => s.step_type === st && s.status === "completed"))
    .map((st) => STEP_LABELS[st] || st);
}

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
  const [rerunConfirm, setRerunConfirm] = useState<string | null>(null);
  
  const { data: project } = useQuery<ProjectDetail>({
    queryKey: ["project", projectId],
    queryFn: () => api.get(`/api/v1/projects/${projectId}`),
    enabled: !!projectId,
  });

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
    const showDropzone = activeStepType === "icp" || activeStepType === "hook";
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-4 py-8">
          <p className="text-lg font-medium">{STEP_LABELS[activeStepType]}</p>
          {showDropzone && (
            <StepDocumentDropzone projectId={projectId} stepType={activeStepType} className="w-full max-w-md mb-4" />
          )}
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

  const handleRerun = () => {
    const downstream = getDownstreamSteps(activeStepType!, steps);
    if (downstream.length > 0) {
      setRerunConfirm(activeStepType);
    } else {
      runAgent();
    }
  };

  const selectOption = async (selected: unknown) => {
    await api.patch(`/api/v1/projects/${projectId}/pipeline/${step.id}`, {
      selected_option: selected,
    });
    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    const STEP_ORDER = ["icp", "hook", "narrative", "retention", "cta", "writer", "factcheck", "readability", "copyright", "policy"];
    const currentIdx = STEP_ORDER.indexOf(activeStepType || "");
    if (currentIdx >= 0 && currentIdx < STEP_ORDER.length - 1) {
      const nextStep = STEP_ORDER[currentIdx + 1];
      usePipelineStore.getState().setActiveStepType(nextStep);
    }
  };

  switch (activeStepType) {
    case "icp": {
      const data = parseOutput<ICPAgentOutput>(step);
      if (!data) return null;
      return (
        <>
          <ICPPanel
            data={data}
            onApprove={() => selectOption(data.icp)}
            onRerun={handleRerun}
            isRunning={running}
            projectId={projectId}
          />
          <RerunConfirmDialog
            open={rerunConfirm === activeStepType}
            onOpenChange={(o) => !o && setRerunConfirm(null)}
            downstream={getDownstreamSteps(activeStepType, steps)}
            onConfirm={() => { setRerunConfirm(null); runAgent(); }}
          />
        </>
      );
    }
    case "hook": {
      const data = parseOutput<HookAgentOutput>(step);
      if (!data) return null;
      const initialHook = step.selected_option ? JSON.parse(step.selected_option) : undefined;
      console.log("[DEBUG] hook initialSelection:", initialHook, "hooks:", data.hooks?.map(h => h.text?.slice(0, 30)));
      return (
        <>
          <HookPanel
            data={data}
            onContinue={(selected: HookSuggestion) => selectOption(selected)}
            onRerun={handleRerun}
            isRunning={running}
            projectId={projectId}
            initialSelection={initialHook}
          />
          <RerunConfirmDialog
            open={rerunConfirm === activeStepType}
            onOpenChange={(o) => !o && setRerunConfirm(null)}
            downstream={getDownstreamSteps(activeStepType, steps)}
            onConfirm={() => { setRerunConfirm(null); runAgent(); }}
          />
        </>
      );
    }
    case "narrative": {
      const data = parseOutput<NarrativeAgentOutput>(step);
      if (!data) return null;
      const initialNarrative = step.selected_option ? JSON.parse(step.selected_option) : undefined;
      console.log("[DEBUG] narrative initialSelection:", initialNarrative, "patterns:", data.patterns?.map(p => p.pattern_name));
      return (
        <>
          <NarrativePanel
            data={data}
            onContinue={(selected: NarrativePattern) => selectOption(selected)}
            onRerun={handleRerun}
            isRunning={running}
            projectId={projectId}
            stepType={activeStepType}
            initialSelection={initialNarrative}
          />
          <RerunConfirmDialog
            open={rerunConfirm === activeStepType}
            onOpenChange={(o) => !o && setRerunConfirm(null)}
            downstream={getDownstreamSteps(activeStepType, steps)}
            onConfirm={() => { setRerunConfirm(null); runAgent(); }}
          />
        </>
      );
    }
    case "retention": {
      const data = parseOutput<RetentionAgentOutput>(step);
      if (!data) return null;
      const initialRetentions = step.selected_option ? JSON.parse(step.selected_option) : undefined;
      return (
        <>
          <RetentionPanel
            data={data}
            onContinue={(selected: RetentionTechnique[]) => selectOption(selected)}
            onRerun={handleRerun}
            isRunning={running}
            projectId={projectId}
            stepType={activeStepType}
            initialSelections={initialRetentions}
          />
          <RerunConfirmDialog
            open={rerunConfirm === activeStepType}
            onOpenChange={(o) => !o && setRerunConfirm(null)}
            downstream={getDownstreamSteps(activeStepType, steps)}
            onConfirm={() => { setRerunConfirm(null); runAgent(); }}
          />
        </>
      );
    }
    case "cta": {
      const data = parseOutput<CTAAgentOutput>(step);
      if (!data) return null;
      const initialCTA = step.selected_option ? JSON.parse(step.selected_option) : undefined;
      return (
        <>
          <CTAPanel
            data={data}
            onContinue={(selected: CTASuggestion) => selectOption(selected)}
            onRerun={handleRerun}
            isRunning={running}
            projectId={projectId}
            stepType={activeStepType}
            initialSelection={initialCTA}
            ctaPurpose={project?.cta_purpose || undefined}
            onUpdateCtaPurpose={async (purpose: string) => {
              await api.patch(`/api/v1/projects/${projectId}`, { cta_purpose: purpose });
              queryClient.invalidateQueries({ queryKey: ["project", projectId] });
            }}
          />
          <RerunConfirmDialog
            open={rerunConfirm === activeStepType}
            onOpenChange={(o) => !o && setRerunConfirm(null)}
            downstream={getDownstreamSteps(activeStepType, steps)}
            onConfirm={() => { setRerunConfirm(null); runAgent(); }}
          />
        </>
      );
    }
    case "writer": {
      console.log("[DEBUG] writer step:", step);
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
    case "analysis": {
      const lastTab = ANALYSIS_STEPS.find((t) => steps.find((s) => s.step_type === t)?.status === "completed") || "factcheck";
      return (
        <AnalysisPanelWrapper
          projectId={projectId}
          activeTab={lastTab as AgentType}
          steps={steps}
        />
      );
    }
    case "factcheck":
    case "readability":
    case "copyright":
    case "policy": {
      return (
        <AnalysisPanelWrapper
          projectId={projectId}
          activeTab={activeStepType as AgentType}
          steps={steps}
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

const ANALYSIS_AGENT_TYPES: AgentType[] = ["factcheck", "readability", "copyright", "policy"];

function AnalysisPanelWrapper({
  projectId,
  activeTab,
  steps,
}: {
  projectId: string;
  activeTab: AgentType;
  steps: PipelineStep[];
}) {
  const queryClient = useQueryClient();
  const { isRunning } = usePipelineStore();
  const [results, setResults] = useState<AnalysisResult[]>([]);

  const loadingAgents = new Set<string>();
  for (const type of ANALYSIS_AGENT_TYPES) {
    if (isRunning[type] || steps.find((s) => s.step_type === type)?.status === "running") {
      loadingAgents.add(type);
    }
  }

  const runAgent = async (agentType: AgentType) => {
    try {
      const result = await api.post<AnalysisResult>(
        `/api/v1/projects/${projectId}/analysis/${agentType}`,
        {}
      );
      setResults((prev) => {
        const filtered = prev.filter((r) => r.agent_type !== agentType);
        return [...filtered, result];
      });
    } catch {
      // error handled by query invalidation
    }
    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    queryClient.invalidateQueries({ queryKey: ["analysis", projectId] });
  };

  return (
    <AnalysisPanel
      projectId={projectId}
      initialTab={activeTab}
      results={results}
      loadingAgents={loadingAgents}
      onRunAgent={runAgent}
    />
  );
}

function RerunConfirmDialog({
  open,
  onOpenChange,
  downstream,
  onConfirm,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  downstream: string[];
  onConfirm: () => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TriangleAlert className="size-5 text-destructive" />
            Re-run this step?
          </DialogTitle>
          <DialogDescription>
            Re-running will invalidate the following completed downstream steps. They will need to be re-run.
          </DialogDescription>
        </DialogHeader>
        {downstream.length > 0 && (
          <ul className="list-disc pl-5 text-sm text-muted-foreground">
            {downstream.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        )}
        <DialogFooter open={open} onOpenChange={onOpenChange}>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            Re-run
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
