from pydantic import BaseModel, Field

from app.schemas.icp import ICPProfile


class HookSuggestion(BaseModel):
    hook_type: str = Field(description="Type of hook (e.g., question, shock, story)")
    text: str = Field(description="The hook text")
    reasoning: str = Field(default="", description="Why this hook works for the ICP")


class HookAgentInput(BaseModel):
    icp: ICPProfile
    topic: str
    target_format: str
    content_goal: str | None = None
    piragi_context: str | None = None


class HookAgentOutput(BaseModel):
    hooks: list[HookSuggestion] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class NarrativePattern(BaseModel):
    pattern_name: str = Field(description="Name of the narrative pattern")
    description: str = Field(description="Description of how the pattern works")
    structure: list[str] = Field(default_factory=list, description="Key beats of the narrative")


class NarrativeAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    topic: str
    target_format: str
    piragi_context: str | None = None


class NarrativeAgentOutput(BaseModel):
    patterns: list[NarrativePattern] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class RetentionTechnique(BaseModel):
    technique_name: str = Field(description="Name of the retention technique")
    description: str = Field(description="How to apply this technique")
    placement_hint: str = Field(default="", description="Where in the script to apply it")


class RetentionAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    target_format: str
    piragi_context: str | None = None


class RetentionAgentOutput(BaseModel):
    techniques: list[RetentionTechnique] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class CTASuggestion(BaseModel):
    cta_type: str = Field(description="Type of CTA (e.g., direct, soft, urgency)")
    text: str = Field(description="The CTA text")
    reasoning: str = Field(default="", description="Why this CTA fits the audience")


class CTAAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    content_goal: str | None = None
    piragi_context: str | None = None


class CTAAgentOutput(BaseModel):
    ctas: list[CTASuggestion] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ScriptDraft(BaseModel):
    title: str = Field(default="", description="Script title")
    content: str = Field(description="Full script content")
    word_count: int = Field(default=0, description="Approximate word count")
    notes: str = Field(default="", description="Notes on the generated script")


class WriterAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: HookSuggestion
    selected_narrative: NarrativePattern
    selected_retention: RetentionTechnique | list[RetentionTechnique]
    selected_cta: CTASuggestion
    topic: str
    target_format: str
    content_goal: str | None = None
    raw_notes: str = ""
    piragi_context: str | None = None


class WriterAgentOutput(BaseModel):
    script: ScriptDraft
    confidence: float = Field(ge=0, le=1)
