"use client";

import { useState } from "react";
import type { RetentionAgentOutput, RetentionTechnique } from "@/types/agents";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface RetentionPanelProps {
  data: RetentionAgentOutput;
  onContinue: (selected: RetentionTechnique[]) => void;
  onRerun: () => void;
  isRunning: boolean;
}

export function RetentionPanel({ data, onContinue, onRerun, isRunning }: RetentionPanelProps) {
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());

  function toggle(i: number) {
    setSelectedIndices((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  }

  function handleContinue() {
    const selected = Array.from(selectedIndices).map((i) => data.techniques[i]);
    onContinue(selected);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Retention Techniques</h3>
        <Button variant="outline" size="sm" onClick={onRerun} disabled={isRunning}>
          Re-run
        </Button>
      </div>

      <div className="space-y-2">
        {data.techniques.map((tech, i) => (
          <button
            key={i}
            onClick={() => toggle(i)}
            className={cn(
              "w-full rounded-lg border p-3 text-left transition-colors",
              selectedIndices.has(i) ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{tech.technique_name}</span>
              {selectedIndices.has(i) && (
                <span className="text-xs text-primary ml-auto">Selected</span>
              )}
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{tech.description}</p>
            {tech.placement_hint && (
              <p className="mt-1 text-xs text-muted-foreground">
                Placement: {tech.placement_hint}
              </p>
            )}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">Confidence: {Math.round(data.confidence * 100)}%</p>
        <Button onClick={handleContinue} disabled={selectedIndices.size === 0}>
          Continue
        </Button>
      </div>
    </div>
  );
}
