export type TargetFormat =
  | "VSL"
  | "YouTube"
  | "Tutorial"
  | "Facebook"
  | "LinkedIn"
  | "Blog";

export type ContentGoal =
  | "Sell"
  | "Educate"
  | "Entertain"
  | "Build Authority";

export interface ProjectSummary {
  id: string;
  name: string;
  target_format: TargetFormat;
  status: string;
  updated_at: string;
}

export interface ProjectDetail {
  id: string;
  name: string;
  topic: string;
  target_format: TargetFormat;
  content_goal: ContentGoal | null;
  raw_notes: string;
  status: string;
  current_step: number;
  notebooklm_notebook_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateInput {
  name: string;
  topic: string;
  target_format: TargetFormat;
  content_goal?: ContentGoal | null;
  raw_notes: string;
}
