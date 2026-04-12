import hashlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.llm.cache import LLMCache
from app.llm.provider_factory import ProviderFactory

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def step_type(self) -> str: ...

    @abstractmethod
    def build_prompt(self, input_data: InputT) -> str: ...

    @abstractmethod
    async def _call_llm(self, prompt: str, factory: ProviderFactory) -> OutputT: ...

    async def execute(self, input_data: InputT, cache: LLMCache, factory: ProviderFactory) -> OutputT:
        prompt = self.build_prompt(input_data)
        cache_key = self._compute_cache_key(input_data)
        cached = await cache.get(prompt, self.step_type, cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        result = await self._call_llm(prompt, factory)
        await cache.set(prompt, self.step_type, cache_key, result)  # type: ignore[arg-type]
        return result

    def _compute_cache_key(self, input_data: InputT) -> str:
        raw = f"{self.step_type}:{input_data}"
        return hashlib.sha256(raw.encode()).hexdigest()
