from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TargetFormat(StrEnum):
    Short_Video = "Short-form Video"
    Long_Video = "Long-form Video"
    VSL = "VSL"
    Blog_Post = "Blog Post"
    LinkedIn_Post = "LinkedIn Post"
    Facebook_Post = "Facebook Post"

    @classmethod
    def from_label(cls, label: str) -> "TargetFormat":
        for f in cls:
            if f.value == label:
                return f
        return cls.VSL


class ContentGoal(StrEnum):
    Sell = "Sell"
    Educate = "Educate"
    Entertain = "Entertain"
    Build_Authority = "Build Authority"


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SubjectUpdateRequest(BaseModel):
    topic: str = Field(default="", max_length=500)
    target_format: str
    content_goal: str | None = None
    raw_notes: str = Field(default="", max_length=10000)


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    topic: str | None = Field(default=None, min_length=1, max_length=200)
    target_format: TargetFormat | None = None
    content_goal: ContentGoal | None = None
    cta_purpose: str | None = Field(default=None, max_length=100)
    raw_notes: str | None = Field(default=None, min_length=1, max_length=10000)


class BranchRequest(BaseModel):
    branch_from_step: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=100)


class ProjectResponse(BaseModel):
    id: str
    name: str
    topic: str | None
    target_format: str | None
    content_goal: str | None
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectSummaryResponse(BaseModel):
    id: str
    name: str
    target_format: str | None
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    id: str
    name: str
    topic: str | None
    target_format: str | None
    content_goal: str | None
    raw_notes: str | None
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
