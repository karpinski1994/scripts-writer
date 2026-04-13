import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import WriterAgentInput, WriterAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert scriptwriter for video and marketing content. "
    "Given an ICP, selected hook, narrative pattern, retention techniques, and CTA, "
    "write a complete script that weaves all these elements together into a compelling piece. "
    "The script should feel natural and persuasive, not formulaic. "
    "Adapt the tone and language style to the ICP profile. "
    "Include the raw notes as source material to incorporate key details."
)


class WriterAgent(BaseAgent[WriterAgentInput, WriterAgentOutput]):
    @property
    def name(self) -> str:
        return "WriterAgent"

    @property
    def step_type(self) -> str:
        return StepType.writer.value

    def build_prompt(self, input_data: WriterAgentInput) -> str:
        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
            f"Selected Retention Technique:\n{input_data.selected_retention.model_dump_json(indent=2)}",
            f"Selected CTA:\n{input_data.selected_cta.model_dump_json(indent=2)}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.raw_notes:
            parts.append(f"Raw Notes:\n{input_data.raw_notes}")
        if input_data.piragi_context:
            parts.append(f"Relevant reference material:\n{input_data.piragi_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=WriterAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> WriterAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return WriterAgentOutput.model_validate(data)
