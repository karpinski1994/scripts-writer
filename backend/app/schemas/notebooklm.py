from pydantic import BaseModel


class NotebookSummary(BaseModel):
    id: str
    title: str


class ConnectNotebookRequest(BaseModel):
    notebook_id: str


class ConnectNotebookResponse(BaseModel):
    project_id: str
    notebook_id: str
    notebook_title: str
    connected: bool


class NotebookQueryRequest(BaseModel):
    query: str


class NotebookQueryResponse(BaseModel):
    answer: str
