import json
import logging
import re

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.analysis import CopyrightAgentInput, CopyrightAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a copyright and trademark expert reviewing video and marketing scripts. "
    "Identify potential copyright issues including: trademarked names used without "
    "disclaimer, copyrighted phrases or slogans, brand names that require attribution, "
    "and content that may infringe on intellectual property. "
    "For each issue, provide an advisory warning and suggestion. "
    "Return findings as a JSON array with type, severity (low/medium/high/critical), "
    "text describing the issue, suggestion for resolution, and confidence (0-1)."
)


class CopyrightAgent(BaseAgent[CopyrightAgentInput, CopyrightAgentOutput]):
    @property
    def name(self) -> str:
        return "CopyrightAgent"

    @property
    def step_type(self) -> str:
        return StepType.copyright.value

    def build_prompt(self, input_data: CopyrightAgentInput) -> str:
        parts = [
            f"Script Content:\n{input_data.script_content}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        return "\n\n".join(parts)

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> CopyrightAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("CopyrightAgent: Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise
        if isinstance(data, list):
            data = {"findings": data, "confidence": 0.7}
        return CopyrightAgentOutput.model_validate(data)
