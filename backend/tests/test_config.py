import pytest

from app.config import Settings, get_settings


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch):
    """Settings should load with sensible defaults when no env vars are set."""
    monkeypatch.delenv("QDRANT_HOST", raising=False)
    monkeypatch.delenv("QDRANT_PORT", raising=False)
    monkeypatch.delenv("QDRANT_COLLECTION", raising=False)
    settings = Settings(
        anthropic_api_key="test-anthropic-key",
        cohere_api_key="test-cohere-key",
    )
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333
    assert settings.qdrant_collection == "irish_knowledge"


def test_settings_override_via_env(monkeypatch: pytest.MonkeyPatch):
    """Settings should reflect values from environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-anthropic")
    monkeypatch.setenv("COHERE_API_KEY", "env-cohere")
    monkeypatch.setenv("QDRANT_HOST", "qdrant-container")
    monkeypatch.setenv("QDRANT_PORT", "6334")
    monkeypatch.setenv("QDRANT_COLLECTION", "test_collection")

    settings = Settings()
    assert settings.anthropic_api_key == "env-anthropic"
    assert settings.cohere_api_key == "env-cohere"
    assert settings.qdrant_host == "qdrant-container"
    assert settings.qdrant_port == 6334
    assert settings.qdrant_collection == "test_collection"


def test_get_settings_returns_same_instance():
    """get_settings() should return a cached singleton."""
    settings_a = get_settings()
    settings_b = get_settings()
    assert settings_a is settings_b
