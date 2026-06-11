# System Architecture
## AI Customer Support Assistant

**Version:** 1.0 | **Date:** June 2026

---

## 1. Architecture Overview

The system follows a **Modular Monolith** pattern — all components run in a single Python process on one machine, structured into clearly separated modules. This avoids Docker while maintaining clean architectural boundaries.

**Key principles:**
- RAG pipeline as first-class citizen (not a plugin)
- LLM routing abstracted behind LiteLLM interface
- All persistence layers injectable/swappable
- Security-by-design at every layer boundary

---

## 2. Context Diagram

```mermaid
C4Context
    title AI Customer Support Assistant — System Context

    Person(agent, "Support Agent", "Asks questions via Chat UI")
    Person(admin, "Knowledge Manager", "Uploads documents via API")

    System(rag_app, "AI Customer Support Assistant", "RAG-powered chat; returns cited answers from company documents")

    System_Ext(openrouter, "OpenRouter API", "Cloud LLM fallback (optional)")
    System_Ext(local_llm, "llama.cpp / Gemma 4 2B", "Local inference engine")

    Rel(agent, rag_app, "Sends questions, receives streamed answers", "HTTPS/SSE")
    Rel(admin, rag_app, "Uploads documents", "HTTPS/REST")
    Rel(rag_app, openrouter, "Fallback LLM call", "HTTPS")
    Rel(rag_app, local_llm, "Primary LLM call", "Local IPC / HTTP")
```

---

## 3. Container Diagram

```mermaid
C4Container
    title Container Diagram

    Person(user, "User")

    Container(frontend, "Chat Frontend", "Single-page HTML/JS", "Renders chat UI; streams SSE tokens")
    Container(backend, "FastAPI Backend", "Python 3.11 / FastAPI", "RAG pipeline, routing, auth, caching")
    ContainerDb(sqlite, "SQLite", "SQLite3", "Users, document metadata, conversations")
    ContainerDb(chroma, "ChromaDB", "Chroma (local disk)", "Vector embeddings + similarity search")
    ContainerDb(redis, "Redis", "Redis 7+", "Query response cache")
    Container(llm_router, "LiteLLM Router", "LiteLLM library", "Routes to local or cloud LLM")
    Container(local_llm, "Gemma 4 2B", "llama-cpp-python", "Local inference")
    System_Ext(openrouter, "OpenRouter API", "Cloud fallback")

    Rel(user, frontend, "HTTP GET / WebSocket", "Browser")
    Rel(frontend, backend, "REST + SSE", "localhost:8000")
    Rel(backend, sqlite, "Read/Write", "SQLite driver")
    Rel(backend, chroma, "Embed + Query", "ChromaDB client")
    Rel(backend, redis, "Cache get/set", "Redis client")
    Rel(backend, llm_router, "Generate(prompt)", "LiteLLM API")
    Rel(llm_router, local_llm, "Primary path", "llama-cpp HTTP")
    Rel(llm_router, openrouter, "Fallback path", "HTTPS")
```

---

## 4. Component Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend (index.html)"]
        UI[Chat UI]
        SSE[SSE Event Handler]
        CitationRenderer[Citation Renderer]
    end

    subgraph Backend["Backend (FastAPI)"]
        Router[API Router]
        subgraph RAGPipeline["RAG Pipeline"]
            QueryHandler[Query Handler]
            InputSanitizer[Input Sanitizer]
            EmbeddingService[Embedding Service]
            VectorSearch[Vector Search]
            PromptBuilder[Prompt Builder]
            StreamController[Stream Controller]
        end
        subgraph IngestionPipeline["Ingestion Pipeline"]
            DocParser[Document Parser]
            Chunker[Text Chunker]
            EmbedWriter[Embed + Write]
        end
        CacheService[Cache Service]
        LLMService[LLM Service / LiteLLM]
        HealthController[Health Controller]
    end

    subgraph Storage["Storage Layer"]
        SQLiteDB[(SQLite)]
        ChromaDB[(ChromaDB)]
        RedisCache[(Redis)]
    end

    subgraph LLMLayer["LLM Layer"]
        LocalLLM[Gemma 4 2B / llama.cpp]
        CloudLLM[OpenRouter API]
    end

    UI --> Router
    SSE --> StreamController
    Router --> QueryHandler
    Router --> DocParser
    QueryHandler --> InputSanitizer
    InputSanitizer --> CacheService
    CacheService --> RedisCache
    CacheService --> EmbeddingService
    EmbeddingService --> VectorSearch
    VectorSearch --> ChromaDB
    VectorSearch --> PromptBuilder
    PromptBuilder --> LLMService
    LLMService --> LocalLLM
    LLMService --> CloudLLM
    LLMService --> StreamController
    StreamController --> SSE
    DocParser --> Chunker
    Chunker --> EmbedWriter
    EmbedWriter --> ChromaDB
    EmbedWriter --> SQLiteDB
    CitationRenderer --> UI
