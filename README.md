# AI Customer Support Assistant

Local FastAPI RAG assistant scaffolded from the project artifacts.

## Setup

```bash
make setup
```

Edit `.env`, then start the app:

```bash
make run
```

Open `http://localhost:8000`. The seed users are `agent` and `admin`.

## Current Implementation

Phase 1 foundation is implemented: configuration, Alembic schema, FastAPI app factory, structured logging, auth/login, protected route scaffolding, health checks, and a minimal frontend. RAG ingestion, Chroma writes, LiteLLM routing, Redis query cache integration, and upload persistence are the next phases.

## Configuration

All runtime settings are loaded from `.env` via `pydantic-settings`. Copy `.env.example` to `.env` and set at least `SECRET_KEY` before production-like use.

Use `LLM_PROVIDER=local` for the local llama.cpp route or `LLM_PROVIDER=openrouter` with `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` once the LLM service phase is implemented.

## Commands

```bash
make migrate
make lint
make test
make backup
```
