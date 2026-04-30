# RAGaire

FastAPI + LangChain + Qdrant RAG pipeline for learning Irish — built as a portfolio project demonstrating applied AI development with a full backend, vector search, and a conversational chat interface.

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

`POST /ingest`
Loads Irish language documents from `/data/irish_docs/`, chunks them with LangChain's `RecursiveCharacterTextSplitter`, embeds them, and upserts into the `irish_knowledge` Qdrant collection.

`POST /query`
Accepts a question, retrieves the top-k relevant chunks from Qdrant, passes them as context to the LLM, and returns a grounded answer with source citations.

`GET /health`
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
│   │   ├── test_config.py
│   │   ├── test_qdrant_client.py
│   │   ├── test_embedder.py
│   │   ├── test_ingestion.py
│   │   ├── test_pipeline.py
│   │   └── test_routes.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── icon.svg
│   │   ├── layout.tsx               # Root layout (fonts, metadata)
│   │   └── page.tsx
│   ├── components/
│   │   └── ChatWindow.tsx           # Chat UI (messages, sources, input)
│   ├── next.config.mjs
│   ├── tailwind.config.ts
│   └── .env.local.example
├── docker-compose.yml
├── AGENTS.md
└── README.md
```

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- API keys for [Anthropic](https://console.anthropic.com/) and [Cohere](https://dashboard.cohere.com/)

### 1. Configure environment variables

Copy the example env file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```
ANTHROPIC_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
```

### 2. Start the backend services

```bash
docker compose up
```

This starts:
- **Qdrant** vector store on `localhost:6333`
- **FastAPI backend** on `localhost:8000`

> Add `--build` the first time, or after changes to `Dockerfile` or `requirements.txt`.

### 3. Start the frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

The chat interface is available at `localhost:3000`. By default it connects to the backend at `localhost:8000` — override this in `.env.local` if needed.

### 4. Running tests

All tests are fully mocked — no live services required. Run from inside the backend container:

```bash
docker compose exec backend pytest tests/ -v
```

Or locally from the `backend/` directory (with dependencies installed):

```bash
cd backend && pytest tests/ -v
```

---

## Development Approach

This project was built with Cursor as an AI-assisted coding environment. Rather than treating AI output as a black box, every significant generation is logged in `PROMPT_LOG.md` — recording what was prompted, what was produced, what was changed, and what was learned in the process.

The goal is to document genuine human–AI collaboration honestly: the AI handles boilerplate and scaffolding; decisions about architecture, knowledge base curation, and design decisions belong to the developer.

---

*Tosaíonn gach máistir teanga mar ragaire ar strae.* (Every master of a language begins as a wanderer astray.)