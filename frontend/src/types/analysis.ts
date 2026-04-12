export type AgentType = "factcheck" | "readability" | "copyright" | "policy";

export interface Finding {
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  text: string;
  suggestion: string;
  confidence: number;
}

export interface AnalysisResult {
  id: string;
  project_id: string;
  script_version_id: string;
  agent_type: AgentType;
  findings: Finding[];
  overall_score: number | null;
  created_at: string;
}
