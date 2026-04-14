import json
import logging
import re

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.analysis import FactCheckAgentInput, FactCheckAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a fact-checking expert for video and marketing scripts. "
    "Identify factual claims in the script content and evaluate their accuracy. "
    "For each claim, assess the confidence level and provide a suggestion if the claim "
    "may be inaccurate or misleading. Focus on verifiable statements like statistics, "
    "dates, scientific claims, and attributed quotes. "
    "Return findings as a JSON array with type, severity (low/medium/high/critical), "
    "text describing the claim, suggestion for correction, and confidence (0-1)."
)


class FactCheckAgent(BaseAgent[FactCheckAgentInput, FactCheckAgentOutput]):
    @property
    def name(self) -> str:
        return "FactCheckAgent"

    @property
    def step_type(self) -> str:
        return StepType.factcheck.value

    def build_prompt(self, input_data: FactCheckAgentInput) -> str:
        parts = [
            f"Script Content:\n{input_data.script_content}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        return "\n\n".join(parts)

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> FactCheckAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("FactCheckAgent: Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise
        return FactCheckAgentOutput.model_validate(data)
