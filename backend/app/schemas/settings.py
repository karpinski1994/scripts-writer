from pydantic import BaseModel


def _mask_key(key: str) -> str:
    if not key:
        return ""
    return f"****{key[-4:]}"


class ProviderConfigResponse(BaseModel):
    name: str
    api_key_masked: str
    base_url: str
    enabled: bool
    model: str


class LLMSettingsResponse(BaseModel):
    providers: list[ProviderConfigResponse]


class ProviderUpdateRequest(BaseModel):
    api_key: str | None = None
    enabled: bool | None = None


class LLMSettingsUpdateRequest(BaseModel):
    modal: ProviderUpdateRequest | None = None
    groq: ProviderUpdateRequest | None = None
    gemini: ProviderUpdateRequest | None = None
    ollama: ProviderUpdateRequest | None = None


class ProviderStatusResponse(BaseModel):
    name: str
    reachable: bool


class LLMStatusResponse(BaseModel):
    providers: list[ProviderStatusResponse]
