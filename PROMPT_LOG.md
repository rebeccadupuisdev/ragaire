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