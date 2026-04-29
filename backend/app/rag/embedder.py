from functools import lru_cache

from langchain_cohere import CohereEmbeddings


@lru_cache(maxsize=1)
def get_embedder() -> CohereEmbeddings:
    """Return a cached Cohere embeddings instance.

    Reads COHERE_API_KEY from the environment automatically via LangChain.
    Vector size: 1024 — matches the Qdrant collection config in qdrant_client.py.
    """
    return CohereEmbeddings(model="embed-multilingual-v3.0")
