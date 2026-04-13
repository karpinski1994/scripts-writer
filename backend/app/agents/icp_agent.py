import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.icp import ICPAgentInput, ICPAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert marketing analyst specializing in Ideal Customer Profile (ICP) generation. "
    "Given raw notes about a product or service, generate a detailed ICP that includes demographics, "
    "psychographics, pain points, desires, objections, and recommended language style. "
    "Be specific and actionable. Base your analysis on the provided notes and context."
)


class ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput]):
    @property
    def name(self) -> str:
        return "ICPAgent"

    @property
    def step_type(self) -> str:
        return StepType.icp.value

    def build_prompt(self, input_data: ICPAgentInput) -> str:
        parts = [
            f"Raw Notes:\n{input_data.raw_notes}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.notebooklm_context:
            parts.append(f"Additional research context from NotebookLM:\n{input_data.notebooklm_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=ICPAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> ICPAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        if not raw or not raw.strip():
            raise ValueError("LLM returned empty response")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM response is not valid JSON: {e}")
        return ICPAgentOutput.model_validate(data)
