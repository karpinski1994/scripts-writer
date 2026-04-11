from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    modal_api_key: str = ""
    modal_base_url: str = "https://api.us-west-2.modal.direct/v1"
    groq_api_key: str = ""
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_enabled: bool = False
    database_url: str = "sqlite+aiosqlite:///./data/scripts_writer.db"
    export_dir: str = "./data/exports"
    log_level: str = "INFO"
    cache_max_size: int = 128
    cache_ttl_seconds: int = 3600
    max_retries: int = 3
    debounce_save_ms: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> AppSettings:
    return AppSettings()
