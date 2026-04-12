import asyncio
from collections.abc import AsyncIterator

import ollama

from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2", priority: int = 4):
        self._base_url = base_url
        self._model = model
        self._priority = priority
        self._client = ollama.AsyncClient(host=base_url)

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def priority(self) -> int:
        return self._priority

    async def generate(self, prompt: str, system_prompt: str = "", model: str | None = None) -> str:
        response = await self._client.chat(
            model=model or self._model,
            messages=self._build_messages(prompt, system_prompt),
        )
        return response.message.content or ""

    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]:
        stream = await self._client.chat(
            model=model or self._model,
            messages=self._build_messages(prompt, system_prompt),
            stream=True,
        )
        async for chunk in stream:
            if chunk.message and chunk.message.content:
                yield chunk.message.content

    async def health_check(self) -> bool:
        try:
            await asyncio.wait_for(self.generate("hi"), timeout=10)
            return True
        except Exception:
            return False

    @staticmethod
    def _build_messages(prompt: str, system_prompt: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages
