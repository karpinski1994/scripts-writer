"use client";

import { useState } from "react";
import type { NarrativeAgentOutput, NarrativePattern } from "@/types/agents";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { NotebookLMContext } from "@/components/shared/notebooklm-context";

interface NarrativePanelProps {
  data: NarrativeAgentOutput;
  onContinue: (selected: NarrativePattern) => void;
  onRerun: () => void;
  isRunning: boolean;
  projectId: string;
}

export function NarrativePanel({ data, onContinue, onRerun, isRunning, projectId }: NarrativePanelProps) {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  function handleContinue() {
    if (selectedIdx !== null) {
      onContinue(data.patterns[selectedIdx]);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Narrative Patterns</h3>
        <Button variant="outline" size="sm" onClick={onRerun} disabled={isRunning}>
          Re-run
        </Button>
      </div>

      <div className="space-y-2">
        {data.patterns.map((pattern, i) => (
          <button
            key={i}
            onClick={() => setSelectedIdx(i)}
            className={cn(
              "w-full rounded-lg border p-3 text-left transition-colors",
              selectedIdx === i ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{pattern.pattern_name}</span>
              {pattern.fit_score !== undefined && (
                <Badge variant="secondary">Fit: {Math.round(pattern.fit_score * 100)}%</Badge>
              )}
              {i === 0 && <Badge variant="default">Recommended</Badge>}
              {selectedIdx === i && (
                <span className="text-xs text-primary ml-auto">Selected</span>
              )}
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{pattern.description}</p>
            {pattern.structure.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {pattern.structure.map((beat, j) => (
                  <Badge key={j} variant="outline" className="text-xs">{beat}</Badge>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>

      <NotebookLMContext stepType="narrative" projectId={projectId} />

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">Confidence: {Math.round(data.confidence * 100)}%</p>
        <Button onClick={handleContinue} disabled={selectedIdx === null}>
          Continue
        </Button>
      </div>
    </div>
  );
}
