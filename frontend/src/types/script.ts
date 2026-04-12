export interface ScriptVersion {
  id: string;
  project_id: string;
  version_number: number;
  content: string;
  format: string;
  hook_text?: string | null;
  narrative_pattern?: string | null;
  cta_text?: string | null;
  created_at: string;
}

export interface ScriptUpdateRequest {
  content: string;
}
