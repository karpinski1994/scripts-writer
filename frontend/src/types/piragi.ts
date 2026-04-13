export interface DocumentSummary {
  category: string;
  file_count: number;
  path: string;
}

export interface ConnectDocumentsRequest {
  document_paths: string;
}

export interface ConnectDocumentsResponse {
  project_id: string;
  document_paths: string;
  connected: boolean;
}

export interface ChunkResult {
  chunk: string;
  source: string;
  relevance: number;
}

export interface PiragiQueryRequest {
  query: string;
  step_type: string;
}

export interface PiragiQueryResponse {
  query: string;
  results: ChunkResult[];
}

export interface PiragiDocumentsResponse {
  categories: DocumentSummary[];
}

export interface ConnectedDocuments {
  document_paths: string;
}

export interface UploadDocumentResponse {
  filename: string;
  category: string;
  path: string;
  size: number;
}