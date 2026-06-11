# Business Requirements Document (BRD)
## AI Customer Support Assistant — RAG-Powered Knowledge Base

**Document Version:** 1.0  
**Status:** Approved for Architecture  
**Date:** June 2026  
**Classification:** Internal — Project Specification

---

## 1. Executive Summary

This document defines the business requirements for an **AI Customer Support Assistant** — a locally-deployed, Retrieval-Augmented Generation (RAG) system that enables accurate, verifiable, domain-specific answers grounded in company documentation. The system operates entirely on a single machine without containerisation, serving as both a production-ready application and a reference implementation of spec-driven AI engineering.

The assistant reduces support ticket volume, accelerates response times, and demonstrates responsible AI deployment practices including source citation, hallucination mitigation, and prompt injection defence.

---

## 2. Business Objectives

| ID | Objective | Metric |
|----|-----------|--------|
| BO-01 | Reduce tier-1 support ticket volume | ≥ 40% reduction within 90 days |
| BO-02 | Deliver accurate, cited answers from company docs | ≥ 90% answer grounding rate |
| BO-03 | Provide cost-effective AI deployment with no cloud dependency | $0 incremental inference cost (local LLM) |
| BO-04 | Enable graceful fallback to cloud LLM when local is unavailable | < 2s fallback latency |
| BO-05 | Serve as a reusable RAG reference architecture for future projects | Documented, templated codebase |

---

## 3. Scope

### 3.1 In Scope

- Single-page HTML chat frontend with Server-Sent Event streaming
- Python FastAPI backend with RAG pipeline
- Local LLM: Gemma 4 2B via llama.cpp (`llama-cpp-python`)
- Cloud LLM fallback: OpenRouter Free API (configurable model)
- LLM routing layer via LiteLLM (local ↔ cloud switching)
- Vector store: ChromaDB (local persistent storage)
- Relational store: SQLite (users, documents, conversation metadata)
- Redis caching for frequent query responses
- Document ingestion pipeline (PDF, TXT, MD)
- Source citation display in chat responses
- Prompt injection defence and input sanitisation
- Single-repo local deployment (no Docker)

### 3.2 Out of Scope

- Multi-tenant SaaS deployment
- Mobile application
- Fine-tuning of LLM models
- Active Directory / SSO integration
- Automated document crawling from external systems
- Voice interface
- Analytics dashboard

---

## 4. Stakeholders

| Role | Name / Group | Responsibility |
|------|-------------|----------------|
| Project Sponsor | Engineering Lead | Final approval, budget |
| Product Owner | Technical PM | Requirements prioritisation |
| Development Team | Full-Stack + AI Engineers | Implementation |
| End Users | Support agents, internal staff | Functional validation |
| Security Reviewer | Security Architect | Threat model sign-off |

---

## 5. User Personas

### Persona A — Support Agent (Primary)
- Needs instant, accurate answers from product docs without digging through wikis
- Non-technical; expects a chat interface similar to consumer AI tools
- Requires source citations to verify and share with customers

### Persona B — Knowledge Manager
- Uploads and maintains the document corpus
- Needs visibility into which documents are indexed and when
- Monitors answer quality and flags hallucinations

### Persona C — Developer / Admin
- Manages local deployment, LLM switching, Redis and ChromaDB
- Needs clear configuration and health endpoints

---

## 6. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Users can type questions in a chat UI | Must Have |
| FR-02 | Backend retrieves relevant chunks from ChromaDB | Must Have |
| FR-03 | Augmented prompt is sent to configured LLM | Must Have |
| FR-04 | Response streams token-by-token via SSE to the frontend | Must Have |
| FR-05 | Each response includes source document name and chunk reference | Must Have |
| FR-06 | System checks Redis cache before invoking LLM | Must Have |
| FR-07 | LiteLLM routes between local Gemma and OpenRouter based on config | Must Have |
| FR-08 | Admin can upload documents (PDF, TXT, MD) via API endpoint | Must Have |
| FR-09 | Documents are chunked, embedded, and stored in ChromaDB | Must Have |
| FR-10 | SQLite stores user sessions, document metadata, conversation history | Must Have |
| FR-11 | Off-topic or unanswerable queries return graceful "I don't know" | Must Have |
| FR-12 | Health check endpoint exposes status of all dependencies | Should Have |
| FR-13 | Conversation history maintained within session | Should Have |
| FR-14 | Input is sanitised to prevent prompt injection | Must Have |

