## 1. Abstract Provider & Error Classes

- [x] 1.1 Create `backend/app/llm/base.py` with `LLMProvider(ABC)` abstract class: `provider_name: str`, `model_name: str`, `priority: int` properties; abstract `generate(prompt, system_prompt, model) -> str`, abstract `stream(prompt, system_prompt, model) -> AsyncIterator[str]`, abstract `health_check() -> bool`, `get_identifier() -> str`
- [x] 1.2 Create `backend/app/llm/errors.py` with custom exceptions: `AllProvidersFailedError`, `RateLimitExhaustedError`
- [x] 1.3 Verify: `uv run python -c "from app.llm.base import LLMProvider; LLMProvider()"` raises TypeError

## 2. Concrete Provider Implementations

- [x] 2.1 Create `backend/app/llm/modal_provider.py` — `ModalProvider(LLMProvider)` using `openai.AsyncOpenAI(api_key, base_url="https://api.us-west-2.modal.direct/v1")`. Implement `generate()` (async chat completion), `stream()` (async streaming chat completion), `health_check()` (1-token generation)
- [x] 2.2 Create `backend/app/llm/groq_provider.py` — `GroqProvider(LLMProvider)` using `openai.AsyncOpenAI(api_key, base_url="https://api.groq.com/openai/v1")`. Same interface as Modal
- [x] 2.3 Create `backend/app/llm/gemini_provider.py` — `GeminiProvider(LLMProvider)` using `google.generativeai.GenerativeModel`. Implement `generate()`, `stream()`, `health_check()`
- [x] 2.4 Create `backend/app/llm/ollama_provider.py` — `OllamaProvider(LLMProvider)` using `ollama` async client. Implement `generate()`, `stream()`, `health_check()` (catch `ConnectionError` → return False)
- [x] 2.5 Verify: all 4 providers import without error: `uv run python -c "from app.llm.modal_provider import ModalProvider; from app.llm.groq_provider import GroqProvider; from app.llm.gemini_provider import GeminiProvider; from app.llm.ollama_provider import OllamaProvider; print('ok')"`

## 3. Provider Factory & Cache

- [x] 3.1 Create `backend/app/llm/provider_factory.py` — `ProviderFactory(settings: AppSettings)` that builds providers, sorts by priority, has `get_provider() -> LLMProvider | None`, `execute_with_failover(prompt, system_prompt) -> str` (retry with exponential backoff on 429/5xx, skip on 4xx auth, failover chain, raise `AllProvidersFailedError` if all fail)
- [x] 3.2 Create `backend/app/llm/cache.py` — `LLMCache` with `OrderedDict`, `max_size`, `ttl_seconds`, `_make_key()` using SHA256, `get()` (check TTL, LRU move_to_end), `set()` (add/move_to_end, evict oldest if over max_size)
- [x] 3.3 Verify: `uv run python -c "from app.llm.provider_factory import ProviderFactory; from app.llm.cache import LLMCache; print('ok')"`

## 4. Settings Schemas & API

- [x] 4.1 Create `backend/app/schemas/settings.py` — `LLMSettingsResponse` (provider configs with masked API keys), `LLMSettingsUpdateRequest` (api_key, enabled per provider), `LLMStatusResponse` (provider name → reachable boolean)
- [x] 4.2 Create `backend/app/api/settings.py` — `GET /api/v1/settings/llm` (return masked config), `PATCH /api/v1/settings/llm` (update .env/keys), `GET /api/v1/settings/llm/status` (run health_check on each configured provider)
- [x] 4.3 Update `backend/app/api/router.py` — include settings router in the aggregated router
- [x] 4.4 Verify: `uv run python -c "from app.api.router import router; print('ok')"` imports without circular dependency

## 5. Test Script

- [x] 5.1 Create `backend/scripts/test_llm.py` — CLI script using `argparse`, takes provider name as positional arg, builds `ProviderFactory` from `AppSettings`, calls `generate()` with "Say hello in one sentence", prints response. Handle missing API keys with clear error messages
- [x] 5.2 Verify: `uv run python scripts/test_llm.py modal` runs (will error if no key, but script loads and gives a clear message)

## 6. Tests

- [x] 6.1 Create `backend/tests/unit/test_llm_cache.py` — test cache hit, miss, TTL expiry, LRU eviction at max_size
- [x] 6.2 Create `backend/tests/unit/test_llm_providers.py` — `MockLLMProvider` (controllable success/failure), test: successful generation, rate limit error, failover from one provider to next, all providers fail → `AllProvidersFailedError`, auth error skips provider, cache hit/miss with factory
- [x] 6.3 Verify: `uv run pytest tests/unit/test_llm_cache.py tests/unit/test_llm_providers.py -v` passes all tests
