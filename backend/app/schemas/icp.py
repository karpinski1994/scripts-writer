from pydantic import BaseModel, Field


class ICPDemographics(BaseModel):
    age_range: str = Field(default="", description="Target age range")
    gender: str = Field(default="", description="Target gender")
    income_level: str = Field(default="", description="Target income level")
    education: str = Field(default="", description="Target education level")
    location: str = Field(default="", description="Target location")
    occupation: str = Field(default="", description="Target occupation")


class ICPPsychographics(BaseModel):
    values: list[str] = Field(default_factory=list, description="Core values")
    interests: list[str] = Field(default_factory=list, description="Key interests")
    lifestyle: str = Field(default="", description="Lifestyle description")
    media_consumption: list[str] = Field(default_factory=list, description="Media consumption habits")
    personality_traits: list[str] = Field(default_factory=list, description="Personality traits")


class ICPProfile(BaseModel):
    demographics: ICPDemographics = Field(default_factory=ICPDemographics)
    psychographics: ICPPsychographics = Field(default_factory=ICPPsychographics)
    pain_points: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    language_style: str = Field(default="professional")


class ICPAgentInput(BaseModel):
    raw_notes: str = ""
    topic: str | None = None
    target_format: str | None = None
    content_goal: str | None = None
    piragi_context: str | None = None


class ICPAgentOutput(BaseModel):
    icp: ICPProfile
    confidence: float = Field(ge=0, le=1)


class ICPProfileResponse(BaseModel):
    id: str
    project_id: str
    demographics: ICPDemographics
    psychographics: ICPPsychographics
    pain_points: list[str]
    desires: list[str]
    objections: list[str]
    language_style: str
    source: str
    approved: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ICPUpdateRequest(BaseModel):
    demographics: ICPDemographics | None = None
    psychographics: ICPPsychographics | None = None
    pain_points: list[str] | None = None
    desires: list[str] | None = None
    objections: list[str] | None = None
    language_style: str | None = None
    approved: bool | None = None
