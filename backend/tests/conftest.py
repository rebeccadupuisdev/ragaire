from unittest.mock import MagicMock, patch

import pytest

_SETTINGS_PATH = "app.vector_store.qdrant_client.get_settings"

TEST_COLLECTION = "test_collection"
TEST_HOST = "test-host"
TEST_PORT = 9999


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all lru_cache functions before and after every test."""
    from app.config import get_settings
    from app.rag.embedder import get_embedder
    from app.vector_store.qdrant_client import get_client

    get_client.cache_clear()
    get_embedder.cache_clear()
    get_settings.cache_clear()
    yield
    get_client.cache_clear()
    get_embedder.cache_clear()
    get_settings.cache_clear()


@pytest.fixture
def mock_settings():
    """Patch get_settings with deterministic test values."""
    with patch(_SETTINGS_PATH) as patched:
        settings = MagicMock()
        settings.qdrant_collection = TEST_COLLECTION
        settings.qdrant_host = TEST_HOST
        settings.qdrant_port = TEST_PORT
        patched.return_value = settings
        yield settings
