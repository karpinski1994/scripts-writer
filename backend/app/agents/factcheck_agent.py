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
        logger.info(f"[FACTCHECK-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[FACTCHECK-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        logger.debug(f"[FACTCHECK-AGENT] Raw LLM response length: {len(raw)}")

        try:
            data = json.loads(raw)
            logger.debug(f"[FACTCHECK-AGENT] Parsed JSON successfully")
        except json.JSONDecodeError:
            logger.warning("[FACTCHECK-AGENT] Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                logger.error("[FACTCHECK-AGENT] Failed to extract JSON")
                raise
        if isinstance(data, list):
            data = {"findings": data, "confidence": 0.7}
        elif isinstance(data, dict):
            if "findings" not in data:
                data = {"findings": data.get("issues", []) or [], "confidence": data.get("confidence", 0.7)}
            if "confidence" not in data:
                data["confidence"] = 0.7

        findings_count = len(data.get("findings", []))
        logger.info(f"[FACTCHECK-AGENT] LLM call completed, findings: {findings_count}")
        return FactCheckAgentOutput.model_validate(data)
