import pytest

from app.config import Settings, get_settings

_CONFIG_MOD = "app.config"


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Settings defaults
# ---------------------------------------------------------------------------

def _clean_settings(monkeypatch) -> Settings:
    """Return a Settings instance isolated from .env and inherited env vars."""
    for var in ("QDRANT_HOST", "QDRANT_PORT", "QDRANT_COLLECTION",
                "ANTHROPIC_API_KEY", "COHERE_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    return Settings(_env_file=None)


class TestSettingsDefaults:
    def test_qdrant_host_defaults_to_localhost(self, monkeypatch):
        assert _clean_settings(monkeypatch).qdrant_host == "localhost"

    def test_qdrant_port_defaults_to_6333(self, monkeypatch):
        assert _clean_settings(monkeypatch).qdrant_port == 6333

    def test_qdrant_collection_defaults_to_irish_knowledge(self, monkeypatch):
        assert _clean_settings(monkeypatch).qdrant_collection == "irish_knowledge"

    def test_anthropic_api_key_defaults_to_empty_string(self, monkeypatch):
        assert _clean_settings(monkeypatch).anthropic_api_key == ""

    def test_cohere_api_key_defaults_to_empty_string(self, monkeypatch):
        assert _clean_settings(monkeypatch).cohere_api_key == ""

    def test_settings_accepts_env_overrides(self, monkeypatch):
        monkeypatch.setenv("QDRANT_HOST", "remote-host")
        monkeypatch.setenv("QDRANT_PORT", "9999")
        monkeypatch.setenv("QDRANT_COLLECTION", "my_collection")

        settings = Settings(_env_file=None)

        assert settings.qdrant_host == "remote-host"
        assert settings.qdrant_port == 9999
        assert settings.qdrant_collection == "my_collection"


# ---------------------------------------------------------------------------
# get_settings cache
# ---------------------------------------------------------------------------

class TestGetSettings:
    def test_returns_settings_instance(self):
        result = get_settings()

        assert isinstance(result, Settings)

    def test_returns_same_instance_on_repeated_calls(self):
        """lru_cache ensures Settings is only instantiated once per process."""
        first = get_settings()
        second = get_settings()

        assert first is second
