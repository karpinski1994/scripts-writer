from pydantic import BaseModel


class PipelineStepResponse(BaseModel):
    id: str
    step_type: str
    step_order: int
    status: str
    output_data: str | None = None
    selected_option: str | None = None
    duration_ms: int | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class StepUpdateRequest(BaseModel):
    selected_option: dict | None = None


class PipelineResponse(BaseModel):
    project_id: str
    current_step: int
    steps: list[PipelineStepResponse]
