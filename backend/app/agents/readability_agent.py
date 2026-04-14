import json
import logging
import re

from app.agents.base import BaseAgent
from app.llm.provider_factory import ProviderFactory
from app.pipeline.state import StepType
from app.schemas.analysis import ReadabilityAgentInput, ReadabilityAgentOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a readability expert for video and marketing scripts. "
    "Given a script and its readability scores, identify complex sentences and "
    "jargon that could be simplified for the target audience. "
    "For each issue, provide a specific simplification suggestion. "
    "Return findings as a JSON array with type, severity (low/medium/high/critical), "
    "text describing the issue, suggestion for simplification, and confidence (0-1)."
)


def _count_syllables(word: str) -> int:
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy":
        count += 1
    return max(count, 1)


def _is_complex_word(word: str) -> bool:
    if word[0].isupper():
        return False
    return _count_syllables(word) >= 3


def compute_readability_scores(text: str) -> tuple[float, float]:
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0, 0.0

    words = re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text)
    if not words:
        return 0.0, 0.0

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(_count_syllables(w) for w in words)
    complex_words = sum(1 for w in words if _is_complex_word(w))

    fk = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
    gf = 0.4 * ((total_words / total_sentences) + 100 * (complex_words / total_words))

    return round(fk, 2), round(gf, 2)


class ReadabilityAgent(BaseAgent[ReadabilityAgentInput, ReadabilityAgentOutput]):
    @property
    def name(self) -> str:
        return "ReadabilityAgent"

    @property
    def step_type(self) -> str:
        return StepType.readability.value

    def build_prompt(self, input_data: ReadabilityAgentInput) -> str:
        fk, gf = compute_readability_scores(input_data.script_content)
        parts = [
            f"Script Content:\n{input_data.script_content}",
            f"Target Format: {input_data.target_format}",
            f"Flesch-Kincaid Grade Level: {fk}",
            f"Gunning Fog Index: {gf}",
            "Identify complex sentences and jargon that could be simplified. "
            "Focus on sentences that contribute to high readability scores.",
        ]
        return "\n\n".join(parts)

    async def execute(self, input_data: ReadabilityAgentInput, cache, factory) -> ReadabilityAgentOutput:
        fk, gf = compute_readability_scores(input_data.script_content)
        prompt = self.build_prompt(input_data)
        cache_key = self._compute_cache_key(input_data)
        cached = await cache.get(prompt, self.step_type, cache_key)
        if cached is not None:
            cached.flesch_kincaid_score = fk
            cached.gunning_fog_score = gf
            return cached
        result = await self._call_llm(prompt, factory)
        result.flesch_kincaid_score = fk
        result.gunning_fog_score = gf
        await cache.set(prompt, self.step_type, cache_key, result)
        return result

    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> ReadabilityAgentOutput:
        logger.info(f"[READABILITY-AGENT] Calling LLM with prompt length: {len(prompt)}")
        logger.debug(f"[READABILITY-AGENT] Prompt preview: {prompt[:200]}...")

        raw = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        logger.debug(f"[READABILITY-AGENT] Raw LLM response length: {len(raw)}")

        try:
            data = json.loads(raw)
            logger.debug(f"[READABILITY-AGENT] Parsed JSON successfully")
        except json.JSONDecodeError:
            logger.warning("[READABILITY-AGENT] Invalid JSON response, attempting to extract JSON")
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                logger.error("[READABILITY-AGENT] Failed to extract JSON")
                raise
        if isinstance(data, list):
            data = {"findings": data, "confidence": 0.7}

        findings_count = len(data.get("findings", []))
        logger.info(f"[READABILITY-AGENT] LLM call completed, findings: {findings_count}")
        return ReadabilityAgentOutput(
            findings=data.get("findings", []),
            flesch_kincaid_score=0.0,
            gunning_fog_score=0.0,
            confidence=data.get("confidence", 0.5),
        )
