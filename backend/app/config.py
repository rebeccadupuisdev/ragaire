from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    anthropic_api_key: str = ""
    cohere_api_key: str = ""

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "irish_knowledge"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
