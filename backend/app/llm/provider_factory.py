import asyncio
import logging

from openai import AuthenticationError, RateLimitError

from app.config import AppSettings
from app.llm.base import LLMProvider
from app.llm.errors import AllProvidersFailedError
from app.llm.gemini_provider import GeminiProvider
from app.llm.groq_provider import GroqProvider
from app.llm.modal_provider import ModalProvider
from app.llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._providers: list[LLMProvider] = []
        self._build_providers()

    def _build_providers(self) -> None:
        providers: list[LLMProvider] = []
        if self._settings.modal_api_key:
            providers.append(
                ModalProvider(
                    api_key=self._settings.modal_api_key,
                    base_url=self._settings.modal_base_url,
                    model=self._settings.modal_model_name,
                )
            )
        if self._settings.groq_api_key:
            providers.append(GroqProvider(api_key=self._settings.groq_api_key))
        if self._settings.gemini_api_key:
            providers.append(
                GeminiProvider(
                    api_key=self._settings.gemini_api_key,
                    model=self._settings.gemini_model,
                )
            )
        if self._settings.ollama_enabled:
            providers.append(OllamaProvider(base_url=self._settings.ollama_base_url))
        self._providers = sorted(providers, key=lambda p: p.priority)

    @property
    def providers(self) -> list[LLMProvider]:
        return list(self._providers)

    def get_provider(self) -> LLMProvider | None:
        return self._providers[0] if self._providers else None

    async def execute_with_failover(self, prompt: str, system_prompt: str = "") -> str:
        if not self._providers:
            raise AllProvidersFailedError({"factory": "No providers configured"})

        logger.info("=== LLM REQUEST ===")
        logger.info(f"Provider order: {[p.provider_name for p in self._providers]}")
        logger.info(f"System prompt:\n{system_prompt}")
        logger.info(f"User prompt:\n{prompt}")

        errors: dict[str, str] = {}
        for provider in self._providers:
            try:
                logger.info(f"Calling provider: {provider.provider_name} ({provider.model_name})")
                result = await self._execute_with_retry(provider, prompt, system_prompt)
                logger.info(f"=== LLM RESPONSE from {provider.provider_name} ===")
                logger.info(f"Response:\n{result}")
                return result
            except AuthenticationError:
                logger.warning(f"Auth error for {provider.provider_name}, skipping")
                errors[provider.provider_name] = "Authentication failed"
                continue
            except Exception as e:
                errors[provider.provider_name] = str(e)
                logger.warning(f"Provider {provider.provider_name} failed: {e}")
                continue

        raise AllProvidersFailedError(errors)

    async def _execute_with_retry(self, provider: LLMProvider, prompt: str, system_prompt: str) -> str:
        max_retries = self._settings.max_retries
        for attempt in range(max_retries):
            try:
                return await provider.generate(prompt, system_prompt)
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.info(
                        f"Rate limited on {provider.provider_name}, "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
