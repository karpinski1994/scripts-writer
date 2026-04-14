import json
import logging
import re

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.agents import NarrativeAgentInput, NarrativeAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert storytelling consultant.
Given ICP, hook, topic, format, generate narrative patterns in JSON.
Output ONLY valid JSON: patterns[pattern_name, description, structure], confidence(0.0-1.0).
Each pattern outlines key beats and flow."""


class NarrativeAgent(BaseAgent[NarrativeAgentInput, NarrativeAgentOutput]):
    @property
    def name(self) -> str:
        return "NarrativeAgent"

    @property
    def step_type(self) -> str:
        return StepType.narrative.value

    def build_prompt(self, input_data: NarrativeAgentInput) -> str:
        parts = [
            f"ICP Summary:\n{input_data.icp.model_dump_json(indent=2)}",
            f"Selected Hook:\n{input_data.selected_hook.model_dump_json(indent=2)}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        if input_data.piragi_context:
            parts.append(f"Relevant reference material:\n{input_data.piragi_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=NarrativeAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> NarrativeAgentOutput:
        logger.info(f"[NARRATIVE-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[NARRATIVE-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)

        if not raw or not raw.strip():
            logger.error("[NARRATIVE-AGENT] LLM returned empty response")
            raise ValueError("LLM returned empty response")
        raw = raw.strip()
        logger.debug(f"[NARRATIVE-AGENT] Raw LLM response length: {len(raw)}")
        logger.debug(f"[NARRATIVE-AGENT] Raw response preview: {raw[:200]}...")

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            data = json.loads(raw)
            logger.debug(f"[NARRATIVE-AGENT] Parsed JSON successfully")
        except json.JSONDecodeError:
            logger.warning("[NARRATIVE-AGENT] Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                logger.error(f"[NARRATIVE-AGENT] Failed to extract valid JSON: {raw[:100]}...")
                raise ValueError(f"LLM response is not valid JSON: {raw[:100]}...")
        if not raw.startswith("{"):
            logger.error(f"[NARRATIVE-AGENT] LLM response is not JSON: {raw[:100]}...")
            raise ValueError(f"LLM response is not JSON: {raw[:100]}...")
        if "confidence" not in data:
            data["confidence"] = 0.8
        if "patterns" in data:
            for pattern in data["patterns"]:
                if "structure" in pattern and isinstance(pattern["structure"], list):
                    new_structure = []
                    for item in pattern["structure"]:
                        if isinstance(item, dict):
                            if "beat" in item and "description" in item:
                                new_structure.append(f"{item['beat']}: {item['description']}")
                            elif "beat" in item:
                                new_structure.append(item["beat"])
                            elif "description" in item:
                                new_structure.append(item["description"])
                            else:
                                new_structure.append(str(item))
                        elif isinstance(item, str):
                            new_structure.append(item)
                    pattern["structure"] = new_structure
        try:
            return NarrativeAgentOutput.model_validate(data)
        except Exception:
            return NarrativeAgentOutput(patterns=[], confidence=0.5)
