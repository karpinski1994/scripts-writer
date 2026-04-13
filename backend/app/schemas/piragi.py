from pydantic import BaseModel


class DocumentSummary(BaseModel):
    category: str
    file_count: int
    path: str


class ConnectDocumentsRequest(BaseModel):
    document_paths: str


class ConnectDocumentsResponse(BaseModel):
    project_id: str
    document_paths: str
    connected: bool


class ChunkResult(BaseModel):
    chunk: str
    source: str
    relevance: float


class PiragiQueryRequest(BaseModel):
    query: str
    step_type: str


class PiragiQueryResponse(BaseModel):
    query: str
    results: list[ChunkResult]


class PiragiDocumentsResponse(BaseModel):
    categories: list[DocumentSummary]


class UploadDocumentResponse(BaseModel):
    filename: str
    category: str
    path: str
    size: int
