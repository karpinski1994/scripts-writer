import json
import logging
import re

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import HookAgentInput, HookAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert copywriter specializing in attention-grabbing hooks for video and marketing content. "
    "The DRAFT/CONTENT is your PRIMARY source of truth — it contains the actual message and content the user wants to convey. "
    "All other data (ICP, topic, format, goal) is auxiliary context to shape HOW hooks are crafted, not WHAT they're about. "
    "Generate multiple hook options in JSON format. "
    "Output ONLY valid JSON: hooks[hook_type, text, reasoning], confidence (0.0-1.0). "
    "Vary the hook types (question, shock, story, statistic, etc.). Hooks must resonate with the draft's core message."
)


class HookAgent(BaseAgent[HookAgentInput, HookAgentOutput]):
    @property
    def name(self) -> str:
        return "HookAgent"

    @property
    def step_type(self) -> str:
        return StepType.hook.value

    def build_prompt(self, input_data: HookAgentInput) -> str:
        icp = input_data.icp
        parts = []
        if input_data.draft:
            parts.append(
                "=== PRIMARY SOURCE (Draft/Content) — This is your most important reference. "
                "Base hooks on THIS content above all else. ===\n"
                f"{input_data.draft}"
            )
        parts.extend(
            [
                f"Topic: {input_data.topic}",
                f"Target Format: {input_data.target_format}",
                f"ICP Summary (auxiliary — shapes HOW to hook, not WHAT about):\n{icp.model_dump_json(indent=2)}",
            ]
        )
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.piragi_context:
            parts.append(f"Relevant reference material:\n{input_data.piragi_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=HookAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> HookAgentOutput:
        logger.info(f"[HOOK-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[HOOK-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)

        if not raw or not raw.strip():
            logger.error("[HOOK-AGENT] LLM returned empty response")
            raise ValueError("LLM returned empty response")
        raw = raw.strip()
        logger.debug(f"[HOOK-AGENT] Raw LLM response length: {len(raw)}")
        logger.debug(f"[HOOK-AGENT] Raw response preview: {raw[:200]}...")

        # Strip markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            data = json.loads(raw)
            logger.debug("[HOOK-AGENT] Parsed JSON successfully")
        except json.JSONDecodeError:
            logger.warning("[HOOK-AGENT] Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                logger.error(f"[HOOK-AGENT] Failed to extract valid JSON: {raw[:100]}...")
                raise ValueError(f"LLM response is not valid JSON: {raw[:100]}...")
        if not raw.startswith("{") and not raw.startswith("["):
            logger.error(f"[HOOK-AGENT] LLM response is not JSON: {raw[:100]}...")
            raise ValueError(f"LLM response is not JSON: {raw[:100]}...")
        # Add default confidence if missing
        if "confidence" not in data:
            data["confidence"] = 0.8

        hook_count = len(data.get("hooks", []))
        logger.info(f"[HOOK-AGENT] LLM call completed, generated {hook_count} hooks")
        return HookAgentOutput.model_validate(data)
