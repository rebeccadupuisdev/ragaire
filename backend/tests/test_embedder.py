from unittest.mock import MagicMock, patch

import pytest

from app.rag.embedder import get_embedder

_EMBEDDER_MOD = "app.rag.embedder"


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure lru_cache does not leak state between tests."""
    get_embedder.cache_clear()
    yield
    get_embedder.cache_clear()


class TestGetEmbedder:
    def test_returns_object_produced_by_cohere_embeddings(self):
        with patch(f"{_EMBEDDER_MOD}.CohereEmbeddings") as MockCohere:
            mock_instance = MagicMock(name="embeddings")
            MockCohere.return_value = mock_instance

            result = get_embedder()

        assert result is mock_instance

    def test_uses_multilingual_v3_model(self):
        with patch(f"{_EMBEDDER_MOD}.CohereEmbeddings") as MockCohere:
            get_embedder()

        MockCohere.assert_called_once_with(model="embed-multilingual-v3.0")

    def test_returns_same_instance_on_repeated_calls(self):
        """The lru_cache ensures CohereEmbeddings is only instantiated once."""
        with patch(f"{_EMBEDDER_MOD}.CohereEmbeddings") as MockCohere:
            MockCohere.return_value = MagicMock(name="embeddings")

            first = get_embedder()
            second = get_embedder()

        assert first is second
        MockCohere.assert_called_once()

    def test_raises_when_cohere_constructor_fails(self):
        """Constructor errors (e.g. missing API key) propagate to the caller."""
        with patch(f"{_EMBEDDER_MOD}.CohereEmbeddings", side_effect=ValueError("missing key")):
            with pytest.raises(ValueError, match="missing key"):
                get_embedder()
