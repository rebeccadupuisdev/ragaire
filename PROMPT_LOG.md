# Prompt Log — RAGaire

A record of AI-assisted development decisions, prompts used, and what was learned.
This log exists to document the human–AI collaboration process honestly.

---

## How to Use This Log

After significant code generation, the agent will automatically append a prefilled entry below.
Complete the last two fields — **Modifications I made** and **What I learned** — once you've
reviewed the output. You don't need to log every small prompt, the agent will judge what
counts as significant.

Entry template:

```markdown
## Entry [number] — YYYY-MM-DD
**Section:** <!-- inferred from context -->
**Persona:** <!-- persona name if active — omitted if none -->
**Prompt:** <!-- the developer's request -->
**What was generated:** <!-- one or two sentence description -->
**Modifications I made:** <!-- your input needed -->
**What I learned:** <!-- your input needed (optional) -->
```

---

## Entries

---

### Entry 008 — 2026-04-29

**Section:** Tests (Full Suite)

**Persona:** test.generate

**Prompt:** Based on the audit, can you improve the tests?

**What was generated:** Added `ge=1` constraint to `QueryRequest.top_k` in `routes.py`; added `autouse` `lru_cache` clear fixtures to `test_embedder.py` and `test_config.py`; added 4 new ingestion tests (loader invoked, splitter receives loaded docs, path ends with `data/irish_docs`, `from_documents` called even with empty chunks); added 6 new pipeline tests (embedder forwarded to vector store, system prompt content, question in `HumanMessage`, empty question edge cases); added 5 new route tests (error propagation for `/ingest` and `/query`, `top_k=0` and negative value 422s, robust question-forwarding assertion); created `test_qdrant_client.py` (17 tests covering `_is_not_found` branches, `get_client` singleton and host/port wiring, `ensure_collection` happy path, 404 creation, name/vector config, fallback `ValueError`, non-404 and generic re-raises); created `test_config.py` (8 tests for defaults isolated from `.env`, env overrides, and `get_settings` caching). Suite grew from 44 to 81 tests, all passing.

---

### Entry 007 — 2026-04-29

**Section:** Tests (Full Suite)

**Persona:** test.audit

**Prompt:** Can you check the tests?

**What was generated:** Audit report across all four existing test files (`test_embedder.py`, `test_ingestion.py`, `test_pipeline.py`, `test_routes.py`) plus the two completely untested modules (`qdrant_client.py`, `config.py`). Identified `lru_cache` state leakage between tests, missing assertions for splitter input, embedder wiring, system prompt content and `HumanMessage` type, no error-path tests for `/ingest` or `/query`, no `top_k` boundary validation, and zero coverage of `ensure_collection`, `_is_not_found`, `get_client`, and `Settings`.

---

### Entry 006 — 2026-04-29

**Section:** API Layer (Phase 4)

**Persona:** code.tutor.stepwise

**Prompt:** Based on the plan, create the code for phase 4

**What was generated:** `backend/app/main.py` — FastAPI app with Loguru stdlib intercept, CORS middleware (allow all origins), `load_dotenv()` before router import, and `include_router`. `backend/app/api/routes.py` — `QueryRequest`, `QueryResponse`, `IngestResponse`, `HealthResponse` Pydantic models and three async route handlers: `POST /ingest` calling `run_ingestion()`, `POST /query` calling `run_query()`, `GET /health` pinging Qdrant via `get_client()`. `backend/tests/test_routes.py` — 11 `TestClient` tests across three classes covering status codes, response schemas, argument forwarding, default and custom `top_k`, 422 on missing body, and Qdrant unavailable fallback.

---

### Entry 005 — 2026-04-29

**Section:** RAG Pipeline — Tests

**Persona:** test.audit → test.generate

**Prompt:** Based on the audit, can you improve the tests?

**What was generated:** Rewrote `test_ingestion.py` and `test_pipeline.py` with a shared `deps` fixture to eliminate repetitive patching, added tests for `loader_cls`, URL construction, embedder forwarding, default `top_k`, `SystemMessage` presence, Anthropic model name, empty-retrieval, and error paths; created `test_embedder.py` (3 tests covering return type, model name, and caching); updated `conftest.py` to clear the `get_embedder` lru_cache. Suite grew from 11 to 30 RAG-specific tests, all 44 passing.

---

### Entry 004 — 2026-04-29

**Section:** RAG Pipeline — Tests

**Persona:** test.audit

**Prompt:** Can you check the tests?

**What was generated:** Audit report identifying gaps in `test_ingestion.py` and `test_pipeline.py`: missing `loader_cls` assertion, no URL or embedding kwarg checks, no default `top_k` test, no `SystemMessage` or model-name assertions, no empty-retrieval or error-path tests, brittle `call_args` unpacking, and zero coverage of `embedder.py`.

---

### Entry 003 — 2026-04-29

**Section:** RAG Pipeline (Phase 3)

**Persona:** code.tutor.stepwise

**Prompt:** Based on the plan, create the code for phase 3

**What was generated:** `backend/data/irish_docs/sample_grammar.txt` — placeholder knowledge base stub. `backend/app/rag/embedder.py` — `get_embedder()` lru_cache singleton returning `CohereEmbeddings`. `backend/app/rag/ingestion.py` — `run_ingestion()` loading `.txt` files via `DirectoryLoader`, splitting with `RecursiveCharacterTextSplitter(chunk_size=500, overlap=50)`, and upserting into Qdrant via `QdrantVectorStore.from_documents`. `backend/app/rag/pipeline.py` — `run_query()` retrieving top-k chunks and generating an answer via `ChatAnthropic`, returning `{answer, sources}`. `backend/tests/test_ingestion.py` — 5 tests covering chunk count, loader config, splitter config, and Qdrant upsert. `backend/tests/test_pipeline.py` — 6 tests covering answer/sources keys, LLM response mapping, top-k retrieval, and context passing; required fix to use `autouse` mock for `get_embedder` rather than clearing the lru_cache.

---

### Entry 002 — 2026-04-29

**Section:** Vector Store (Phase 2)

**Persona:** code.tutor.stepwise

**Prompt:** Based on the plan, create the code for phase 2

**What was generated:** `backend/app/vector_store/qdrant_client.py` — `get_client()` singleton (lru_cache) and `ensure_collection()` with idempotent 404-aware collection creation. `backend/tests/test_qdrant_client.py` — 5 tests covering absent collection, existing collection, non-404 error re-raise, and get_client singleton behaviour; expanded to 14 by developer. `backend/pytest.ini` added so `from app.`* imports resolve inside the container.

**Modifications I made:** I used the test.audit persona to check the tests were correct and complete. I then used the test.generate persona to generate the tests based on the audit.

---

### Entry 001 — 2026-04-29

**Section:** Infra & Config (Phase 1)

**Persona:** learn.tutor

**Prompt:** Based on the plan, create phase 1 and explain major steps

**What was generated:** Scaffolded the full Phase 1 infrastructure: `backend/requirements.txt`, `.env.example`, `docker-compose.yml`, `backend/Dockerfile`, `backend/app/config.py` (pydantic-settings `BaseSettings` with `get_settings()` singleton), and `backend/tests/test_config.py` with three unit tests covering defaults, env overrides, and singleton caching. All package versions are pinned.