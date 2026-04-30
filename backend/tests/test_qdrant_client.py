from unittest.mock import MagicMock, call, patch

import pytest
from qdrant_client.http.exceptions import UnexpectedResponse

from app.vector_store.qdrant_client import (
    _is_not_found,
    ensure_collection,
    get_client,
)

_CLIENT_MOD = "app.vector_store.qdrant_client"


def _unexpected_response(status_code: int) -> UnexpectedResponse:
    """Construct a minimal UnexpectedResponse without calling its full __init__."""
    exc = Exception.__new__(UnexpectedResponse)
    exc.status_code = status_code
    return exc


@pytest.fixture(autouse=True)
def clear_client_cache():
    get_client.cache_clear()
    yield
    get_client.cache_clear()


# ---------------------------------------------------------------------------
# _is_not_found
# ---------------------------------------------------------------------------

class TestIsNotFound:
    def test_unexpected_response_404_returns_true(self):
        assert _is_not_found(_unexpected_response(404)) is True

    def test_unexpected_response_500_returns_false(self):
        assert _is_not_found(_unexpected_response(500)) is False

    def test_unexpected_response_403_returns_false(self):
        assert _is_not_found(_unexpected_response(403)) is False

    def test_value_error_with_not_found_returns_true(self):
        assert _is_not_found(ValueError("collection not found")) is True

    def test_value_error_without_not_found_returns_false(self):
        assert _is_not_found(ValueError("some other error")) is False

    def test_runtime_error_with_not_found_string_returns_true(self):
        """The fallback check is case-insensitive to 'not found' in str(exc)."""
        assert _is_not_found(RuntimeError("resource not found in store")) is True

    def test_generic_exception_returns_false(self):
        assert _is_not_found(RuntimeError("connection refused")) is False


# ---------------------------------------------------------------------------
# get_client
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_returns_qdrant_client_instance(self):
        with patch(f"{_CLIENT_MOD}.QdrantClient") as MockClient, \
             patch(f"{_CLIENT_MOD}.get_settings") as mock_settings:
            mock_settings.return_value.qdrant_host = "localhost"
            mock_settings.return_value.qdrant_port = 6333

            result = get_client()

        assert result is MockClient.return_value

    def test_returns_same_instance_on_repeated_calls(self):
        """lru_cache ensures QdrantClient is only instantiated once."""
        with patch(f"{_CLIENT_MOD}.QdrantClient") as MockClient, \
             patch(f"{_CLIENT_MOD}.get_settings") as mock_settings:
            mock_settings.return_value.qdrant_host = "localhost"
            mock_settings.return_value.qdrant_port = 6333
            MockClient.return_value = MagicMock()

            first = get_client()
            second = get_client()

        assert first is second
        MockClient.assert_called_once()

    def test_connects_to_configured_host_and_port(self):
        with patch(f"{_CLIENT_MOD}.QdrantClient") as MockClient, \
             patch(f"{_CLIENT_MOD}.get_settings") as mock_settings:
            mock_settings.return_value.qdrant_host = "my-host"
            mock_settings.return_value.qdrant_port = 1234

            get_client()

        MockClient.assert_called_once_with(host="my-host", port=1234)


# ---------------------------------------------------------------------------
# ensure_collection
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def mock_settings_patch():
    with patch(f"{_CLIENT_MOD}.get_settings") as patched:
        patched.return_value.qdrant_collection = "test_collection"
        yield patched


class TestEnsureCollection:
    def test_skips_creation_when_collection_exists(self, mock_client, mock_settings_patch):
        """get_collection succeeding means collection exists; create_collection not called."""
        ensure_collection(mock_client)

        mock_client.get_collection.assert_called_once_with("test_collection")
        mock_client.create_collection.assert_not_called()

    def test_creates_collection_when_404_response(self, mock_client, mock_settings_patch):
        """An UnexpectedResponse with status 404 triggers collection creation."""
        mock_client.get_collection.side_effect = _unexpected_response(404)

        ensure_collection(mock_client)

        mock_client.create_collection.assert_called_once()

    def test_creates_collection_with_correct_name(self, mock_client, mock_settings_patch):
        mock_client.get_collection.side_effect = _unexpected_response(404)

        ensure_collection(mock_client)

        call_kwargs = mock_client.create_collection.call_args.kwargs
        assert call_kwargs["collection_name"] == "test_collection"

    def test_creates_collection_with_1024_cosine_vectors(self, mock_client, mock_settings_patch):
        """Vector size must match Cohere embed-multilingual-v3.0 output dimensions."""
        from qdrant_client.models import Distance, VectorParams

        mock_client.get_collection.side_effect = _unexpected_response(404)

        ensure_collection(mock_client)

        call_kwargs = mock_client.create_collection.call_args.kwargs
        vectors_config = call_kwargs["vectors_config"]
        assert vectors_config.size == 1024
        assert vectors_config.distance == Distance.COSINE

    def test_creates_collection_when_not_found_value_error(self, mock_client, mock_settings_patch):
        """A ValueError with 'not found' is treated as a missing collection."""
        mock_client.get_collection.side_effect = ValueError("collection not found")

        ensure_collection(mock_client)

        mock_client.create_collection.assert_called_once()

    def test_reraises_non_404_unexpected_response(self, mock_client, mock_settings_patch):
        """A non-404 UnexpectedResponse (e.g. 500) is not swallowed."""
        mock_client.get_collection.side_effect = _unexpected_response(500)

        with pytest.raises(UnexpectedResponse):
            ensure_collection(mock_client)

        mock_client.create_collection.assert_not_called()

    def test_reraises_unrelated_exception(self, mock_client, mock_settings_patch):
        """Arbitrary exceptions from get_collection are re-raised."""
        mock_client.get_collection.side_effect = ConnectionError("network failure")

        with pytest.raises(ConnectionError):
            ensure_collection(mock_client)

        mock_client.create_collection.assert_not_called()
