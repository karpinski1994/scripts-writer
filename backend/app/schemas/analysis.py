from datetime import datetime

from pydantic import BaseModel, Field


class Finding(BaseModel):
    type: str
    severity: str
    text: str
    suggestion: str = ""
    confidence: float = Field(ge=0, le=1)


class FactCheckAgentInput(BaseModel):
    script_content: str
    topic: str
    target_format: str


class FactCheckAgentOutput(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ReadabilityAgentInput(BaseModel):
    script_content: str
    target_format: str


class ReadabilityAgentOutput(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    flesch_kincaid_score: float
    gunning_fog_score: float
    confidence: float = Field(ge=0, le=1)


class CopyrightAgentInput(BaseModel):
    script_content: str
    topic: str
    target_format: str


class CopyrightAgentOutput(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class PolicyAgentInput(BaseModel):
    script_content: str
    topic: str
    target_format: str


class PolicyAgentOutput(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class AnalysisOutput(BaseModel):
    factcheck: dict = Field(default_factory=dict)
    readability: dict = Field(default_factory=dict)
    copyright: dict = Field(default_factory=dict)
    policy: dict = Field(default_factory=dict)


class AnalysisResultResponse(BaseModel):
    id: str
    project_id: str
    script_version_id: str
    agent_type: str
    findings: list[Finding] = Field(default_factory=list)
    overall_score: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
