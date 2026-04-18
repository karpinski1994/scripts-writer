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
    "Consider the ICP's objections and motivations. "
    "Generate at least 5 varied CTA options (e.g., direct, soft, urgency, value-driven). "
    "Output ONLY valid JSON format with this exact structure: "
    '{"ctas": [{"cta_type": "string", "text": "string", "reasoning": "string"}], "confidence": 0.0-1.0}'
)


class CTAAgent(BaseAgent[CTAAgentInput, CTAAgentOutput]):
    @property
    def name(self) -> str:
        return "CTAAgent"

    @property
    def step_type(self) -> str:
        return StepType.cta.value

    def build_prompt(self, input_data: CTAAgentInput) -> str:
        logger.info(f"[CTA-AGENT] build_prompt called, cta_purpose: {input_data.cta_purpose}")
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
        logger.debug(f"[CTA-AGENT] Raw response preview: {raw[:500]}...")

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
            logger.info(f"[CTA-AGENT] Full raw response for parsing:\n{raw[:1500]}")
            ctas = self._parse_text_response(raw)
            logger.info(f"[CTA-AGENT] Parsed CTAs from text: {len(ctas)}, results: {ctas}")
            if ctas:
                data = {"ctas": ctas, "confidence": 0.7}
            else:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    raw = raw[start:end]
                    logger.info(f"[CTA-AGENT] Trying fallback JSON parse from positions {start}:{end}")
                    data = json.loads(raw)
                else:
                    logger.warning("[CTA-AGENT] No JSON found, returning empty CTAs")
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
        pending_cta_type = None
        pending_text = []

        type_keywords = {
            "direct cta": "direct",
            "direct ctas": "direct",
            "soft cta": "soft",
            "soft ctas": "soft",
            "urgency cta": "urgency",
            "urgency ctas": "urgency",
            "value-driven cta": "value-driven",
            "value-driven ctas": "value-driven",
            "value driven": "value-driven",
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()
            for kw, ctype in type_keywords.items():
                if kw in line_lower:
                    current_type = ctype
                    break
            else:
                if "**" in line:
                    if line.startswith("**") and not line.startswith("** "):
                        continue
                    if (
                        '"' in line
                        or line.startswith("Direct")
                        or line.startswith("Soft")
                        or line.startswith("Urgency")
                        or line.startswith("Value")
                    ):
                        if line.startswith("**"):
                            line = line.replace("**", "").strip()
                        if line.endswith("**"):
                            line = line[:-2].strip()
                        if len(line) > 10:
                            ctas.append(
                                {
                                    "cta_type": current_type,
                                    "text": line.strip(),
                                    "reasoning": "Extracted from bold CTA section",
                                }
                            )
                    elif (
                        line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("-")
                    ):
                        item = line.lstrip("123.- ").strip()
                        if item and len(item) > 5:
                            ctas.append(
                                {
                                    "cta_type": current_type,
                                    "text": item.strip(),
                                    "reasoning": "Extracted from numbered line",
                                }
                            )
                continue

        return ctas[:4]
