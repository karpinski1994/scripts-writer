"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { ProjectDetail } from "@/types/project";
import type { Pipeline } from "@/types/pipeline";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, FileText, GitBranch } from "lucide-react";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useAgentStream } from "@/hooks/use-agent-stream";
import { PipelineView } from "@/components/pipeline/pipeline-view";
import { StepSidebar } from "@/components/pipeline/step-sidebar";
import { AgentPanelWrapper } from "@/components/agents/agent-panel-wrapper";
import { ExportPanel } from "@/components/shared/export-panel";
import { BranchDialog } from "@/components/shared/branch-dialog";
import { ErrorBoundary } from "@/components/shared/error-boundary";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const { setActiveStepType, setSteps, reset } = usePipelineStore();
  const [showBranchDialog, setShowBranchDialog] = useState(false);

  const {
    data: project,
    isLoading: projectLoading,
    error: projectError,
  } = useQuery<ProjectDetail>({
    queryKey: ["project", id],
    queryFn: () => api.get<ProjectDetail>(`/api/v1/projects/${id}`),
    enabled: !!id,
  });

  const {
    data: pipeline,
    isLoading: pipelineLoading,
  } = useQuery<Pipeline>({
    queryKey: ["pipeline", id],
    queryFn: () => api.get<Pipeline>(`/api/v1/projects/${id}/pipeline`),
    enabled: !!id,
  });

  useAgentStream(id);

  const hasRunningStep = pipeline?.steps?.some((s) => s.status === "running");
  const hasFailedStep = pipeline?.steps?.some((s) => s.status === "failed");

  useEffect(() => {
    if (hasRunningStep && id) {
      api.post(`/api/v1/projects/${id}/pipeline/cancel`, {}).catch(() => {});
    }
  }, [id, hasRunningStep]);

  useEffect(() => {
    if (hasFailedStep && id) {
      api.post(`/api/v1/projects/${id}/pipeline/reset-errors`, {}).catch(() => {});
    }
  }, [id, hasFailedStep]);

  useEffect(() => {
    if (pipeline?.steps) {
      setSteps(pipeline.steps);
      const firstPending = pipeline.steps.find(
        (s) => s.status === "pending" || s.status === "failed"
      );
      if (firstPending && !usePipelineStore.getState().activeStepType) {
        setActiveStepType(firstPending.step_type);
      }
    }
  }, [pipeline, setSteps, setActiveStepType]);

  useEffect(() => {
    return () => { reset(); };
  }, [reset]);

  if (projectLoading || pipelineLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (projectError && projectError instanceof ApiError && projectError.status === 404) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24">
        <p className="text-lg text-muted-foreground">Project not found</p>
        <Button asChild variant="outline">
          <Link href="/">
            <ArrowLeft />
            Back to Dashboard
          </Link>
        </Button>
      </div>
    );
  }

  if (!project || !pipeline) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="icon-sm">
          <Link href="/">
            <ArrowLeft />
          </Link>
        </Button>
        <h1 className="text-xl font-bold tracking-tight">{project.name}</h1>
        <Badge variant="secondary">{project.target_format}</Badge>
        {project.content_goal && (
          <Badge variant="outline">{project.content_goal}</Badge>
        )}
        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowBranchDialog(true)}
          >
            <GitBranch className="size-4" />
            Branch
          </Button>
        </div>
      </div>

      <PipelineView steps={pipeline.steps} />

      <div className="flex gap-4">
        <StepSidebar steps={pipeline.steps} />
        <div className="flex-1 min-w-0">
          <ErrorBoundary>
            {pipeline.steps.every((s) => s.status === "pending") && (
              <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed py-8">
                <p className="text-sm text-muted-foreground">Run ICP Agent to get started</p>
              </div>
            )}
            <AgentPanelWrapper projectId={id} steps={pipeline.steps} />
          </ErrorBoundary>
        </div>
      </div>

      {pipeline.steps.some((s) => s.step_type === "writer" && s.status === "completed") && (
        <ExportPanel projectId={id} />
      )}

      <BranchDialog
        open={showBranchDialog}
        onOpenChange={setShowBranchDialog}
        projectId={id}
        steps={pipeline.steps}
        projectName={project.name}
      />
    </div>
  );
}
