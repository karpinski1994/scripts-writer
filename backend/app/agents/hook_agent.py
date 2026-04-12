import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import HookAgentInput, HookAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert copywriter specializing in attention-grabbing hooks for video and marketing content. "
    "Given an Ideal Customer Profile (ICP), topic, format, and goal, generate multiple hook options that "
    "would immediately capture the target audience's attention. Each hook should be tailored to the ICP's "
    "pain points, desires, and communication style. Vary the hook types (question, shock, story, statistic, etc.)."
)


class HookAgent(BaseAgent[HookAgentInput, HookAgentOutput]):
    @property
    def name(self) -> str:
        return "HookAgent"

    @property
    def step_type(self) -> str:
        return StepType.hook.value

    def build_prompt(self, input_data: HookAgentInput) -> str:
        icp = input_data.icp
        parts = [
            f"ICP Summary:\n{icp.model_dump_json(indent=2)}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=HookAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> HookAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return HookAgentOutput.model_validate(data)
