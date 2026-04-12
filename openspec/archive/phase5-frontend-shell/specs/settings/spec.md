## Purpose

Defines the settings page for LLM provider configuration, connectivity testing, and API key management.

## ADDED Requirements

### Requirement: Settings page shows LLM provider configuration
The system SHALL provide a page at `/settings` that fetches `GET /api/v1/settings/llm` and displays each provider's configuration: name, API key (masked showing last 4 chars), base URL, enabled status (toggle), and model name. Providers SHALL be listed in priority order: Modal, Groq, Gemini, Ollama.

#### Scenario: Settings page loads provider config
- **WHEN** the settings page loads
- **THEN** all configured providers are shown with masked API keys, base URLs, and enabled toggles

### Requirement: Update LLM provider settings
The system SHALL provide a "Save" button that calls `PATCH /api/v1/settings/llm` with updated provider configurations (API keys and enabled flags). After successful save, a success toast SHALL be shown.

#### Scenario: Save provider settings
- **WHEN** the user updates an API key and clicks Save
- **THEN** `PATCH /api/v1/settings/llm` is called with the updated config and a success toast is shown

### Requirement: Test provider connectivity
The system SHALL provide a "Test Connection" button per provider (or "Test All" button) that calls `GET /api/v1/settings/llm/status` and displays a green checkmark or red X next to each provider based on reachability.

#### Scenario: Test connection shows provider status
- **WHEN** the "Test Connection" button is clicked
- **THEN** `GET /api/v1/settings/llm/status` is called and each provider shows a green checkmark (reachable) or red X (unreachable)

### Requirement: Zustand settings store
The system SHALL provide `settings-store.ts` with Zustand managing local editing state for provider config before saving. The store SHALL track pending API key changes and enabled toggles separately from the server state.

#### Scenario: Local edits before save
- **WHEN** the user types a new API key in the settings form
- **THEN** the local store is updated but the backend is not called until Save is clicked

### Requirement: TypeScript types for settings
The system SHALL define `ProviderConfig`, `LLMSettings`, `ProviderStatus`, `LLMStatus` interfaces matching backend `ProviderConfigResponse`, `LLMSettingsResponse`, `ProviderStatusResponse`, `LLMStatusResponse` schemas.

#### Scenario: Settings types match backend
- **WHEN** settings are fetched from `GET /api/v1/settings/llm`
- **THEN** the response data can be assigned to a `LLMSettings` typed variable without type errors
