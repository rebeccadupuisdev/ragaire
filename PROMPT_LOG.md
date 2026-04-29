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

**Prompt:** Based on the plan, create the code for step 3

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