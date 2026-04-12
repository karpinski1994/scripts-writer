class AllProvidersFailedError(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        provider_details = ", ".join(f"{k}: {v}" for k, v in errors.items())
        super().__init__(f"All LLM providers failed: {provider_details}")


class RateLimitExhaustedError(Exception):
    def __init__(self, provider_name: str, retries: int):
        self.provider_name = provider_name
        self.retries = retries
        super().__init__(f"Rate limit exhausted for {provider_name} after {retries} retries")
