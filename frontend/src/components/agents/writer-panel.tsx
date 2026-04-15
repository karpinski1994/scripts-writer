"use client";

import type { PipelineStep } from "@/types/pipeline";
import type { WriterAgentOutput } from "@/types/agents";
import { usePipelineStore } from "@/stores/pipeline-store";
import { StreamingText } from "@/components/shared/streaming-text";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, FileText, RotateCw } from "lucide-react";

interface WriterPanelProps {
  projectId: string;
  step: PipelineStep;
  onRun: () => void;
  onNavigateToEditor: () => void;
}

function parseOutput(step: PipelineStep): WriterAgentOutput | null {
  if (!step.output_data) return null;
  try {
    return JSON.parse(step.output_data) as WriterAgentOutput;
  } catch {
    return null;
  }
}

export function WriterPanel({
  step,
  onRun,
  onNavigateToEditor,
}: WriterPanelProps) {
  const { streamingOutput, isRunning, setActiveStepType } = usePipelineStore();
  const running = isRunning["writer"] ?? step.status === "running";
  const streaming = streamingOutput["writer"];
  const data = parseOutput(step);
  console.log("[DEBUG] WriterPanel step.output_data:", step.output_data);
  console.log("[DEBUG] WriterPanel parsed data:", data);

  if (running) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="size-4 animate-spin" />
            Generating script...
          </CardTitle>
        </CardHeader>
        <CardContent>
          {streaming && <StreamingText text={streaming} isActive />}
        </CardContent>
      </Card>
    );
  }

  if (step.status === "pending") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
          <FileText className="size-12 text-muted-foreground" />
          <p className="text-lg font-medium">Script Writer</p>
          <p className="text-sm text-muted-foreground">
            Generate a script based on your ICP, hook, narrative, retention, and CTA selections.
          </p>
          <Button onClick={onRun}>Generate Script</Button>
        </CardContent>
      </Card>
    );
  }

  if (step.status === "failed") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
          <p className="text-lg font-medium text-destructive">Script Generation Failed</p>
          {step.error_message && (
            <p className="text-sm text-muted-foreground">{step.error_message}</p>
          )}
          <Button onClick={onRun}>Retry</Button>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const preview = data.script.content.slice(0, 500);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="size-4" />
          Script Generated
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-md border bg-muted/50 p-3">
          <p className="text-sm whitespace-pre-wrap">
            {preview}
            {data.script.content.length > 500 && "..."}
          </p>
        </div>
        <p className="text-xs text-muted-foreground">
          {data.script.word_count} words
        </p>
        <div className="flex gap-2">
          <Button onClick={() => setActiveStepType("analysis")}>Continue to Analysis</Button>
          <Button onClick={onNavigateToEditor}>Open in Editor</Button>
          <Button variant="outline" onClick={onRun}>
            <RotateCw className="size-4" />
            Regenerate
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
