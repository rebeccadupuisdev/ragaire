from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel, Field

from app.rag.ingestion import run_ingestion
from app.rag.pipeline import run_query
from app.vector_store.qdrant_client import get_client

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Request body for POST /query."""

    question: str
    top_k: int = Field(default=4, ge=1)


class QueryResponse(BaseModel):
    """Response body for POST /query."""

    answer: str
    sources: list[str]


class IngestResponse(BaseModel):
    """Response body for POST /ingest."""

    status: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    vector_store: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/ingest", response_model=IngestResponse)
async def ingest() -> IngestResponse:
    """Trigger ingestion of all documents in the irish_docs directory."""
    logger.info("Ingest request received.")
    chunks = run_ingestion()
    return IngestResponse(status="ok", chunks_indexed=chunks)


@router.post("/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    """Run a RAG query and return an answer with source citations."""
    logger.info("Query request received: {!r}", body.question)
    result = run_query(body.question, top_k=body.top_k)
    return QueryResponse(answer=result["answer"], sources=result["sources"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Check service health and Qdrant connectivity."""
    try:
        get_client().get_collections()
        vector_store_status = "connected"
    except Exception:
        logger.warning("Qdrant health check failed.")
        vector_store_status = "unavailable"
    return HealthResponse(status="healthy", vector_store=vector_store_status)
