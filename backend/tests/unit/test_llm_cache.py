import asyncio

import pytest

from app.llm.cache import LLMCache


@pytest.mark.asyncio
async def test_cache_hit():
    cache = LLMCache(max_size=128, ttl_seconds=3600)
    await cache.set("hello", "system", "model-a", "response-1")
    result = await cache.get("hello", "system", "model-a")
    assert result == "response-1"


@pytest.mark.asyncio
async def test_cache_miss_different_prompt():
    cache = LLMCache()
    await cache.set("hello", "system", "model-a", "response-1")
    result = await cache.get("goodbye", "system", "model-a")
    assert result is None


@pytest.mark.asyncio
async def test_cache_miss_different_model():
    cache = LLMCache()
    await cache.set("hello", "system", "model-a", "response-1")
    result = await cache.get("hello", "system", "model-b")
    assert result is None


@pytest.mark.asyncio
async def test_cache_ttl_expiry():
    cache = LLMCache(max_size=128, ttl_seconds=0)
    await cache.set("hello", "system", "model-a", "response-1")
    await asyncio.sleep(0.01)
    result = await cache.get("hello", "system", "model-a")
    assert result is None


@pytest.mark.asyncio
async def test_cache_lru_eviction():
    cache = LLMCache(max_size=3, ttl_seconds=3600)
    await cache.set("prompt-1", "", "model", "r1")
    await cache.set("prompt-2", "", "model", "r2")
    await cache.set("prompt-3", "", "model", "r3")
    await cache.set("prompt-4", "", "model", "r4")
    assert await cache.get("prompt-1", "", "model") is None
    assert await cache.get("prompt-2", "", "model") == "r2"
    assert await cache.get("prompt-3", "", "model") == "r3"
    assert await cache.get("prompt-4", "", "model") == "r4"


@pytest.mark.asyncio
async def test_cache_overwrite_updates_lru():
    cache = LLMCache(max_size=2, ttl_seconds=3600)
    await cache.set("a", "", "m", "r-a")
    await cache.set("b", "", "m", "r-b")
    await cache.set("a", "", "m", "r-a-updated")
    await cache.set("c", "", "m", "r-c")
    assert await cache.get("a", "", "m") == "r-a-updated"
    assert await cache.get("b", "", "m") is None
