import logging
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class ModalProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.us-west-2.modal.direct/v1",
        model: str = "zai-org/GLM-5.1-FP8",
        priority: int = 3,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._priority = priority
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    @property
    def provider_name(self) -> str:
        return "modal"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def priority(self) -> int:
        return self._priority

    async def generate(self, prompt: str, system_prompt: str = "", model: str | None = None) -> str:
        model = model or self._model
        messages = self._build_messages(prompt, system_prompt)
        logger.info(f"HTTP Request: POST {self._base_url}/chat/completions")
        logger.debug(f"Request body: model={model}, messages={messages}")
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=model or self._model,
            messages=self._build_messages(prompt, system_prompt),
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def health_check(self) -> bool:
        try:
            await self.generate("hi", model=self._model)
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
