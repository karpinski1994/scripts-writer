"use client";

import { useState } from "react";
import type { HookAgentOutput, HookSuggestion } from "@/types/agents";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { NotebookLMContext } from "@/components/shared/notebooklm-context";

interface HookPanelProps {
  data: HookAgentOutput;
  onContinue: (selected: HookSuggestion) => void;
  onRerun: () => void;
  isRunning: boolean;
  projectId: string;
  initialSelection?: HookSuggestion;
}

export function HookPanel({ data, onContinue, onRerun, isRunning, projectId, initialSelection }: HookPanelProps) {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(() => {
    if (initialSelection) {
      return data.hooks.findIndex(h => h.text === initialSelection.text);
    }
    return null;
  });
  const [customText, setCustomText] = useState("");

  function handleContinue() {
    if (customText.trim()) {
      onContinue({ hook_type: "custom", text: customText.trim(), reasoning: "" });
    } else if (selectedIdx !== null) {
      onContinue(data.hooks[selectedIdx]);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Hook Suggestions</h3>
        <Button variant="outline" size="sm" onClick={onRerun} disabled={isRunning}>
          Re-run
        </Button>
      </div>

      <div className="space-y-2">
        {data.hooks.map((hook, i) => (
          <button
            key={i}
            onClick={() => { setSelectedIdx(i); setCustomText(""); }}
            className={cn(
              "w-full rounded-lg border p-3 text-left transition-colors",
              selectedIdx === i && customText === "" ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
            )}
          >
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{hook.hook_type}</Badge>
              {selectedIdx === i && customText === "" && (
                <span className="text-xs text-primary">Selected</span>
              )}
            </div>
            <p className="mt-1 text-sm font-medium">{hook.text}</p>
            {hook.reasoning && (
              <p className="mt-1 text-xs text-muted-foreground">{hook.reasoning}</p>
            )}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Custom Hook</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Enter your own hook text..."
            value={customText}
            onChange={(e) => { setCustomText(e.target.value); setSelectedIdx(null); }}
          />
        </CardContent>
      </Card>

      <NotebookLMContext stepType="hook" projectId={projectId} />

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">Confidence: {Math.round(data.confidence * 100)}%</p>
        <Button onClick={handleContinue} disabled={selectedIdx === null && !customText.trim()}>
          Continue
        </Button>
      </div>
    </div>
  );
}
