# AI Coding Assistant Implementation Prompt
## AI Customer Support Assistant

**Optimised for:** Cursor · Claude Code · Cline · Roo Code · Windsurf · GitHub Copilot Agent

---

## 1. Project Context

You are implementing the **AI Customer Support Assistant** — a locally-deployed, RAG-powered chat application.

**Tech stack:**
- Python 3.11 + FastAPI + uvicorn
- ChromaDB (vector store, local disk)
- SQLite (relational — users, documents, conversations)
- Redis (query cache)
- LiteLLM (LLM routing)
- Gemma 4 2B via llama-cpp-python (primary LLM)
- OpenRouter API (fallback LLM)
- Single-page HTML frontend (SSE streaming chat UI)
- No Docker

---

## 2. Referenced Documents

Before writing any code, read and internalize all of the following:

```
artifacts/BRD.md                  — Business requirements, scope, acceptance criteria
artifacts/SystemArchitecture.md   — All diagrams, component structure, security architecture
artifacts/DatabaseDesign.md       — Full schema, index strategy, ChromaDB schema, Redis keys
artifacts/API_Specification.md    — All endpoints, request/response schemas, error codes
artifacts/SecurityDesign.md       — STRIDE, input sanitiser code, prompt boundaries, RBAC
artifacts/DevOpsDesign.md         — Repo structure, Makefile, setup script, CI config
artifacts/TestStrategy.md         — Test structure, fixtures, golden dataset pattern
artifacts/ExecutionPlan.md        — Milestones, epics, features, critical path
```

When you are uncertain about a design decision, **check the artifacts first**. Never invent requirements.

---

## 3. Development Rules (Non-Negotiable)

1. **Implement incrementally** — one feature at a time, per the ExecutionPlan milestones
2. **Tests before merging** — each feature must have tests before moving to the next
3. **No hardcoded secrets** — all secrets via `.env` + `pydantic-settings`
4. **No raw SQL strings** — use parameterised queries only
5. **All user input must pass through `sanitizer.py`** before touching any prompt
6. **All API endpoints require auth** except `/health` and `/auth/login`
7. **Structured logs only** — use `structlog`; never log raw queries, tokens, or API keys
8. **Type annotations required** on all function signatures
9. **Do not modify the `.env.example`** without updating `README.md`
10. **Run `make lint` and `make test` before declaring any task complete**

---

## 4. Coding Standards

```python
# Style: ruff (PEP8-compatible)
# Type checking: mypy --strict
# Max function length: 40 lines (split if longer)
# Max file length: 300 lines (split into modules if longer)
# Async: all I/O must be async (FastAPI async endpoints, async DB calls)
# Error handling: always catch specific exceptions; never bare `except:`
# Docstrings: Google-style on all public functions

# Example:
async def search_documents(query: str, top_k: int = 3) -> list[ChunkResult]:
    """Search ChromaDB for semantically similar document chunks.

    Args:
        query: Sanitised user query string.
        top_k: Number of results to return.

    Returns:
        List of ChunkResult objects with text and metadata.

    Raises:
        ChromaDBError: If the collection is unavailable.
    """
    ...
```

---

## 5. Architecture Constraints

- **Module boundaries must match SystemArchitecture.md Component Diagram** exactly
  - `app/routers/` — HTTP layer only; no business logic
  - `app/services/` — all business logic; no HTTP primitives
  - `app/models/` — DB models only
  - `app/schemas/` — Pydantic schemas only
- **LLM calls go only through `llm_service.py`** — no direct LiteLLM calls elsewhere
- **Vector DB calls go only through `rag_service.py`**
- **Cache calls go only through `cache_service.py`**
- **Input sanitisation happens only in `sanitizer.py`** — called in `chat.py` router before any service call

---

## 6. Implementation Phases

### Phase 1 — Foundation (start here)

```
Tasks:
1. Create repo structure exactly as in DevOpsDesign.md §2
2. Create app/config.py (pydantic-settings, all env vars from .env.example)
3. Create migrations/versions/001_initial_schema.py (all tables from DatabaseDesign.md §3)
4. Run `alembic upgrade head` — verify tables created
5. Create app/main.py (FastAPI factory, include routers, CORS, rate limiting)
6. Create scripts/setup.sh
7. Create Makefile with all commands from DevOpsDesign.md §3

Validation gate:
- `make lint` passes
- `alembic upgrade head` creates all tables
- `make run` starts without errors
- GET /api/v1/health returns 200 with all components listed
```

### Phase 2 — Ingestion Pipeline

```
Tasks:
1. Implement app/services/ingest_service.py:
   - parse_document(file) → raw text + page_map
   - chunk_text(text, chunk_size=500, overlap=50) → List[Chunk]
   - embed_chunks(chunks) → List[vector]
   - write_to_chroma(doc_id, chunks, vectors) → None
   - write_to_sqlite(document metadata) → None
2. Implement app/routers/documents.py (POST /upload, GET /, DELETE /{id})
3. Implement scripts/ingest.py CLI

Validation gate:
- Upload a real PDF via POST /upload
- GET /documents shows it with status "indexed"
- ChromaDB collection has correct chunk count
- `pytest tests/unit/test_chunker.py tests/integration/test_upload_endpoint.py` passes
```

