import json
import time
import uuid
from collections.abc import AsyncIterator

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.routers.dependencies import get_current_user
from app.schemas.api_schemas import ChatRequest, CurrentUser
from app.services.cache_service import get as cache_get
from app.services.cache_service import set as cache_set
from app.services.llm_service import stream_completion
from app.services.rag_service import build_prompt, search
from app.services.sanitizer import sanitize

router = APIRouter(prefix="/chat", tags=["chat"])
logger = structlog.get_logger()


def sse_event(event: str, data: dict[str, object]) -> str:
    """Format one Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("")
async def chat(
    payload: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> StreamingResponse:
    """Stream a RAG-powered assistant response with citations."""
    clean_query = sanitize(payload.query)
    started_at = time.perf_counter()
    
    # Check cache first
    cached_response = await cache_get(clean_query)
    if cached_response:
        logger.info(
            "chat.cache_hit",
            user_id=current_user.id,
            query_length=len(clean_query),
        )
        
        async def cached_stream() -> AsyncIterator[str]:
            # Yield cached tokens
            for token in cached_response.get("tokens", []):
                yield sse_event("token", {"token": token})
            
            # Yield citations
            citations = [
                {
                    "source_name": cit.get("source_name"),
                    "page_number": cit.get("page_number"),
                }
                for cit in cached_response.get("citations", [])
            ]
            yield sse_event("citations", {"citations": citations})
            
            message_id = uuid.uuid4().hex
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            yield sse_event(
                "done",
                {
                    "message_id": message_id,
                    "latency_ms": latency_ms,
                    "cache_hit": True,
                    "provider": cached_response.get("provider", "cache"),
                },
            )
        
        return StreamingResponse(cached_stream(), media_type="text/event-stream")
    
    # Search for relevant chunks
    chunks = await search(clean_query, top_k=3)
    prompt = build_prompt(clean_query, chunks)

    async def event_stream() -> AsyncIterator[str]:
        full_response = []
        async for token in stream_completion(prompt):
            full_response.append(token)
            yield sse_event("token", {"token": token})
        
        # Extract citations from chunks
        citations = [
            {
                "source_name": chunk.source_name,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]
        yield sse_event("citations", {"citations": citations})
        
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        message_id = uuid.uuid4().hex
        
        # Cache the response
        full_text = "".join(full_response)
        provider = get_settings().llm_provider
        await cache_set(
            clean_query,
            {
                "tokens": full_response,
                "citations": citations,
                "provider": provider,
                "full_response": full_text,
            },
        )
        
        logger.info(
            "chat.query",
            user_id=current_user.id,
            cache_hit=False,
            provider=provider,
            latency_ms=latency_ms,
            chunk_count=len(chunks),
        )
        
        yield sse_event(
            "done",
            {
                "message_id": message_id,
                "latency_ms": latency_ms,
                "cache_hit": False,
                "provider": provider,
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")

