"use client";

import { useState } from "react";
import type { AgentType, Finding, AnalysisResult } from "@/types/analysis";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Shield, BookOpen, Copyright, ScrollText } from "lucide-react";

const AGENT_LABELS: Record<AgentType, string> = {
  factcheck: "Fact Check",
  readability: "Readability",
  copyright: "Copyright",
  policy: "Policy",
};

const AGENT_ICONS: Record<AgentType, React.ReactNode> = {
  factcheck: <Shield className="size-4" />,
  readability: <BookOpen className="size-4" />,
  copyright: <Copyright className="size-4" />,
  policy: <ScrollText className="size-4" />,
};

const SEVERITY_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  low: "secondary",
  medium: "default",
  high: "destructive",
  critical: "destructive",
};

interface AnalysisPanelProps {
  projectId: string;
  initialTab?: AgentType;
  results: AnalysisResult[];
  loadingAgents: Set<string>;
  onRunAgent: (agentType: AgentType) => void;
}

function ScoreGauge({ label, score, max = 20 }: { label: string; score: number; max?: number }) {
  const pct = Math.min(Math.max((score / max) * 100, 0), 100);
  const color = score <= 8 ? "bg-green-500" : score <= 12 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{score}</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function FindingCard({ finding, onDismiss }: { finding: Finding; onDismiss?: () => void }) {
  return (
    <div className="rounded-lg border p-3 space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={SEVERITY_VARIANT[finding.severity] ?? "secondary"}>
            {finding.severity}
          </Badge>
          <span className="text-xs text-muted-foreground">{finding.type}</span>
        </div>
        {onDismiss && (
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={onDismiss}>
            Dismiss
          </Button>
        )}
      </div>
      <p className="text-sm">{finding.text}</p>
      {finding.suggestion && (
        <p className="text-xs text-muted-foreground">Suggestion: {finding.suggestion}</p>
      )}
    </div>
  );
}

export function AnalysisPanel({
  projectId,
  initialTab = "factcheck",
  results,
  loadingAgents,
  onRunAgent,
}: AnalysisPanelProps) {
  const [activeTab, setActiveTab] = useState<AgentType>(initialTab);
  const [dismissedFindings, setDismissedFindings] = useState<Set<string>>(new Set());

  const currentResult = results.find((r) => r.agent_type === activeTab);
  const isLoading = loadingAgents.has(activeTab);
  const visibleFindings = currentResult?.findings.filter(
    (f) => !dismissedFindings.has(`${activeTab}-${f.text}`)
  ) ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-1.5">
          {(Object.keys(AGENT_LABELS) as AgentType[]).map((type) => (
            <Button
              key={type}
              variant={activeTab === type ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveTab(type)}
              className="flex items-center gap-1.5"
            >
              {AGENT_ICONS[type]}
              {AGENT_LABELS[type]}
            </Button>
          ))}
        </div>

        {isLoading && (
          <div className="flex flex-col items-center justify-center gap-2 py-8">
            <Loader2 className="size-6 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Running {AGENT_LABELS[activeTab]}...</p>
          </div>
        )}

        {!isLoading && !currentResult && (
          <div className="flex flex-col items-center justify-center gap-3 py-8">
            <p className="text-sm text-muted-foreground">
              No {AGENT_LABELS[activeTab]} results yet.
            </p>
            <Button size="sm" onClick={() => onRunAgent(activeTab)}>
              Run {AGENT_LABELS[activeTab]}
            </Button>
          </div>
        )}

        {!isLoading && currentResult && (
          <div className="space-y-3">
            {activeTab === "readability" && currentResult.overall_score !== null && (
              <div className="rounded-lg border bg-muted/50 p-3 space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Readability Scores</p>
                <ScoreGauge
                  label="Flesch-Kincaid Grade Level"
                  score={
                    (currentResult.findings as unknown as Record<string, number>)?.flesch_kincaid_score
                    ?? currentResult.overall_score
                  }
                />
                <ScoreGauge
                  label="Gunning Fog Index"
                  score={
                    (currentResult.findings as unknown as Record<string, number>)?.gunning_fog_score
                    ?? currentResult.overall_score
                  }
                />
              </div>
            )}
            {visibleFindings.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                No issues found.
              </p>
            )}
            {visibleFindings.map((finding, i) => (
              <FindingCard
                key={`${activeTab}-${i}`}
                finding={finding}
                onDismiss={() =>
                  setDismissedFindings((prev) => {
                    const next = new Set(prev);
                    next.add(`${activeTab}-${finding.text}`);
                    return next;
                  })
                }
              />
            ))}
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onRunAgent(activeTab)}
              >
                Re-run {AGENT_LABELS[activeTab]}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
