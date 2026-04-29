from unittest.mock import MagicMock, patch

import pytest
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance

from app.vector_store.qdrant_client import ensure_collection, get_client
from tests.conftest import TEST_COLLECTION, TEST_HOST, TEST_PORT, _SETTINGS_PATH


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_not_found() -> UnexpectedResponse:
    """Build the UnexpectedResponse that Qdrant raises for a missing collection."""
    return UnexpectedResponse(
        status_code=404,
        reason_phrase=b"Not Found",
        content=b"",
        headers={},
    )


# ---------------------------------------------------------------------------
# ensure_collection tests
# ---------------------------------------------------------------------------

class TestEnsureCollection:
    def test_creates_collection_when_absent(self, mock_settings):
        """create_collection is called exactly once when the collection does not exist."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = _make_not_found()

        ensure_collection(mock_client)

        mock_client.create_collection.assert_called_once()

    def test_creates_collection_with_correct_name(self, mock_settings):
        """create_collection receives the collection name from settings."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = _make_not_found()

        ensure_collection(mock_client)

        call_kwargs = mock_client.create_collection.call_args.kwargs
        assert call_kwargs["collection_name"] == TEST_COLLECTION

    def test_creates_collection_with_correct_vectors_config(self, mock_settings):
        """create_collection is called with size=1024 and COSINE distance."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = _make_not_found()

        ensure_collection(mock_client)

        vectors_config = mock_client.create_collection.call_args.kwargs["vectors_config"]
        assert vectors_config.size == 1024
        assert vectors_config.distance == Distance.COSINE

    def test_skips_creation_when_collection_exists(self, mock_settings):
        """create_collection is never called when the collection already exists."""
        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock()

        ensure_collection(mock_client)

        mock_client.create_collection.assert_not_called()

    def test_reraises_non_404_unexpected_response(self, mock_settings):
        """Non-404 UnexpectedResponse exceptions propagate to the caller."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = UnexpectedResponse(
            status_code=500,
            reason_phrase=b"Internal Server Error",
            content=b"",
            headers={},
        )

        with pytest.raises(UnexpectedResponse):
            ensure_collection(mock_client)

        mock_client.create_collection.assert_not_called()

    def test_creates_collection_on_plain_not_found_error(self, mock_settings):
        """Plain exception with 'not found' in its message triggers collection creation."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = ValueError("not found: collection missing")

        ensure_collection(mock_client)

        mock_client.create_collection.assert_called_once()

    def test_reraises_plain_error_without_not_found(self, mock_settings):
        """Plain exception whose message does not contain 'not found' propagates."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = ValueError("connection refused")

        with pytest.raises(ValueError, match="connection refused"):
            ensure_collection(mock_client)

        mock_client.create_collection.assert_not_called()

    def test_reraises_when_create_collection_fails(self, mock_settings):
        """If create_collection itself raises, the exception propagates."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = _make_not_found()
        mock_client.create_collection.side_effect = RuntimeError("disk full")

        with pytest.raises(RuntimeError, match="disk full"):
            ensure_collection(mock_client)


# ---------------------------------------------------------------------------
# get_client tests
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_returns_qdrant_client_instance(self):
        """get_client() returns the QdrantClient instance produced by the constructor."""
        with patch("app.vector_store.qdrant_client.QdrantClient") as MockQdrant:
            mock_instance = MagicMock(spec=QdrantClient)
            MockQdrant.return_value = mock_instance

            client = get_client()

        assert client is mock_instance

    def test_constructs_client_with_host_and_port_from_settings(self):
        """QdrantClient is constructed using host and port read from settings."""
        with patch(_SETTINGS_PATH) as mock_get_settings, \
             patch("app.vector_store.qdrant_client.QdrantClient") as MockQdrant:
            settings = MagicMock()
            settings.qdrant_host = TEST_HOST
            settings.qdrant_port = TEST_PORT
            mock_get_settings.return_value = settings
            MockQdrant.return_value = MagicMock(spec=QdrantClient)

            get_client()

        MockQdrant.assert_called_once_with(host=TEST_HOST, port=TEST_PORT)

    def test_singleton_returns_same_instance(self):
        """Calling get_client() twice returns the exact same object (lru_cache)."""
        with patch("app.vector_store.qdrant_client.QdrantClient") as MockQdrant:
            MockQdrant.return_value = MagicMock()

            first = get_client()
            second = get_client()

        assert first is second
        assert MockQdrant.call_count == 1
