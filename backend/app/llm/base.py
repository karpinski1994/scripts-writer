from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @property
    @abstractmethod
    def priority(self) -> int: ...

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", model: str | None = None) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    def get_identifier(self) -> str:
        return f"{self.provider_name}/{self.model_name}"
