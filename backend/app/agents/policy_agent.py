import json
import logging

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.analysis import PolicyAgentInput, PolicyAgentOutput

logger = logging.getLogger(__name__)

PLATFORM_PROMPTS = {
    "YouTube": "YouTube policies including community guidelines, advertiser-friendly content, "
    "misinformation policies, and disclosure requirements for sponsored content.",
    "Facebook": "Facebook policies including community standards, advertising policies, "
    "and content restrictions for branded content.",
    "LinkedIn": "LinkedIn policies including professional community policies, advertising "
    "guidelines, and content standards for professional audiences.",
    "VSL": "General video sales letter policies including FTC guidelines for claims, "
    "testimonials, and earnings disclosures.",
    "Tutorial": "Tutorial content policies including proper attribution, "
    "accuracy requirements, and platform-specific guidelines.",
    "Blog": "Blog content policies including SEO guidelines, FTC disclosure requirements, "
    "and content attribution standards.",
}

SYSTEM_PROMPT = (
    "You are a platform policy expert reviewing video and marketing scripts. "
    "Check the script for compliance with platform-specific policies and guidelines. "
    "Identify potential violations including: prohibited claims, missing disclosures, "
    "restricted content categories, and policy-triggering language. "
    "For each issue, provide the specific policy concern and a suggestion to comply. "
    "Return findings as a JSON array with type, severity (low/medium/high/critical), "
    "text describing the issue, suggestion for compliance, and confidence (0-1)."
)


class PolicyAgent(BaseAgent[PolicyAgentInput, PolicyAgentOutput]):
    @property
    def name(self) -> str:
        return "PolicyAgent"

    @property
    def step_type(self) -> str:
        return StepType.policy.value

    def build_prompt(self, input_data: PolicyAgentInput) -> str:
        platform_guidance = PLATFORM_PROMPTS.get(
            input_data.target_format, "General content policies and FTC guidelines."
        )
        parts = [
            f"Script Content:\n{input_data.script_content}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
            f"Platform Policy Focus: {platform_guidance}",
        ]
        return "\n\n".join(parts)

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> PolicyAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        data = json.loads(raw)
        return PolicyAgentOutput.model_validate(data)
