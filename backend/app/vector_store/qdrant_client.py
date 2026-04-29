from functools import lru_cache

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from app.config import get_settings


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    """Return a cached QdrantClient connected to the configured host and port."""
    settings = get_settings()
    logger.info(
        "Connecting to Qdrant at {}:{}", settings.qdrant_host, settings.qdrant_port
    )
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def ensure_collection(client: QdrantClient) -> None:
    """Create the vector collection if it does not already exist.

    Safe to call on every startup — a 404-style response from Qdrant means the
    collection is absent; any other exception is re-raised.

    Vector size 1024 matches Cohere embed-multilingual-v3.0 output dimensions.
    """
    collection_name = get_settings().qdrant_collection
    try:
        client.get_collection(collection_name)
        logger.info("Collection '{}' already exists — skipping creation.", collection_name)
    except (UnexpectedResponse, Exception) as exc:
        # Qdrant raises UnexpectedResponse (404) when the collection is missing.
        # We create it only on that specific signal; all other exceptions bubble up.
        if _is_not_found(exc):
            logger.info("Creating collection '{}'.", collection_name)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
        else:
            raise


def _is_not_found(exc: Exception) -> bool:
    """Return True when the exception signals a missing collection (HTTP 404)."""
    if isinstance(exc, UnexpectedResponse):
        return exc.status_code == 404
    # Fallback: some older qdrant-client versions raise a plain ValueError.
    return "not found" in str(exc).lower()
