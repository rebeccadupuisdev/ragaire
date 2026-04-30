import time
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
# Cohere trial limit is 100k tokens/min. Each ~500-char chunk ≈ 125 tokens,
# so 96 chunks ≈ 12k tokens. An 8-second pause between batches keeps throughput
# safely under the cap (~90k tokens/min at most).
_EMBED_BATCH_SIZE = 96
_EMBED_BATCH_DELAY_S = 8


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
        title = Path(doc.metadata["source"]).stem.replace("_", " ").title()
        chunks_for_doc = header_splitter.split_text(doc.page_content)
        for chunk in chunks_for_doc:
            chunk.metadata["title"] = title
        header_chunks.extend(chunks_for_doc)

    chunks = char_splitter.split_documents(header_chunks)
    logger.info("Split into {} chunks.", len(chunks))

    settings = get_settings()
    qdrant_url = f"http://{settings.qdrant_host}:{settings.qdrant_port}"
    embedder = get_embedder()

    batches = [chunks[i : i + _EMBED_BATCH_SIZE] for i in range(0, len(chunks), _EMBED_BATCH_SIZE)]
    logger.info("Embedding in {} batches of up to {} chunks.", len(batches), _EMBED_BATCH_SIZE)

    vector_store: QdrantVectorStore | None = None
    for idx, batch in enumerate(batches):
        logger.info("Embedding batch {}/{} ({} chunks)...", idx + 1, len(batches), len(batch))
        if vector_store is None:
            vector_store = QdrantVectorStore.from_documents(
                documents=batch,
                embedding=embedder,
                url=qdrant_url,
                collection_name=settings.qdrant_collection,
            )
        else:
            vector_store.add_documents(batch)

        if idx < len(batches) - 1:
            time.sleep(_EMBED_BATCH_DELAY_S)

    logger.info("Ingestion complete. {} chunks indexed.", len(chunks))
    return len(chunks)
