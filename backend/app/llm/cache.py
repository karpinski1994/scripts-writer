import hashlib
import time
from collections import OrderedDict


class LLMCache:
    def __init__(self, max_size: int = 128, ttl_seconds: int = 3600):
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _make_key(self, prompt: str, system_prompt: str, model: str) -> str:
        raw = f"{model}:{system_prompt}:{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, prompt: str, system_prompt: str, model: str) -> str | None:
        key = self._make_key(prompt, system_prompt, model)
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                self._cache.move_to_end(key)
                return value
            del self._cache[key]
        return None

    async def set(self, prompt: str, system_prompt: str, model: str, value: str) -> None:
        key = self._make_key(prompt, system_prompt, model)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, time.time())
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
