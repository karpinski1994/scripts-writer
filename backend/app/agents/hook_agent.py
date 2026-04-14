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
    "Given an Ideal Customer Profile (ICP), topic, format, and goal, generate multiple hook options in JSON format. "
    "Output ONLY valid JSON with these exact fields: hooks[hook_type, text, reasoning], confidence (0.0-1.0). "
    "Vary the hook types (question, shock, story, statistic, etc.)."
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
        parts = [
            f"ICP Summary:\n{icp.model_dump_json(indent=2)}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
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
        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        if not raw or not raw.strip():
            raise ValueError("LLM returned empty response")
        raw = raw.strip()
        # Strip markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("HookAgent: Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise ValueError(f"LLM response is not valid JSON: {raw[:100]}...")
        if not raw.startswith("{") and not raw.startswith("["):
            raise ValueError(f"LLM response is not JSON: {raw[:100]}...")
        # Add default confidence if missing
        if "confidence" not in data:
            data["confidence"] = 0.8
        return HookAgentOutput.model_validate(data)
