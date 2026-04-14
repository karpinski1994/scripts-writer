"use client";

import { useState, useEffect, useRef } from "react";
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
import { SubjectPanel } from "./subject-panel";
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
  subject: "Subject",
  hook: "Hook",
  narrative: "Narrative",
  retention: "Retention",
  cta: "CTA",
  writer: "Writer",
  analysis: "Analysis",
  factcheck: "Fact Check",
  readability: "Readability",
  copyright: "Copyright",
  policy: "Policy",
};

const STEP_ORDER_LIST = [
  "icp", "subject", "hook", "narrative", "retention", "cta", "writer",
  "analysis", "factcheck", "readability", "copyright", "policy",
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
  targetFormat?: string;
}

function parseOutput<T>(step: PipelineStep): T | null {
  if (!step.output_data) return null;
  try {
    return JSON.parse(step.output_data) as T;
  } catch {
    return null;
  }
}

export function AgentPanelWrapper({ projectId, steps, targetFormat }: AgentPanelWrapperProps) {
  const { activeStepType, isRunning } = usePipelineStore();
  const queryClient = useQueryClient();
  const router = useRouter();

  const showRetention = targetFormat && new Set(["short_video", "long_video", "vsl", "Short-form Video", "Long-form Video", "VSL"]).has(targetFormat);
  const [rerunConfirm, setRerunConfirm] = useState<string | null>(null);
  // Tracks which step we already sent an auto-run request for (prevents duplicates)
  const autoRunTriggeredRef = useRef<string | null>(null);
  const prevActiveStepRef = useRef<string | null>(null);

  const { data: project } = useQuery<ProjectDetail>({
    queryKey: ["project", projectId],
    queryFn: () => api.get(`/api/v1/projects/${projectId}`),
    enabled: !!projectId,
  });

  const step = activeStepType ? steps.find((s) => s.step_type === activeStepType) : undefined;

  const getDependencies = (stepType: string): string[] => {
    const deps = DEPENDENCY_MAP[stepType] ?? [];
    if (!showRetention && (stepType === "cta" || stepType === "writer")) {
      return deps.filter((d) => d !== "retention");
    }
    return deps;
  };

  const ready = activeStepType ? isStepReady(activeStepType, steps, getDependencies(activeStepType)) : false;
  const running = activeStepType ? (isRunning[activeStepType] ?? step?.status === "running") : false;

  // Auto-run agent steps that are pending and have all dependencies met
  const AUTO_RUN_STEPS = ["hook", "narrative", "retention", "cta"];
  const isPending = step?.status === "pending" || !step;
  const shouldAutoRun =
    !!activeStepType &&
    AUTO_RUN_STEPS.includes(activeStepType) &&
    ready &&
    !running &&
    isPending;

  // Reset the auto-run guard when switching to a different step
  if (activeStepType !== prevActiveStepRef.current) {
    prevActiveStepRef.current = activeStepType;
    autoRunTriggeredRef.current = null;
  }

  useEffect(() => {
    if (!shouldAutoRun || !activeStepType) return;
    // Prevent duplicate triggers for the same step
    if (autoRunTriggeredRef.current === activeStepType) return;
    autoRunTriggeredRef.current = activeStepType;

    console.log(`[AGENT-PANEL] Auto-running agent for pending step: ${activeStepType}`);
    api
      .post(`/api/v1/projects/${projectId}/pipeline/run/${activeStepType}`, {})
      .then(() => {
        queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
      })
      .catch((err) => {
        console.error(`[AGENT-PANEL] Auto-run failed for ${activeStepType}:`, err);
        autoRunTriggeredRef.current = null; // Allow retry on failure
        queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
      });
  }, [shouldAutoRun, activeStepType, projectId]);

  if (!activeStepType) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Select a step to view details</p>
        </CardContent>
      </Card>
    );
  }

  if (!ready && step?.status !== "completed" && step?.status !== "running" && step?.status !== "failed") {
    const deps = getDependencies(activeStepType);
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
    if (activeStepType === "subject") {
      return <SubjectPanel projectId={projectId} />;
    }

    if (["factcheck", "readability", "copyright", "policy"].includes(activeStepType)) {
      return (
        <AnalysisPanelWrapper
          projectId={projectId}
          activeTab={activeStepType as AgentType}
          steps={steps}
        />
      );
    }

    // For auto-run steps, show loading while the agent is being triggered
    if (AUTO_RUN_STEPS.includes(activeStepType) && ready) {
      return (
        <Card>
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
            <Loader2 className="size-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Starting {STEP_LABELS[activeStepType]} agent...</p>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Waiting for previous steps...</p>
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

  if (activeStepType === "subject") {
    return <SubjectPanel projectId={projectId} />;
  }

  if (step.status !== "completed" || !step.output_data) {
    return null;
  }

  const runAgent = async () => {
    console.log(`[AGENT-PANEL] Running agent for step: ${activeStepType}, projectId: ${projectId}`);
    try {
      console.log(`[AGENT-PANEL] Sending POST to /api/v1/projects/{projectId}/pipeline/run/${activeStepType}`);
      await api.post(`/api/v1/projects/${projectId}/pipeline/run/${activeStepType}`, {});
      console.log(`[AGENT-PANEL] Agent triggered successfully for step: ${activeStepType}`);
    } catch (err) {
      console.error(`[AGENT-PANEL] Failed to run agent for ${activeStepType}:`, err);
      // error handled by query invalidation
    }
    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
  };

  const handleRerun = () => {
    const downstream = getDownstreamSteps(activeStepType!, steps);
    console.log(`[AGENT-PANEL] HandleRerun - step: ${activeStepType}, downstream: ${downstream.join(", ")}`);
    if (downstream.length > 0) {
      setRerunConfirm(activeStepType);
    } else {
      runAgent();
    }
  };

  const selectOption = async (selected: unknown) => {
    console.log(`[AGENT-PANEL] Selecting option for step: ${activeStepType}, stepId: ${step?.id}`);
    console.log(`[AGENT-PANEL] Selected data:`, selected);

    await api.patch(`/api/v1/projects/${projectId}/pipeline/${step.id}`, {
      selected_option: selected,
    });
    console.log(`[AGENT-PANEL] Option selected successfully`);

    queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    const FULL_STEP_ORDER = ["icp", "subject", "hook", "narrative", "retention", "cta", "writer", "factcheck", "readability", "copyright", "policy"];
    const stepOrder = showRetention ? FULL_STEP_ORDER : FULL_STEP_ORDER.filter((s) => s !== "retention");
    const currentIdx = stepOrder.indexOf(activeStepType || "");
    if (currentIdx >= 0 && currentIdx < stepOrder.length - 1) {
      const nextStep = stepOrder[currentIdx + 1];
      console.log(`[AGENT-PANEL] Auto-advancing to next step: ${nextStep}`);
      usePipelineStore.getState().setActiveStepType(nextStep);
    }
  };

  switch (activeStepType) {
    case "subject": {
      return <SubjectPanel projectId={projectId} />;
    }
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
