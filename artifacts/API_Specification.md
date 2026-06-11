# API Specification
## AI Customer Support Assistant

**Version:** 1.0 | **Base URL:** `http://localhost:8000/api/v1`  
**Auth:** Bearer token (session token) | **Format:** JSON + SSE

---

## 1. Authentication

All endpoints except `/health` and `/auth/login` require:
```
Authorization: Bearer {session_token}
```
Session tokens are generated at login and stored in Redis (`session:{token}`).

---

## 2. Endpoints

---

### POST `/auth/login`

Create a session.

**Request:**
```json
{
  "username": "string"
}
```

**Response 200:**
```json
{
  "session_token": "string",
  "user_id": "string",
  "display_name": "string",
  "role": "agent | admin"
}
```

**Response 404:**
```json
{ "detail": "User not found" }
```

---

### POST `/chat`

Submit a query. Returns a **Server-Sent Event** stream.

**Request:**
```json
{
  "query": "string",
  "conversation_id": "string | null",
  "session_id": "string"
}
```

**Validation:**
- `query`: required, 1–2000 characters, stripped of injection patterns
- `session_id`: required, valid active session

**SSE Event Stream:**

Each event is one of:

```
event: token
data: {"token": "Hello"}

event: token
data: {"token": " world"}

event: citations
data: {"citations": [{"source": "policy_v2.pdf", "page": 3, "chunk_id": "doc123_4"}]}

event: done
data: {"message_id": "uuid", "latency_ms": 1240, "cache_hit": false, "provider": "local"}

event: error
data: {"detail": "LLM unavailable. Please try again."}
```

**Response 400:**
```json
{ "detail": "Query must be between 1 and 2000 characters" }
```

**Response 401:**
```json
{ "detail": "Invalid or expired session" }
```

**Response 429:**
```json
{ "detail": "Rate limit exceeded. Try again in 60 seconds." }
```

---

### POST `/documents/upload`

Upload a document for ingestion. **Admin only.**

**Request:** `multipart/form-data`
```
file: <binary>   # PDF, TXT, or MD
```

**Response 200:**
```json
{
  "document_id": "string",
  "original_name": "string",
  "file_type": "pdf",
  "status": "pending",
  "message": "Document queued for ingestion"
}
```

**Response 400:**
```json
{ "detail": "Unsupported file type. Allowed: pdf, txt, md" }
```

**Response 403:**
```json
{ "detail": "Admin role required" }
```

**Response 413:**
```json
{ "detail": "File exceeds 50MB limit" }
```

---

### GET `/documents`

List all indexed documents.

**Response 200:**
```json
{
  "documents": [
    {
      "id": "string",
      "original_name": "string",
      "file_type": "pdf",
      "chunk_count": 42,
      "status": "indexed",
      "uploaded_at": 1719000000,
      "indexed_at": 1719000120
    }
  ],
  "total": 1
}
```

---

### DELETE `/documents/{document_id}`

Remove a document and its vectors. **Admin only.**

**Response 200:**
```json
{ "message": "Document and all vectors deleted", "chunks_removed": 42 }
```

**Response 404:**
```json
{ "detail": "Document not found" }
```

---

### GET `/conversations`

List conversations for the authenticated user.

**Query params:** `?limit=20&offset=0`

**Response 200:**
```json
{
  "conversations": [
    {
      "id": "string",
      "title": "string | null",
      "created_at": 1719000000,
      "message_count": 6
    }
  ],
  "total": 1
}
```

---

### GET `/conversations/{conversation_id}/messages`

Retrieve message history for a conversation.

**Response 200:**
```json
{
  "messages": [
    {
      "id": "string",
      "role": "user | assistant",
      "content": "string",
      "citations": [],
      "created_at": 1719000000,
      "cache_hit": false,
      "provider": "local"
    }
  ]
}
```

---

### GET `/health`

System health check. No authentication required.

**Response 200:**
```json
{
  "status": "ok | degraded",
  "components": {
    "sqlite": { "status": "ok" },
    "chromadb": { "status": "ok", "collection_count": 1, "vector_count": 247 },
    "redis": { "status": "ok", "ping_ms": 0.4 },
    "llm_local": { "status": "ok | degraded | unavailable" },
    "llm_cloud": { "status": "configured | not_configured" }
  },
  "version": "1.0.0"
}
```

---

## 3. Error Codes Reference

| HTTP Code | Meaning |
|-----------|---------|
| 400 | Bad request / validation error |
| 401 | Missing or invalid session |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 413 | File too large |
| 422 | Unprocessable entity (Pydantic validation) |
| 429 | Rate limit exceeded |
| 503 | Dependency unavailable (LLM, ChromaDB) |

---

## 4. OpenAPI Schema Excerpt

```yaml
openapi: "3.1.0"
info:
  title: AI Customer Support Assistant API
  version: "1.0.0"
paths:
  /api/v1/chat:
    post:
      summary: Submit query (SSE stream)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [query, session_id]
              properties:
                query:
                  type: string
                  minLength: 1
                  maxLength: 2000
                conversation_id:
                  type: string
                  nullable: true
                session_id:
                  type: string
      responses:
        "200":
          description: SSE stream of tokens and citations
          content:
            text/event-stream:
              schema:
                type: string
        "401":
          $ref: '#/components/responses/Unauthorized'
        "429":
          $ref: '#/components/responses/RateLimited'
```
