# RAGaire

FastAPI + LangChain + Qdrant RAG pipeline for learning Irish — built as a portfolio project demonstrating applied AI development with a full backend, vector search, and a conversational chat interface.

## Current Status

> **Phase 1 complete — infrastructure & config**

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Infra & config (Docker, env, Pydantic settings, tests) | ✅ Done |
| 2 | Vector store & ingestion pipeline | 🔜 Next |
| 3 | RAG query chain & LLM integration | ⬜ Planned |
| 4 | API routes (`/ingest`, `/query`, `/health`) | ⬜ Planned |
| 5 | Frontend chat interface | ⬜ Planned |

---

## The Concept

**RAGaire** (*ragaire* = Late-night rambler in Irish) is an Irish language learning assistant powered by retrieval-augmented generation. Ask it anything about Irish grammar, vocabulary, phrases, or culture — and it will answer using a curated knowledge base, citing exactly which source chunks informed the response.

## Tech Stack

- **Backend:** FastAPI + Pydantic v2
- **AI / RAG:** LangChain, Anthropic Claude API
- **Embeddings:** Cohere `embed-v3` (multilingual)
- **Vector DB:** Qdrant (local via Docker)
- **Frontend:** Next.js 14 (App Router) + Tailwind CSS
- **Infra:** Docker + Docker Compose
- **Testing:** pytest + Loguru

## The Three Endpoints

`**POST /ingest`**
Loads Irish language documents from `/data/irish_docs/`, chunks them with LangChain's `RecursiveCharacterTextSplitter`, embeds them, and upserts into the `irish_knowledge` Qdrant collection.

`**POST /query`**
Accepts a question, retrieves the top-k relevant chunks from Qdrant, passes them as context to the LLM, and returns a grounded answer with source citations.

`**GET /health**`
Returns API and vector store status.

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
│   │   └── test_config.py
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

## Development Approach

This project was built with Cursor as an AI-assisted coding environment. Rather than treating AI output as a black box, every significant generation is logged in `PROMPT_LOG.md` — recording what was prompted, what was produced, what was changed, and what was learned in the process.

The goal is to document genuine human–AI collaboration honestly: the AI handles boilerplate and scaffolding; decisions about architecture, knowledge base curation, and design decisions belong to the developer.

---

*Tosaíonn gach máistir teanga mar ragaire ar strae.* (Every master of a language begins as a wanderer astray.)