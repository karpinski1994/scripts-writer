from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TargetFormat(StrEnum):
    VSL = "VSL"
    YouTube = "YouTube"
    Tutorial = "Tutorial"
    Facebook = "Facebook"
    LinkedIn = "LinkedIn"
    Blog = "Blog"


class ContentGoal(StrEnum):
    Sell = "Sell"
    Educate = "Educate"
    Entertain = "Entertain"
    Build_Authority = "Build Authority"


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=1, max_length=200)
    target_format: TargetFormat
    content_goal: ContentGoal | None = None
    raw_notes: str = Field(min_length=1, max_length=10000)


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    topic: str | None = Field(default=None, min_length=1, max_length=200)
    target_format: TargetFormat | None = None
    content_goal: ContentGoal | None = None
    raw_notes: str | None = Field(default=None, min_length=1, max_length=10000)


class ProjectResponse(BaseModel):
    id: str
    name: str
    topic: str
    target_format: str
    content_goal: str | None
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectSummaryResponse(BaseModel):
    id: str
    name: str
    target_format: str
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    id: str
    name: str
    topic: str
    target_format: str
    content_goal: str | None
    raw_notes: str
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