---

## 7. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-01 | Performance | First token latency ≤ 3s on local LLM (hardware-dependent) |
| NFR-02 | Performance | Redis cache hit response ≤ 200ms |
| NFR-03 | Reliability | System recovers from LLM timeout within 5s with error message |
| NFR-04 | Security | No LLM API keys stored in code; loaded from `.env` |
| NFR-05 | Security | Input sanitised before insertion into prompt |
| NFR-06 | Availability | Single-node; no HA requirement for local deployment |
| NFR-07 | Maintainability | All configuration externalised to `.env` file |
| NFR-08 | Observability | Structured JSON logs for all RAG pipeline steps |
| NFR-09 | Portability | Runs on Linux/macOS/Windows with Python 3.11+ |
| NFR-10 | Data Privacy | No user data sent to cloud unless OpenRouter fallback explicitly enabled |

---

## 8. Assumptions

- Local hardware has ≥ 8 GB RAM and supports llama.cpp model inference
- Python 3.11+ and Redis are pre-installed on the host machine
- Company documents are available in PDF, TXT, or Markdown format
- OpenRouter API key is optional and only used when local LLM is unavailable
- The system serves a single team (< 20 concurrent users)

---

## 9. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-01 | Local LLM latency too high for acceptable UX | Medium | High | Stream tokens; set timeout; fallback to OpenRouter |
| R-02 | Hallucinations when context is insufficient | Medium | High | Strict system prompt; "I don't know" guardrail |
| R-03 | Prompt injection via uploaded documents | Low | High | Input sanitisation; chunk-level content moderation |
| R-04 | Redis unavailability causes cache misses | Low | Low | Graceful degradation; pass-through to LLM |
| R-05 | ChromaDB corruption on disk | Low | Medium | Periodic backup of chroma_db directory |

---

## 10. Dependencies

- `llama-cpp-python` — local LLM inference
- `chromadb` — vector store
- `litellm` — LLM routing
- `fastapi` + `uvicorn` — backend framework
- `redis` — caching
- `sqlite3` (stdlib) — relational store
- `sentence-transformers` or OpenAI embedding API — embeddings
- OpenRouter API account (optional, for cloud fallback)

---

## 11. Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AC-01 | User can ask a question and receive a streamed, cited answer within 5s |
| AC-02 | Uploading a PDF causes it to appear in ChromaDB and answer subsequent queries |
| AC-03 | Second identical query is served from Redis cache |
| AC-04 | Switching `LLM_PROVIDER=openrouter` in `.env` routes queries to OpenRouter |
| AC-05 | Prompt injection attempt returns sanitised output, not leaked system prompt |
| AC-06 | `/health` endpoint returns green status for all components |

---

## 12. Success Metrics

| Metric | Target |
|--------|--------|
| Answer grounding rate (response cites source) | ≥ 90% |
| Cache hit rate after warm-up period | ≥ 30% |
| User satisfaction (informal survey) | ≥ 4/5 |
| Time to first response (streaming) | ≤ 3s |
| Setup time for new deployment | ≤ 30 minutes |

---

## 13. Roadmap

| Phase | Milestone | Duration |
|-------|-----------|----------|
| 1 | Core RAG pipeline (ingest + query + stream) | Week 1–2 |
| 2 | Frontend chat UI + SSE integration | Week 2 |
| 3 | Redis caching + LiteLLM routing | Week 3 |
| 4 | Security hardening + prompt injection defence | Week 3 |
| 5 | Health checks, logging, docs | Week 4 |
| 6 | UAT + tuning | Week 4–5 |
