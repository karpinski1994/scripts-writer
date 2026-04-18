from datetime import datetime

from pydantic import BaseModel


class ScriptVersionResponse(BaseModel):
    id: str
    project_id: str
    version_number: int
    content: str
    format: str
    hook_text: str | None = None
    narrative_pattern: str | None = None
    cta_text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScriptUpdateRequest(BaseModel):
    content: str


class RewriteSelectionRequest(BaseModel):
    full_content: str
    selected_text: str
    instruction: str
