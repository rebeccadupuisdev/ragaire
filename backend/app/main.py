import logging
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

load_dotenv()

from app.api.routes import router  # noqa: E402 — import after load_dotenv

# ---------------------------------------------------------------------------
# Loguru — intercept stdlib logging so uvicorn/FastAPI logs flow through it
# ---------------------------------------------------------------------------
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=0, force=True)

class _InterceptHandler(logging.Handler):
    """Route stdlib log records into Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore[assignment]
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.root.handlers = [_InterceptHandler()]
logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="RAGaire", version="0.1.0", description="Irish language RAG assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
