from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", priority: int = 3):
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
        model = model or self._model_name
        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
        )
        response = await self._client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text or ""

    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]:
        model = model or self._model_name
        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            candidate_count=1,
        )
        response = await self._client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
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
