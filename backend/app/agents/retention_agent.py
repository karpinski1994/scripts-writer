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
        if input_data.piragi_context:
            parts.append(f"Relevant reference material:\n{input_data.piragi_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=RetentionAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> RetentionAgentOutput:
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from LLM, text response - attempting to parse as text")
            techniques = self._parse_text_response(raw)
            if techniques:
                data = {"techniques": techniques, "confidence": 0.7}
            else:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    raw = raw[start:end]
                    data = json.loads(raw)
                else:
                    data = {"techniques": [], "confidence": 0.5}
        try:
            return RetentionAgentOutput.model_validate(data)
        except Exception:
            techniques = self._parse_text_response(raw) if isinstance(raw, str) else []
            if techniques:
                return RetentionAgentOutput(techniques=techniques, confidence=0.7)
            return RetentionAgentOutput(techniques=[], confidence=0.5)

    def _parse_text_response(self, text: str) -> list[dict]:
        techniques = []
        lines = text.split("\n")
        current_section = ""
        skip_section = False

        cta_keywords = [
            "call to action",
            "cta",
            "schedule",
            "consultation",
            "book your",
            "risk-free",
            "guarantee",
            "follow-up",
            "reward",
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue
            line_lower = line.lower()

            if any(kw in line_lower for kw in cta_keywords) and any(
                kw in line_lower for kw in ["action", "schedule", "book", "risk", "consultation"]
            ):
                continue

            if "**" in line and "(" in line and line.strip().startswith("**"):
                current_section = line
                continue

            if line.startswith(("1.", "2.", "3.", "1 ", "2 ", "3 ")) or line.startswith("-"):
                item = line.lstrip("123.- ").strip()
                if item and "**" in item:
                    parts = item.split(":", 1)
                    if len(parts) >= 2:
                        name = parts[0].replace("**", "").strip()
                        desc = parts[1].strip()[:200]
                        techniques.append(
                            {"technique_name": name, "description": desc, "placement_hint": current_section}
                        )

        return techniques
