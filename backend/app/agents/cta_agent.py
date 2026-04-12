import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import CTAAgentInput, CTAAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert in calls-to-action (CTAs) for video and marketing content. "
    "Given an ICP, a selected hook, a selected narrative pattern, and an optional content goal, "
    "generate CTA options that will drive the desired action from the audience. "
    "Consider the ICP's objections and motivations. Vary CTA types (direct, soft, urgency, value-driven)."
)


class CTAAgent(BaseAgent[CTAAgentInput, CTAAgentOutput]):
    @property
    def name(self) -> str:
        return "CTAAgent"

    @property
    def step_type(self) -> str:
        return StepType.cta.value

    def build_prompt(self, input_data: CTAAgentInput) -> str:
        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
        ]
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.notebooklm_context:
            parts.append(f"Additional research context from NotebookLM:\n{input_data.notebooklm_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=CTAAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> CTAAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return CTAAgentOutput.model_validate(data)
