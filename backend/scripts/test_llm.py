import argparse
import asyncio

from app.config import get_settings
from app.llm.errors import AllProvidersFailedError
from app.llm.provider_factory import ProviderFactory

PROVIDER_MAP = {
    "modal": lambda s: s.modal_api_key,
    "groq": lambda s: s.groq_api_key,
    "gemini": lambda s: s.gemini_api_key,
    "ollama": lambda s: s.ollama_enabled,
}


def main():
    parser = argparse.ArgumentParser(description="Test LLM provider connectivity")
    parser.add_argument("provider", choices=list(PROVIDER_MAP.keys()), help="Provider name to test")
    args = parser.parse_args()

    settings = get_settings()
    key_check = PROVIDER_MAP[args.provider](settings)

    if not key_check:
        print(f"Error: {args.provider} is not configured. Set the API key in .env and try again.")
        return 1

    factory = ProviderFactory(settings)
    provider = None
    for p in factory.providers:
        if p.provider_name == args.provider:
            provider = p
            break

    if not provider:
        print(f"Error: {args.provider} provider not found in factory.")
        return 1

    print(f"Testing {provider.get_identifier()}...")

    try:
        response = asyncio.run(provider.generate("Say hello in one sentence"))
        print(f"\nResponse: {response}")
        return 0
    except AllProvidersFailedError as e:
        print(f"\nError: {e}")
        return 1
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