### Phase 3 — RAG Query Pipeline

```
Tasks:
1. Implement app/services/rag_service.py:
   - embed_query(query) → vector
   - search(query_vector, top_k) → List[ChunkResult]
   - build_prompt(query, chunks) → str (use exact template from SecurityDesign.md §3.2)
2. Implement app/services/llm_service.py:
   - LiteLLM wrapper
   - Routing logic: local first, OpenRouter fallback
   - Streaming support (yield tokens)
3. Implement app/services/cache_service.py:
   - get(query) → cached_response | None
   - set(query, response, ttl=3600)
4. Implement app/services/sanitizer.py (exact patterns from SecurityDesign.md §3.1)
5. Implement app/routers/chat.py (POST /chat with SSE)

Validation gate:
- Ask a question about an ingested document
- Response streams tokens to browser via SSE
- Response includes `event: citations` with correct source document
- Same query twice → second response has `cache_hit: true`
- `pytest tests/unit/ tests/integration/test_chat_endpoint.py` passes
```

### Phase 4 — Frontend

```
Tasks:
1. Implement frontend/index.html (single file — HTML + CSS + JS)
   - Chat message list (user + assistant bubbles)
   - Input box + send button
   - EventSource SSE handler — renders tokens as they arrive
   - Citation section (expandable below each response)
   - Drag-drop file upload zone (calls POST /documents/upload)
   - Health indicator badge
2. Serve static file from FastAPI: app.mount("/", StaticFiles(...))

Validation gate:
- Open http://localhost:8000 in browser
- Ask question → see streaming response
- Upload a PDF → see it indexed → ask question about it → see citation
```

### Phase 5 — Security & Testing

```
Tasks:
1. Run security test suite: `pytest tests/security/`
2. Fix any failures — harden sanitizer or prompt boundaries
3. Complete unit test coverage to ≥ 80%: `make test`
4. Run integration test suite: `pytest tests/integration/`
5. Write README.md with: setup, run, ingest, config, LLM switching
6. Write runbook: backup, restore, troubleshooting

Validation gate:
- `pytest tests/ --cov=app --cov-report=term-missing` shows ≥ 80%
- All 6 acceptance criteria from BRD.md §11 pass manually
- `make lint` clean
- All INJECTION_PAYLOADS in test_prompt_injection.py handled safely
```

---

## 7. Validation Gates Summary

| Gate | Command | Must Pass Before |
|------|---------|-----------------|
| Lint | `make lint` | Any commit |
| Type check | `mypy app/` | Any commit |
| Unit tests | `make test-unit` | Moving to next phase |
| Integration tests | `make test-integration` | Declaring phase done |
| Security tests | `pytest tests/security/` | Phase 5 |
| Coverage | `pytest --cov=app` ≥ 80% | Final sign-off |
| BRD acceptance criteria | Manual UAT | Final sign-off |

---

## 8. Testing Requirements

- Every new service function needs a unit test in `tests/unit/`
- Every new API endpoint needs an integration test in `tests/integration/`
- Fixtures must use temp databases (not production data)
- Mock the LLM in unit tests; use a real local LLM response only in E2E tests
- Security payloads in `tests/security/test_prompt_injection.py` must all be tested

---

## 9. Deliverables Checklist

```
Core:
[ ] app/ — full Python application matching SystemArchitecture.md
[ ] frontend/index.html — single-page chat UI
[ ] migrations/ — all Alembic migrations
[ ] scripts/ — setup.sh, ingest.py, backup.sh

Config:
[ ] .env.example — all variables documented
[ ] Makefile — all commands working

Tests:
[ ] tests/unit/ — ≥ 80% coverage
[ ] tests/integration/ — all endpoints covered
[ ] tests/security/ — all injection payloads tested

CI:
[ ] .github/workflows/ci.yml — lint + unit tests

Docs:
[ ] README.md — setup, run, config, LLM switching
[ ] Runbook — backup, restore, troubleshooting
[ ] API auto-docs at http://localhost:8000/docs
```

---

## 10. Definition of Done

A task is **done** when ALL of the following are true:

- [ ] Code matches the design in the referenced artifacts
- [ ] Structured logs emitted for all key operations
- [ ] All secrets loaded from `.env` (never hardcoded)
- [ ] Input sanitisation applied at the boundary
- [ ] Auth enforced on all protected endpoints
- [ ] Unit tests written and passing
- [ ] `make lint` passes with zero warnings
- [ ] `mypy app/` passes
- [ ] README updated if public interface changed
- [ ] No TODO comments left in committed code
