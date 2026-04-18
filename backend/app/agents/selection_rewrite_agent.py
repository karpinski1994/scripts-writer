import logging
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert editor. You will receive the FULL SCRIPT for context, but your ONLY job is to rewrite the EXACT SELECTED PORTION. "
    "Output ONLY the rewritten text. Ensure the tone matches the surrounding context unless instructed otherwise. "
    "Do NOT include markdown, JSON, or any conversational filler. Return only the raw rewritten text."
)


class SelectionRewriteInput(BaseModel):
    full_content: str
    selected_text: str
    instruction: str
    icp_summary: Optional[str] = None


@dataclass
class SelectionRewriteOutput:
    rewritten_text: str


async def rewrite_selection(
    factory,
    full_content: str,
    selected_text: str,
    instruction: str,
    icp_summary: Optional[str] = None,
) -> str:
    """Rewrite selected text using LLM with full script context."""

    prompt_parts = [
        "FULL SCRIPT (for context):",
        full_content,
        "",
        "SELECTED TEXT TO REWRITE:",
        selected_text,
        "",
        "INSTRUCTION:",
        instruction,
    ]

    if icp_summary:
        prompt_parts.extend(
            [
                "",
                "ICP PROFILE (for tone matching):",
                icp_summary,
            ]
        )

    prompt = "\n".join(prompt_parts)

    logger.info(f"[SELECTION-REWRITE] Rewriting selection, instruction: {instruction}")
    logger.debug(f"[SELECTION-REWRITE] Selected text preview: {selected_text[:100]}...")

    try:
        result = await factory.execute_with_failover(prompt, SYSTEM_PROMPT)
        rewritten = result.strip()

        logger.info(f"[SELECTION-REWRITE] Rewrite completed, result length: {len(rewritten)}")
        logger.debug(f"[SELECTION-REWRITE] Result preview: {rewritten[:100]}...")

        return rewritten
    except Exception as e:
        logger.error(f"[SELECTION-REWRITE] Failed: {e}")
        raise
