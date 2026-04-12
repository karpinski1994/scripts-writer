from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", priority: int = 3):
        self._api_key = api_key
        self._model_name = model
        self._priority = priority
        self._client = genai.Client(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def priority(self) -> int:
        return self._priority

    async def generate(self, prompt: str, system_prompt: str = "", model: str | None = None) -> str:
        contents = self._build_contents(prompt, system_prompt)
        response = await self._client.aio.models.generate_content(
            model=model or self._model_name,
            contents=contents,
        )
        return response.text or ""

    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]:
        contents = self._build_contents(prompt, system_prompt)
        response = await self._client.aio.models.generate_content(
            model=model or self._model_name,
            contents=contents,
            config=types.GenerateContentConfig(candidate_count=1),
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def health_check(self) -> bool:
        try:
            await self.generate("hi")
            return True
        except Exception:
            return False

    @staticmethod
    def _build_contents(prompt: str, system_prompt: str) -> list[str]:
        parts: list[str] = []
        if system_prompt:
            parts.append(system_prompt)
        parts.append(prompt)
        return parts
