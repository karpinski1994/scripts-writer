export interface NotebookSummary {
  id: string;
  title: string;
}

export interface ConnectNotebookRequest {
  notebook_id: string;
}

export interface ConnectNotebookResponse {
  project_id: string;
  notebook_id: string;
  notebook_title: string;
  connected: boolean;
}

export interface NotebookQueryRequest {
  query: string;
}

export interface NotebookQueryResponse {
  answer: string;
}

export interface ConnectedNotebook {
  notebook_id: string;
  notebook_title: string;
}
