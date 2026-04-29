# AGENTS.md — RAGaire

Project-specific context for the **RAGaire** Irish language RAG assistant.
This file defines the stack, structure, data rules, and ownership boundaries for AI-assisted development in Cursor.

---

## Project Overview

A RAG (Retrieval-Augmented Generation) pipeline that answers questions about the Irish language, grounded in a curated knowledge base. Users interact via a chat interface; responses include cited source chunks.

### The Core Pipeline

1. **Ingestion** — load, chunk, embed, and upsert Irish language documents into Qdrant
2. **Retrieval** — embed a user query, retrieve top-k relevant chunks from Qdrant
3. **Generation** — pass retrieved context + question to an LLM, return a grounded answer with sources

---

## Stack

This project uses the following stack. Do not suggest alternatives to any of these.


| Layer             | Choice                                 |
| ----------------- | -------------------------------------- |
| Backend           | FastAPI + Pydantic v2                  |
| RAG Orchestration | LangChain                              |
| LLM               | Anthropic Claude API                   |
| Embeddings        | Cohere `embed-v3` (multilingual)       |
| Vector DB         | Qdrant (local via Docker)              |
| Frontend          | Next.js 14 (App Router) + Tailwind CSS |
| Infra             | Docker + Docker Compose                |
| Testing           | pytest                                 |
| Logging           | Loguru                                 |


---

## Project Structure

```
ragaire/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── api/
│   │   │   └── routes.py            # /query, /ingest, /health
│   │   ├── rag/
│   │   │   ├── pipeline.py          # RAG chain (retriever + LLM)
│   │   │   ├── embedder.py          # Embedding logic
│   │   │   └── ingestion.py         # Document loading & chunking
│   │   ├── vector_store/
│   │   │   └── qdrant_client.py     # Qdrant wrapper
│   │   └── config.py                # Settings via pydantic BaseSettings
│   ├── data/
│   │   └── irish_docs/              # Curated .txt knowledge files
│   ├── tests/
│   │   └── test_pipeline.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   └── components/
│       └── ChatWindow.tsx
├── docker-compose.yml
├── AGENTS.md
└── README.md
```

---

## API Contract

### `POST /query`

```json
// Request
{ "question": "string", "top_k": 4 }

// Response
{ "answer": "string", "sources": ["chunk1...", "chunk2..."] }
```

### `POST /ingest`

```json
// Response
{ "status": "ok", "chunks_indexed": 142 }
```

### `GET /health`

```json
// Response
{ "status": "healthy", "vector_store": "connected" }
```

---

## Data Rules

- `/data/irish_docs/` contains curated `.txt` files — the knowledge base
- All chunking and embedding logic lives in `rag/ingestion.py`
- Chunking config: `chunk_size=500`, `overlap=50` via `RecursiveCharacterTextSplitter`
- Qdrant collection name: `irish_knowledge`
- Do not re-read or re-embed documents per request — ingestion is a one-time setup step via `/ingest`

---

## Language & Content

- Code, comments, and variable names are in **English**
- The LLM system prompt instructs the assistant to respond in English with Irish examples and translations

---

## Developer Ownership

The following are fixed and should not be changed without explicit instruction:

- **Knowledge base content** — what goes into `/data/irish_docs/` is the developer's responsibility
- **LLM system prompt** — the tone and framing of the assistant persona belongs to the developer
- **Architecture decisions** — if something is not specified in this file, ask before implementing

---

## Coding Standards

- Type hints everywhere in Python
- Pydantic models for all request/response schemas
- No hardcoded secrets — use `.env` + `python-dotenv` (`ANTHROPIC_API_KEY`, `COHERE_API_KEY`)
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`
- Ask before introducing any dependency not already in `requirements.txt`

