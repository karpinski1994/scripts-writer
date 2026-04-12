"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { ProjectDetail } from "@/types/project";
import type { Pipeline } from "@/types/pipeline";
import type { NotebookSummary } from "@/types/notebooklm";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, BookOpen, Unplug } from "lucide-react";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useNotebookLMStore } from "@/stores/notebooklm-store";
import { useAgentStream } from "@/hooks/use-agent-stream";
import { PipelineView } from "@/components/pipeline/pipeline-view";
import { StepSidebar } from "@/components/pipeline/step-sidebar";
import { AgentPanelWrapper } from "@/components/agents/agent-panel-wrapper";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const { setActiveStepType, setSteps, reset } = usePipelineStore();
  const { connectedNotebook, connectNotebook, disconnectNotebook, fetchNotebooks, notebooks, reset: resetNotebookLM } = useNotebookLMStore();
  const [showConnectDialog, setShowConnectDialog] = useState(false);

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
    return () => { reset(); resetNotebookLM(); };
  }, [reset, resetNotebookLM]);

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
        <Button variant="outline" render={<Link href="/" />}>
          <ArrowLeft />
          Back to Dashboard
        </Button>
      </div>
    );
  }

  if (!project || !pipeline) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon-sm" render={<Link href="/" />}>
          <ArrowLeft />
        </Button>
        <h1 className="text-xl font-bold tracking-tight">{project.name}</h1>
        <Badge variant="secondary">{project.target_format}</Badge>
        {project.content_goal && (
          <Badge variant="outline">{project.content_goal}</Badge>
        )}
        <div className="ml-auto flex items-center gap-2">
          {connectedNotebook ? (
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="gap-1">
                <BookOpen className="size-3" />
                {connectedNotebook.notebook_title}
              </Badge>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => disconnectNotebook(id)}
                title="Disconnect NotebookLM"
              >
                <Unplug className="size-3" />
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                await fetchNotebooks(id);
                setShowConnectDialog(true);
              }}
            >
              <BookOpen className="size-4" />
              Connect NotebookLM
            </Button>
          )}
        </div>
      </div>

      {showConnectDialog && (
        <div className="rounded-md border p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Select a Notebook</h3>
            <Button variant="ghost" size="sm" onClick={() => setShowConnectDialog(false)}>
              Cancel
            </Button>
          </div>
          {notebooks.length === 0 ? (
            <p className="text-sm text-muted-foreground">No notebooks found.</p>
          ) : (
            <div className="space-y-1">
              {notebooks.map((nb: NotebookSummary) => (
                <button
                  key={nb.id}
                  className="w-full rounded-md border px-3 py-2 text-left text-sm hover:bg-muted transition-colors"
                  onClick={async () => {
                    await connectNotebook(id, nb.id);
                    setShowConnectDialog(false);
                  }}
                >
                  {nb.title || nb.id}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <PipelineView steps={pipeline.steps} />

      <div className="flex gap-4">
        <StepSidebar steps={pipeline.steps} />
        <div className="flex-1 min-w-0">
          <AgentPanelWrapper projectId={id} steps={pipeline.steps} />
        </div>
      </div>
    </div>
  );
}
