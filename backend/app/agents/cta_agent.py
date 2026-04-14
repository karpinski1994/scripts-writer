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
        if input_data.cta_purpose:
            parts.append(f"CTA Purpose: {input_data.cta_purpose}")
        else:
            parts.append("CTA Purpose: [Not specified - ask user to define their call-to-action goal]")
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.piragi_context:
            parts.append(f"Relevant reference material:\n{input_data.piragi_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=CTAAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> CTAAgentOutput:
        logger.info(f"[CTA-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[CTA-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        raw = raw.strip()
        logger.debug(f"[CTA-AGENT] Raw LLM response length: {len(raw)}")
        logger.debug(f"[CTA-AGENT] Raw response preview: {raw[:200]}...")

        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        try:
            data = json.loads(raw)
            logger.debug(f"[CTA-AGENT] Parsed JSON successfully")
        except json.JSONDecodeError:
            logger.warning("[CTA-AGENT] Invalid JSON from LLM, text response - attempting to parse as text")
            ctas = self._parse_text_response(raw)
            if ctas:
                data = {"ctas": ctas, "confidence": 0.7}
            else:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    raw = raw[start:end]
                    data = json.loads(raw)
                else:
                    data = {"ctas": [], "confidence": 0.5}
        try:
            logger.info(f"[CTA-AGENT] LLM call completed, generated {len(data.get('ctas', []))} CTAs")
            return CTAAgentOutput.model_validate(data)
        except Exception:
            ctas = self._parse_text_response(raw)
            if ctas:
                return CTAAgentOutput(ctas=ctas, confidence=0.7)
            return CTAAgentOutput(ctas=[], confidence=0.5)

    def _parse_text_response(self, text: str) -> list[dict]:
        ctas = []
        lines = text.split("\n")
        current_type = "direct"

        type_keywords = {
            "direct ctas": "direct",
            "soft ctas": "soft",
            "urgency ctas": "urgency",
            "value-driven ctas": "value-driven",
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()
            for kw, ctype in type_keywords.items():
                if kw in line_lower:
                    current_type = ctype
                    continue

            if line.startswith(("1.", "2.", "3.", "1 ", "2 ", "3 ")) or line.startswith("-"):
                item = line.lstrip("123.- ").strip()
                if item and "**" in item:
                    parts = item.split(":", 1)
                    if len(parts) >= 2:
                        name = parts[0].replace("**", "").strip()
                        desc = parts[1].strip()
                        ctas.append(
                            {
                                "cta_type": current_type,
                                "text": f"{name}: {desc}",
                                "reasoning": "Extracted from text response",
                            }
                        )

        return ctas
