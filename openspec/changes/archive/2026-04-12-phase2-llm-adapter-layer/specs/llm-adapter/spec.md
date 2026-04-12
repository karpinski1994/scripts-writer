## Purpose

Defines the LLM provider abstraction layer including abstract provider interface, 4 concrete implementations (Modal, Groq, Gemini, Ollama), provider factory with failover, LLM response cache, and settings API endpoints for viewing, updating, and testing LLM provider connectivity.

## ADDED Requirements

### Requirement: Abstract LLM provider interface
The system SHALL define an abstract `LLMProvider` class with `provider_name`, `model_name`, and `priority` properties, and abstract methods `generate()`, `stream()`, and `health_check()`. The class SHALL NOT be instantiable directly.

#### Scenario: Cannot instantiate LLMProvider directly
- **WHEN** code attempts `LLMProvider()`
- **THEN** a `TypeError` is raised because the class is abstract

#### Scenario: Concrete subclass implements all methods
- **WHEN** a class inherits from `LLMProvider` and implements `generate()`, `stream()`, and `health_check()`
- **THEN** the class can be instantiated without error

### Requirement: Modal LLM provider
The system SHALL provide a `ModalProvider` that uses the OpenAI-compatible SDK with `base_url="https://api.us-west-2.modal.direct/v1"` and the configured `modal_api_key`. It SHALL implement `generate()` (non-streaming text generation), `stream()` (yielding tokens), and `health_check()` (testing connectivity with a 1-token generation).

#### Scenario: Modal provider generates text
- **WHEN** `ModalProvider.generate(prompt="Say hello")` is called with a valid API key
- **THEN** a non-empty string response is returned

#### Scenario: Modal provider handles rate limit
- **WHEN** the Modal API returns HTTP 429
- **THEN** a `RateLimitError` is raised that the factory can catch for failover

### Requirement: Groq LLM provider
The system SHALL provide a `GroqProvider` that uses the OpenAI-compatible SDK with `base_url="https://api.groq.com/openai/v1"` and the configured `groq_api_key`. It SHALL implement the same `generate()`, `stream()`, and `health_check()` interface as ModalProvider.

#### Scenario: Groq provider generates text
- **WHEN** `GroqProvider.generate(prompt="Say hello")` is called with a valid API key
- **THEN** a non-empty string response is returned

### Requirement: Gemini LLM provider
The system SHALL provide a `GeminiProvider` that uses the `google-generativeai` SDK with the configured `gemini_api_key`. It SHALL implement the same `generate()`, `stream()`, and `health_check()` interface.

#### Scenario: Gemini provider generates text
- **WHEN** `GeminiProvider.generate(prompt="Say hello")` is called with a valid API key
- **THEN** a non-empty string response is returned

### Requirement: Ollama LLM provider
The system SHALL provide an `OllamaProvider` that uses the `ollama` SDK with `base_url` defaulting to `http://localhost:11434`. It SHALL implement the same `generate()`, `stream()`, and `health_check()` interface. If Ollama is not running, `health_check()` SHALL return `False` without raising an exception.

#### Scenario: Ollama provider handles connection refused
- **WHEN** `OllamaProvider.health_check()` is called and Ollama is not running
- **THEN** `False` is returned without raising an exception

#### Scenario: Ollama is disabled by default
- **WHEN** `AppSettings.ollama_enabled` is `False`
- **THEN** `OllamaProvider` is not included in the failover chain

### Requirement: Provider factory with failover
The system SHALL provide a `ProviderFactory` that builds providers from `AppSettings`, orders them by priority, and exposes `get_provider()` (returns first healthy provider) and `execute_with_failover(prompt, system_prompt)` (executes with automatic failover chain). On rate limit or 5xx errors, the factory SHALL retry with exponential backoff up to `max_retries` per provider, then failover to the next provider. On 4xx auth errors, the factory SHALL skip the provider immediately. If all providers fail, `AllProvidersFailedError` SHALL be raised.

#### Scenario: Failover from Modal to Groq
- **WHEN** `execute_with_failover()` is called and Modal fails with a rate limit error
- **THEN** the factory retries Modal up to `max_retries`, then fails over to Groq

#### Scenario: All providers fail
- **WHEN** `execute_with_failover()` is called and all providers fail
- **THEN** an `AllProvidersFailedError` is raised with a summary of which providers failed

#### Scenario: Auth error skips provider immediately
- **WHEN** a provider returns a 4xx authentication error
- **THEN** the factory skips that provider without retrying and moves to the next

### Requirement: LLM response cache
The system SHALL provide an `LLMCache` with LRU eviction (configurable `max_size`, default 128), TTL (configurable `ttl_seconds`, default 3600), `get()`/`set()` methods keyed by SHA256 hash of `model:system_prompt:prompt`. Expired entries SHALL be evicted on access. When `max_size` is exceeded, the oldest entry SHALL be evicted.

#### Scenario: Cache hit on identical prompt
- **WHEN** the same `(prompt, system_prompt, model)` combination is requested twice within TTL
- **THEN** the second call returns the cached value without calling the LLM

#### Scenario: Cache miss on expired entry
- **WHEN** a cached entry's TTL has expired and `get()` is called
- **THEN** `None` is returned and the entry is removed

#### Scenario: Cache eviction at max_size
- **WHEN** 129 unique entries are added with `max_size=128`
- **THEN** the first (oldest) entry is evicted

### Requirement: LLM settings schemas
The system SHALL define Pydantic schemas: `LLMSettingsResponse` (provider configs with masked API keys showing last 4 chars), `LLMSettingsUpdateRequest` (API key updates, enabled toggles), and `LLMStatusResponse` (mapping of provider name to reachable boolean).

#### Scenario: API keys are masked in response
- **WHEN** `GET /api/v1/settings/llm` is called
- **THEN** API keys are returned as `****abcd` (last 4 chars visible)

#### Scenario: Settings update persists
- **WHEN** `PATCH /api/v1/settings/llm` is called with a new API key
- **THEN** the key is updated and subsequent GET requests show the new masked key

### Requirement: Settings API endpoints
The system SHALL expose 3 endpoints: `GET /api/v1/settings/llm` (current config with masked keys), `PATCH /api/v1/settings/llm` (update config), and `GET /api/v1/settings/llm/status` (run health_check on each configured provider and return reachable status).

#### Scenario: Provider status check
- **WHEN** `GET /api/v1/settings/llm/status` is called with a valid Modal API key
- **THEN** the response includes `{"modal": true}` if the provider is reachable

#### Scenario: Provider status shows unreachable
- **WHEN** `GET /api/v1/settings/llm/status` is called with an invalid API key
- **THEN** the response includes `{"modal": false}` for that provider

### Requirement: LLM connectivity test script
The system SHALL provide `backend/scripts/test_llm.py` that accepts a provider name as a CLI argument, sends a minimal prompt, and prints the LLM response or an error message.

#### Scenario: Test Modal provider
- **WHEN** `uv run python scripts/test_llm.py modal` is executed with a valid API key
- **THEN** an LLM-generated greeting is printed to stdout

#### Scenario: Test with missing API key
- **WHEN** `uv run python scripts/test_llm.py modal` is executed without an API key
- **THEN** a clear error message is printed indicating the API key is not configured
