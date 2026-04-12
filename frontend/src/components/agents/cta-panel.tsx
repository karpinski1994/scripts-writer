"use client";

import { useState } from "react";
import type { CTAAgentOutput, CTASuggestion } from "@/types/agents";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface CTAPanelProps {
  data: CTAAgentOutput;
  onContinue: (selected: CTASuggestion) => void;
  onRerun: () => void;
  isRunning: boolean;
}

export function CTAPanel({ data, onContinue, onRerun, isRunning }: CTAPanelProps) {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [customText, setCustomText] = useState("");

  function handleContinue() {
    if (customText.trim()) {
      onContinue({ cta_type: "custom", text: customText.trim(), reasoning: "" });
    } else if (selectedIdx !== null) {
      onContinue(data.ctas[selectedIdx]);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">CTA Suggestions</h3>
        <Button variant="outline" size="sm" onClick={onRerun} disabled={isRunning}>
          Re-run
        </Button>
      </div>

      <div className="space-y-2">
        {data.ctas.map((cta, i) => (
          <button
            key={i}
            onClick={() => { setSelectedIdx(i); setCustomText(""); }}
            className={cn(
              "w-full rounded-lg border p-3 text-left transition-colors",
              selectedIdx === i && customText === "" ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
            )}
          >
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{cta.cta_type}</Badge>
              {selectedIdx === i && customText === "" && (
                <span className="text-xs text-primary">Selected</span>
              )}
            </div>
            <p className="mt-1 text-sm font-medium">{cta.text}</p>
            {cta.reasoning && (
              <p className="mt-1 text-xs text-muted-foreground">{cta.reasoning}</p>
            )}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Custom CTA</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Enter your own CTA text..."
            value={customText}
            onChange={(e) => { setCustomText(e.target.value); setSelectedIdx(null); }}
          />
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">Confidence: {Math.round(data.confidence * 100)}%</p>
        <Button onClick={handleContinue} disabled={selectedIdx === null && !customText.trim()}>
          Continue
        </Button>
      </div>
    </div>
  );
}
