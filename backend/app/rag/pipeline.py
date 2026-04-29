from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_qdrant import QdrantVectorStore
from loguru import logger

from app.config import get_settings
from app.rag.embedder import get_embedder

# ---------------------------------------------------------------------------
# DEVELOPER-OWNED: Edit the system prompt below to shape the assistant persona.
# See AGENTS.md — "Developer Ownership" section.
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are a helpful Irish language tutor. Answer the user's question using ONLY
the context provided. Respond in English and include Irish examples with
translations where relevant. Explain the translations word for word where relevant.
If the context does not contain enough information
to answer, say so honestly rather than guessing.
"""
# ---------------------------------------------------------------------------


def run_query(question: str, top_k: int = 4) -> dict:
    """Retrieve relevant chunks from Qdrant and generate an answer via Claude.

    Returns a dict with keys:
        answer  — the LLM's response string
        sources — list of raw chunk page_content strings used as context
    """
    settings = get_settings()

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=get_embedder(),
        url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
        collection_name=settings.qdrant_collection,
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    retrieved_docs = retriever.invoke(question)
    logger.info("Retrieved {} chunks for query.", len(retrieved_docs))

    sources = [doc.page_content for doc in retrieved_docs]
    context = "\n\n---\n\n".join(sources)

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
    ]

    response = llm.invoke(messages)
    answer = response.content

    logger.info("Query answered successfully.")
    return {"answer": answer, "sources": sources}
