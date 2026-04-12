## Why

The backend has project CRUD and a database, but no way to communicate with LLM providers. Every subsequent phase (agents, pipeline, streaming) depends on the ability to send prompts to LLMs and get responses. Without this layer, no agent can execute. Phase 2 builds the LLM adapter layer so that Phase 3 (ICP agent) and beyond can invoke language models with failover, caching, and health checking.

## What Changes

- Add abstract `LLMProvider` base class defining the provider interface (`generate`, `stream`, `health_check`)
- Add 4 concrete provider implementations: Modal (GLM-5.1 via OpenAI-compatible API), Groq (via OpenAI-compatible API), Gemini (via `google-generativeai`), Ollama (local via `ollama` SDK)
- Add `ProviderFactory` that builds providers from `AppSettings`, sorts by priority, and executes requests with automatic failover (Modal → Groq → Gemini → Ollama)
- Add `LLMCache` with LRU eviction and TTL for caching identical prompts
- Add Pydantic schemas for LLM settings (view masked keys, update keys, check provider status)
- Add Settings API endpoints: GET/PATCH `/api/v1/settings/llm` and GET `/api/v1/settings/llm/status`
- Add `scripts/test_llm.py` CLI script for manual LLM connectivity testing
- Add unit tests for providers, factory, and cache using `MockLLMProvider`

## Capabilities

### New Capabilities
- `llm-adapter`: LLM provider abstraction, 4 concrete implementations (Modal, Groq, Gemini, Ollama), provider factory with failover, LLM response cache, settings schemas, and settings API endpoints

### Modified Capabilities
- `project-crud`: Update aggregated API router to include settings endpoints under `/api/v1/settings`

## Impact

- **New files**: `app/llm/base.py`, `app/llm/modal_provider.py`, `app/llm/groq_provider.py`, `app/llm/gemini_provider.py`, `app/llm/ollama_provider.py`, `app/llm/provider_factory.py`, `app/llm/cache.py`, `app/schemas/settings.py`, `app/api/settings.py`, `scripts/test_llm.py`, `tests/unit/test_llm_providers.py`
- **Modified files**: `app/api/router.py` (add settings router), `app/config.py` (no change needed, already has all provider config fields)
- **New API surface**: 3 endpoints under `/api/v1/settings/llm`
- **External dependencies**: All already in `pyproject.toml` (openai, google-generativeai, ollama)
