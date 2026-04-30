from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from loguru import logger

from app.config import get_settings
from app.rag.embedder import get_embedder

_DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "irish_docs"
_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50


def run_ingestion() -> int:
    """Load, chunk, embed, and upsert all documents in the irish_docs directory.

    Returns the number of chunks indexed.
    """
    logger.info("Starting ingestion from {}", _DOCS_DIR)

    loader = DirectoryLoader(str(_DOCS_DIR), glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()
    logger.info("Loaded {} documents.", len(docs))

    # Split on markdown headings first so chunks never cross section boundaries,
    # then apply character-level splitting for sections that exceed the chunk size.
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE, chunk_overlap=_CHUNK_OVERLAP
    )

    header_chunks = []
    for doc in docs:
        header_chunks.extend(header_splitter.split_text(doc.page_content))

    chunks = char_splitter.split_documents(header_chunks)
    logger.info("Split into {} chunks.", len(chunks))

    settings = get_settings()
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embedder(),
        url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
        collection_name=settings.qdrant_collection,
    )

    logger.info("Ingestion complete. {} chunks indexed.", len(chunks))
    return len(chunks)
