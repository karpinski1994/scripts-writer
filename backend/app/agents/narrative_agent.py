import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import NarrativeAgentInput, NarrativeAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert storytelling consultant specializing in narrative structures for video and marketing content. "
    "Given an ICP, a selected hook, topic, and format, generate narrative pattern options that will carry the "
    "audience from the hook through to the conclusion. Each pattern should outline the key beats and flow. "
    "Consider the ICP's values, objections, and desired outcomes when structuring the narrative."
)


class NarrativeAgent(BaseAgent[NarrativeAgentInput, NarrativeAgentOutput]):
    @property
    def name(self) -> str:
        return "NarrativeAgent"

    @property
    def step_type(self) -> str:
        return StepType.narrative.value

    def build_prompt(self, input_data: NarrativeAgentInput) -> str:
        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=NarrativeAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> NarrativeAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return NarrativeAgentOutput.model_validate(data)
