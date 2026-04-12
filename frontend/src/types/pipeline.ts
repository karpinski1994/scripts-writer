export interface PipelineStep {
  id: string;
  step_type: string;
  step_order: number;
  status: string;
  output_data?: string | null;
  selected_option?: string | null;
  duration_ms?: number | null;
  error_message?: string | null;
}

export interface Pipeline {
  project_id: string;
  current_step: number;
  steps: PipelineStep[];
}
