import json
import logging

from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.icp import ICPAgentInput, ICPAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert marketing analyst specializing in ICP generation. "
    "Given raw notes about a product/service, and clients generate ICP in JSON format. "
    "Output ONLY valid JSON with exact fields: icp.demographics(age_range,gender,income_level,"
    "education,location,occupation), icp.psychographics(values:list[str],interests:list[str],"
    "lifestyle:str,media_consumption:list[str],personality_traits:list[str]), "
    "icp.pain_points:list[str], icp.desires:list[str], icp.objections:list[str], "
    "icp.language_style:str, confidence:float(0.0-1.0). Be specific and actionable."
)


class ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput]):
    @property
    def name(self) -> str:
        return "ICPAgent"

    @property
    def step_type(self) -> str:
        return StepType.icp.value

    def build_prompt(self, input_data: ICPAgentInput) -> str:
        parts = [
            f"Raw Notes:\n{input_data.raw_notes}",
            f"Topic: {input_data.topic}",
            f"Target Format: {input_data.target_format}",
        ]
        if input_data.content_goal:
            parts.append(f"Content Goal: {input_data.content_goal}")
        if input_data.faiss_context:
            parts.append(f"Relevant reference material from FAISS:\n{input_data.faiss_context}")
        return "\n\n".join(parts)

    def _build_agent(self) -> Agent:
        return Agent(
            model="test",
            result_type=ICPAgentOutput,
            system_prompt=SYSTEM_PROMPT,
        )

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> ICPAgentOutput:
        logger.info(f"[ICP-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[ICP-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)

        if not raw or not raw.strip():
            logger.error("[ICP-AGENT] LLM returned empty response")
            raise ValueError("LLM returned empty response")

        raw = raw.strip()
        logger.debug(f"[ICP-AGENT] Raw LLM response length: {len(raw)}")
        logger.debug(f"[ICP-AGENT] Raw response preview: {raw[:200]}...")
        # Strip markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        if not raw.startswith("{") and not raw.startswith("["):
            logger.error(f"[ICP-AGENT] LLM response is not JSON: {raw[:100]}...")
            raise ValueError(f"LLM response is not JSON: {raw[:100]}...")
        try:
            data = json.loads(raw)
            logger.debug(f"[ICP-AGENT] Parsed JSON successfully")
        except json.JSONError as e:
            logger.error(f"[ICP-AGENT] LLM response is not valid JSON: {e}")
            raise ValueError(f"LLM response is not valid JSON: {e}")
        # Normalize: convert strings to arrays where needed
        icp = data.get("icp", {})
        psychographics = icp.get("psychographics", {})
        for field in ["values", "interests", "media_consumption", "personality_traits"]:
            val = psychographics.get(field)
            if isinstance(val, str):
                psychographics[field] = [x.strip() for x in val.split(",") if x.strip()]
        for field in ["pain_points", "desires", "objections"]:
            val = icp.get(field)
            if isinstance(val, str):
                icp[field] = [x.strip() for x in val.split(",") if x.strip()]
        data["icp"] = icp

        logger.info(f"[ICP-AGENT] LLM call completed, ICP profile: {icp.get('demographics', {})}")
        return ICPAgentOutput.model_validate(data)
