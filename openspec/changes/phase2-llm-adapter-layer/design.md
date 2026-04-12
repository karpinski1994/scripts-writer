## Context

The backend has a working FastAPI app with project CRUD and SQLite database (Phase 1 complete). The `AppSettings` class already defines all LLM-related config fields (modal_api_key, modal_base_url, groq_api_key, gemini_api_key, ollama_base_url, ollama_enabled). However, there is no code that actually calls any LLM. Every agent in subsequent phases depends on this layer.

The TRD specifies 4 LLM providers with a failover chain (Modal → Groq → Gemini → Ollama), an abstract provider interface, and a settings API for checking connectivity. The LLD defines `LLMProvider` (ABC), 4 concrete providers, `ProviderFactory`, and `LLMCache` with pseudocode.

## Goals / Non-Goals

**Goals:**
- Abstract `LLMProvider` interface that all agents will use
- 4 concrete provider implementations that can each generate and stream text
- `ProviderFactory` with priority-based failover chain
- `LLMCache` with LRU eviction and TTL for identical prompt caching
- Settings API to view/update LLM configuration and check provider health
- CLI test script for manual LLM connectivity verification
- Comprehensive unit tests using `MockLLMProvider`

**Non-Goals:**
- Agent implementations (Phase 3)
- Pipeline orchestration (Phase 3)
- WebSocket streaming (Phase 6)
- Pydantic AI integration (Phase 3)
- Frontend settings UI (Phase 5)

## Decisions

### 1. Abstract base class with ABC, not Protocol
**Choice:** Use `ABC` with `@abstractmethod` for `LLMProvider`
**Alternative:** Use `typing.Protocol` (structural typing)
**Rationale:** ABC provides clear error messages if a method is not implemented. Protocol is better for duck-typing but adds confusion for this small number of providers. The LLD class hierarchy shows explicit inheritance, so ABC matches the design.

### 2. OpenAI-compatible SDK for Modal and Groq
**Choice:** Use the `openai` Python package with custom `base_url` for both Modal and Groq
**Alternative:** Use provider-specific SDKs
**Rationale:** Both Modal and Groq expose OpenAI-compatible APIs. Using one SDK reduces code duplication. The TRD explicitly lists `openai` (OpenAI-compatible) as the SDK for both.

### 3. Async via `asyncio.to_thread` for sync SDKs
**Choice:** The `openai` and `google-generativeai` SDKs have async support natively, so we use their async methods directly. For `ollama` (which may be sync-only in some versions), fall back to `asyncio.to_thread`.
**Alternative:** Use only sync SDKs with thread wrapping everywhere
**Rationale:** Minimize thread overhead by using native async where available. Only wrap when necessary.

### 4. Provider failover with exponential backoff
**Choice:** `ProviderFactory.execute_with_failover()` tries each provider in priority order. On rate limit (429) or 5xx errors, retry with exponential backoff (1s, 2s, 4s) up to `max_retries` per provider, then failover to the next. On 4xx auth errors, skip provider immediately (no retry).
**Alternative:** Simple round-robin without retry, or single-provider with retry only
**Rationale:** Matches the TRD failover specification exactly. Auth errors are configuration issues, not transient — retrying them wastes time.

### 5. Cache key uses SHA256 of prompt + system_prompt + model
**Choice:** Hash the concatenation of `model:system_prompt:prompt` with SHA256 for the cache key
**Alternative:** Use the raw string as key, or hash with MD5
**Rationale:** SHA256 avoids key collisions and handles long prompts efficiently. MD5 is faster but has known collision weaknesses. Raw strings would create unbounded key sizes. Matches LLD pseudocode exactly.

### 6. Settings API returns masked API keys
**Choice:** `GET /api/v1/settings/llm` returns API keys with only the last 4 characters visible (e.g., `****abcd`)
**Alternative:** Return full keys, or return boolean "configured" flags
**Rationale:** Per TRD security requirements: API keys must be masked in API responses. Last-4-chars pattern is standard for confirming which key is configured without exposing it.

### 7. Provider health check hits a minimal endpoint
**Choice:** `health_check()` sends a tiny prompt ("hi") with max_tokens=1 to verify connectivity without significant cost
**Alternative:** Ping the base URL, or check API key validity only
**Rationale:** Actually calling the LLM confirms end-to-end connectivity (API key valid, service up, model available). A 1-token generation costs fractions of a cent.

## Risks / Trade-offs

- **[Risk] OpenAI SDK version changes** → Mitigation: Pin `openai>=2.31.0` in dependencies. The v2 API is stable and well-documented.

- **[Risk] Google Gemini SDK has different response format** → Mitigation: The `GeminiProvider` normalizes the response to the same string output as other providers. Agent code never sees provider-specific formats.

- **[Risk] Ollama not running on user's machine** → Mitigation: `OllamaProvider.health_check()` catches `ConnectionError` and returns `False`. The settings API shows Ollama as unreachable. Provider is last in failover chain so it only runs if all cloud providers fail.

- **[Trade-off] In-memory cache only** → Cache is lost on restart. Mitigation: LLM responses are already persisted in `pipeline_steps.output_data`. The cache only avoids re-generating within a single session.

- **[Trade-off] No rate limiting on our side** → We rely on provider-side rate limits. Mitigation: For a single-user local app, provider-side limits are sufficient. If needed later, add a token counter middleware.
