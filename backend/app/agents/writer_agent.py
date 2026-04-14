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
        retention_data = input_data.selected_retention
        if retention_data is None:
            retention_json = "N/A (not applicable for this format)"
        elif isinstance(retention_data, list):
            retention_json = json.dumps([r.model_dump() for r in retention_data], indent=2)
        else:
            retention_json = retention_data.model_dump_json(indent=2)

        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Selected Narrative:\n{input_data.selected_narrative.model_dump_json(indent=2)}",
            f"Selected Retention Technique(s):\n{retention_json}",
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
        logger.info(f"[WRITER-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[WRITER-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        raw = raw.strip()
        logger.debug(f"[WRITER-AGENT] Raw LLM response length: {len(raw)}")
        logger.debug(f"[WRITER-AGENT] Raw response preview: {raw[:200]}...")

        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        title = "VSL Script"
        content = raw
        word_count = len(raw.split())

        try:
            data = json.loads(raw)
            logger.debug(f"[WRITER-AGENT] Parsed JSON successfully")
            content = data.get("script", {}).get("content", raw) or raw
            word_count = data.get("script", {}).get("word_count", word_count) or word_count
        except json.JSONDecodeError:
            logger.warning("[WRITER-AGENT] Invalid JSON from LLM, using text response directly")

        try:
            logger.info(f"[WRITER-AGENT] LLM call completed, word_count: {word_count}")
            return WriterAgentOutput(
                script={"title": title, "content": content, "word_count": word_count, "notes": ""}, confidence=0.7
            )
        except Exception as e:
            logger.warning(f"[WRITER-AGENT] Validation failed: {e}")
            return WriterAgentOutput(
                script={"title": title, "content": content, "word_count": word_count, "notes": ""}, confidence=0.5
            )
