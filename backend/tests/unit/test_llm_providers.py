from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from openai import AuthenticationError, RateLimitError

from app.config import AppSettings
from app.llm.base import LLMProvider
from app.llm.cache import LLMCache
from app.llm.errors import AllProvidersFailedError
from app.llm.provider_factory import ProviderFactory


class MockLLMProvider(LLMProvider):
    def __init__(
        self,
        name: str,
        response: str | None = "mock response",
        should_fail: bool = False,
        fail_error: Exception | None = None,
        priority: int = 1,
    ):
        self._name = name
        self._response = response
        self._should_fail = should_fail
        self._fail_error = fail_error
        self._priority = priority

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return "mock-model"

    @property
    def priority(self) -> int:
        return self._priority

    async def generate(self, prompt: str, system_prompt: str = "", model: str | None = None) -> str:
        if self._should_fail:
            if self._fail_error:
                raise self._fail_error
            raise RuntimeError(f"{self._name} failed")
        return self._response or ""

    async def stream(self, prompt: str, system_prompt: str = "", model: str | None = None) -> AsyncIterator[str]:
        if self._should_fail:
            raise RuntimeError(f"{self._name} failed")
        yield self._response or ""

    async def health_check(self) -> bool:
        return not self._should_fail


@pytest.mark.asyncio
async def test_successful_generation():
    provider = MockLLMProvider(name="mock", response="hello world")
    result = await provider.generate("test prompt")
    assert result == "hello world"


@pytest.mark.asyncio
async def test_rate_limit_error():
    provider = MockLLMProvider(
        name="mock",
        should_fail=True,
        fail_error=RateLimitError(message="rate limited", response=AsyncMock(), body=AsyncMock()),
    )
    with pytest.raises(RateLimitError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_failover_from_one_provider_to_next():
    factory = ProviderFactory.__new__(ProviderFactory)
    factory._settings = AppSettings()
    factory._providers = [
        MockLLMProvider(name="failing", should_fail=True, priority=1),
        MockLLMProvider(name="working", response="success from backup", priority=2),
    ]
    result = await factory.execute_with_failover("test prompt")
    assert result == "success from backup"


@pytest.mark.asyncio
async def test_all_providers_fail():
    factory = ProviderFactory.__new__(ProviderFactory)
    factory._settings = AppSettings()
    factory._providers = [
        MockLLMProvider(name="p1", should_fail=True, priority=1),
        MockLLMProvider(name="p2", should_fail=True, priority=2),
    ]
    with pytest.raises(AllProvidersFailedError) as exc_info:
        await factory.execute_with_failover("test prompt")
    assert "p1" in exc_info.value.errors
    assert "p2" in exc_info.value.errors


@pytest.mark.asyncio
async def test_auth_error_skips_provider():
    factory = ProviderFactory.__new__(ProviderFactory)
    factory._settings = AppSettings()
    factory._providers = [
        MockLLMProvider(
            name="bad-auth",
            should_fail=True,
            fail_error=AuthenticationError(message="bad key", response=AsyncMock(), body=AsyncMock()),
            priority=1,
        ),
        MockLLMProvider(name="working", response="success", priority=2),
    ]
    result = await factory.execute_with_failover("test prompt")
    assert result == "success"


@pytest.mark.asyncio
async def test_no_providers_configured():
    factory = ProviderFactory.__new__(ProviderFactory)
    factory._settings = AppSettings()
    factory._providers = []
    with pytest.raises(AllProvidersFailedError):
        await factory.execute_with_failover("test prompt")


@pytest.mark.asyncio
async def test_cache_hit_with_factory():
    cache = LLMCache(max_size=10, ttl_seconds=3600)
    await cache.set("test prompt", "system", "mock-model", "cached response")
    result = await cache.get("test prompt", "system", "mock-model")
    assert result == "cached response"


@pytest.mark.asyncio
async def test_cache_miss_with_factory():
    cache = LLMCache()
    result = await cache.get("nonexistent", "", "model")
    assert result is None
