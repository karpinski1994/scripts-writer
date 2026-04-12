from fastapi import APIRouter

from app.config import get_settings
from app.llm.gemini_provider import GeminiProvider
from app.llm.groq_provider import GroqProvider
from app.llm.modal_provider import ModalProvider
from app.llm.ollama_provider import OllamaProvider
from app.schemas.settings import (
    LLMSettingsResponse,
    LLMSettingsUpdateRequest,
    LLMStatusResponse,
    ProviderConfigResponse,
    ProviderStatusResponse,
    _mask_key,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/llm", response_model=LLMSettingsResponse)
async def get_llm_settings():
    settings = get_settings()
    providers = [
        ProviderConfigResponse(
            name="modal",
            api_key_masked=_mask_key(settings.modal_api_key),
            base_url=settings.modal_base_url,
            enabled=bool(settings.modal_api_key),
            model="glm-5.1",
        ),
        ProviderConfigResponse(
            name="groq",
            api_key_masked=_mask_key(settings.groq_api_key),
            base_url="https://api.groq.com/openai/v1",
            enabled=bool(settings.groq_api_key),
            model="llama-3.3-70b-versatile",
        ),
        ProviderConfigResponse(
            name="gemini",
            api_key_masked=_mask_key(settings.gemini_api_key),
            base_url="Gemini REST API",
            enabled=bool(settings.gemini_api_key),
            model="gemini-2.0-flash",
        ),
        ProviderConfigResponse(
            name="ollama",
            api_key_masked="",
            base_url=settings.ollama_base_url,
            enabled=settings.ollama_enabled,
            model="llama3.2",
        ),
    ]
    return LLMSettingsResponse(providers=providers)


@router.patch("/llm", response_model=LLMSettingsResponse)
async def update_llm_settings(body: LLMSettingsUpdateRequest):
    import os

    from app.config import AppSettings

    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")

    updates: dict[str, str] = {}
    if body.modal:
        if body.modal.api_key is not None:
            updates["MODAL_API_KEY"] = body.modal.api_key
        if body.modal.enabled is not None:
            updates["OLLAMA_ENABLED"] = str(body.modal.enabled).lower()
    if body.groq:
        if body.groq.api_key is not None:
            updates["GROQ_API_KEY"] = body.groq.api_key
    if body.gemini:
        if body.gemini.api_key is not None:
            updates["GEMINI_API_KEY"] = body.gemini.api_key
    if body.ollama:
        if body.ollama.enabled is not None:
            updates["OLLAMA_ENABLED"] = str(body.ollama.enabled).lower()

    existing: dict[str, str] = {}
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    existing.update(updates)
    with open(env_path, "w") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

    os.environ.update(updates)
    AppSettings.model_config["env_file"] = env_path

    return await get_llm_settings()


@router.get("/llm/status", response_model=LLMStatusResponse)
async def get_llm_status():
    settings = get_settings()
    results: list[ProviderStatusResponse] = []

    if settings.modal_api_key:
        provider = ModalProvider(api_key=settings.modal_api_key, base_url=settings.modal_base_url)
        reachable = await provider.health_check()
        results.append(ProviderStatusResponse(name="modal", reachable=reachable))

    if settings.groq_api_key:
        provider = GroqProvider(api_key=settings.groq_api_key)
        reachable = await provider.health_check()
        results.append(ProviderStatusResponse(name="groq", reachable=reachable))

    if settings.gemini_api_key:
        provider = GeminiProvider(api_key=settings.gemini_api_key)
        reachable = await provider.health_check()
        results.append(ProviderStatusResponse(name="gemini", reachable=reachable))

    if settings.ollama_enabled:
        provider = OllamaProvider(base_url=settings.ollama_base_url)
        reachable = await provider.health_check()
        results.append(ProviderStatusResponse(name="ollama", reachable=reachable))

    return LLMStatusResponse(providers=results)
