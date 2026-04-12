import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import RetentionAgentInput, RetentionAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert in audience retention techniques for video and marketing content. "
    "Given an ICP, a selected hook, a selected narrative pattern, and the content format, "
    "generate retention technique options that will keep the audience engaged throughout. "
    "Consider open loops, pattern interrupts, curiosity gaps, and other proven retention methods. "
    "Specify where each technique should be placed in the script."
)


class RetentionAgent(BaseAgent[RetentionAgentInput, RetentionAgentOutput]):
    @property
    def name(self) -> str:
        return "RetentionAgent"

    @property
    def step_type(self) -> str:
        return StepType.retention.value

    def build_prompt(self, input_data: RetentionAgentInput) -> str:
        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
            f"Target Format: {input_data.target_format}",
        ]
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=RetentionAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> RetentionAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return RetentionAgentOutput.model_validate(data)