```

---

## 5. Data Flow Diagram — Query Path

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant FE as Frontend
    participant API as FastAPI
    participant SAN as Input Sanitizer
    participant CACHE as Redis Cache
    participant EMBED as Embedding Service
    participant CHROMA as ChromaDB
    participant PB as Prompt Builder
    participant LITELLM as LiteLLM Router
    participant LLM as Local/Cloud LLM

    U->>FE: Types question
    FE->>API: POST /chat {query, session_id}
    API->>SAN: sanitize(query)
    SAN-->>API: clean_query
    API->>CACHE: get(hash(clean_query))
    alt Cache Hit
        CACHE-->>API: cached_response
        API-->>FE: SSE stream (cached)
    else Cache Miss
        API->>EMBED: embed(clean_query)
        EMBED-->>API: query_vector
        API->>CHROMA: similarity_search(query_vector, top_k=3)
        CHROMA-->>API: [chunk_1, chunk_2, chunk_3] + metadata
        API->>PB: build_prompt(query, chunks)
        PB-->>API: augmented_prompt
        API->>LITELLM: generate(augmented_prompt, stream=True)
        LITELLM->>LLM: forward request
        loop Token stream
            LLM-->>LITELLM: token
            LITELLM-->>API: token
            API-->>FE: SSE data: token
            FE-->>U: Render token
        end
        API->>CACHE: set(hash(query), full_response, ttl=3600)
    end
    API-->>FE: SSE: citations [source_name, page]
    FE-->>U: Render citations
```

---

## 6. Data Flow Diagram — Ingestion Path

```mermaid
sequenceDiagram
    participant ADM as Admin
    participant API as FastAPI /upload
    participant PARSER as Document Parser
    participant CHUNKER as Text Chunker
    participant EMBED as Embedding Service
    participant CHROMA as ChromaDB
    participant SQLITE as SQLite

    ADM->>API: POST /upload (multipart file)
    API->>PARSER: parse(file) → raw_text
    PARSER-->>API: text + page_map
    API->>CHUNKER: chunk(text, size=500, overlap=50)
    CHUNKER-->>API: [chunk_1..chunk_n]
    loop Each chunk
        API->>EMBED: embed(chunk_i)
        EMBED-->>API: vector_i
        API->>CHROMA: upsert(id, vector_i, metadata)
    end
    API->>SQLITE: INSERT document_metadata (name, path, chunk_count, uploaded_at)
    API-->>ADM: {status: "ingested", chunks: n}
```

---

## 7. Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Single Host Machine                          │
│                                                                  │
│  ┌──────────────┐   ┌──────────────────────────────────────┐   │
│  │  Browser     │   │  Python Process (uvicorn, port 8000) │   │
│  │  localhost   │──▶│  FastAPI Application                 │   │
│  │  :8000       │   │  ├── routers/                        │   │
│  └──────────────┘   │  ├── services/                       │   │
│                      │  │    ├── rag_service.py             │   │
│                      │  │    ├── llm_service.py (LiteLLM)  │   │
│                      │  │    ├── cache_service.py           │   │
│                      │  │    └── ingest_service.py         │   │
│                      │  └── models/                        │   │
│                      └──────────────────────────────────────┘   │
│                               │                                  │
│          ┌────────────────────┼────────────────────┐            │
│          ▼                    ▼                    ▼            │
│  ┌──────────────┐  ┌───────────────────┐  ┌──────────────┐    │
│  │  SQLite      │  │  ChromaDB         │  │  Redis       │    │
│  │  app.db      │  │  ./chroma_db/     │  │  localhost   │    │
│  │  (file)      │  │  (local disk)     │  │  :6379       │    │
│  └──────────────┘  └───────────────────┘  └──────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │  llama.cpp server (port 8080)        │                       │
│  │  Model: gemma-4-2b-instruct.gguf    │                       │
│  └──────────────────────────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
              │ (Optional, when LLM_PROVIDER=openrouter)
              ▼
      ┌───────────────┐
      │  OpenRouter   │
      │  API (Cloud)  │
      └───────────────┘
```

---

## 8. Security Architecture

```mermaid
graph LR
    subgraph TrustBoundary["Trust Boundary: Localhost"]
        FE[Frontend]
        API[FastAPI]
        subgraph SecureZone["Secure Zone"]
            ENV[.env secrets]
            SQLITE[(SQLite)]
            CHROMA[(ChromaDB)]
            REDIS[(Redis)]
        end
    end

    subgraph ExternalZone["External (Optional)"]
        OR[OpenRouter API]
    end

    FE -->|"Input sanitised before processing"| API
    API -->|"Reads secrets at startup only"| ENV
    ENV -.->|"OPENROUTER_API_KEY"| OR
    API -->|"Parameterised queries only"| SQLITE
    API -->|"No raw user input stored as-is"| CHROMA
```

**Security controls summary:**
- API keys in `.env`, never in code or logs
- All user inputs pass through `InputSanitizer` before prompt construction
- SQLite queries use parameterised statements
- Redis keys are hashed (SHA-256) — no PII in cache keys
- CORS restricted to `localhost` origin
- Rate limiting via FastAPI middleware (60 req/min default)

---

## 9. High Availability Design

Single-node deployment — no HA requirement. Resilience is handled by:
- **Redis failure:** Cache service catches `ConnectionError` and falls through to LLM
- **LLM failure:** LiteLLM catches timeout; switches provider if fallback configured
- **ChromaDB failure:** Returns HTTP 503 with descriptive error
- **SQLite failure:** Returns HTTP 503; no data loss (read-only during query)

---

## 10. Scalability Design

The current architecture targets < 20 concurrent users. Scaling path if needed:

| Step | Change |
|------|--------|
| 1 | Add `uvicorn --workers N` for CPU parallelism |
| 2 | Replace SQLite with PostgreSQL |
| 3 | Replace local Chroma with Weaviate or Pinecone |
| 4 | Deploy behind Nginx reverse proxy |
| 5 | Containerise with Docker Compose |
