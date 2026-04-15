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
    "The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message the user wants to convey. "
    "All other data (ICP, hook, narrative, CTA purpose) is auxiliary context to shape the CTA. "
    "The CTA purpose is the highest-priority instruction and defines the exact action the audience should take. "
    "Every CTA must clearly drive that action and must not substitute a different conversion goal. "
    "The CTA should feel like a natural next step after the draft's content, not an interruption. "
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
        parts = []
        if input_data.cta_purpose:
            parts.append(
                "Primary CTA Goal (most important instruction):\n"
                f"- Exact audience action: {input_data.cta_purpose}\n"
                "- Every CTA must drive this exact action.\n"
                "- Do not replace it with a different or softer CTA goal."
            )
        else:
            parts.append(
                "Primary CTA Goal (most important instruction):\n"
                "[Not specified - ask user to define the exact action they want the audience to take]"
            )
        if input_data.draft:
            parts.append(
                "=== PRIMARY SOURCE (Draft/Content) — The CTA must feel like a natural next step from THIS content. ===\n"
                f"{input_data.draft}"
            )
        parts.extend(
            [
                f"ICP Summary (auxiliary):\n{input_data.icp.model_dump_json(indent=2)}",
                f"Selected Hook (auxiliary):\n{input_data.selected_hook.model_dump_json(indent=2)}",
                f"Selected Narrative (auxiliary):\n{input_data.selected_narrative.model_dump_json(indent=2)}",
            ]
        )
        if input_data.content_goal:
            parts.append(f"Content Goal (secondary context): {input_data.content_goal}")
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
