import json
import time
import uuid
from collections.abc import AsyncIterator

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.routers.dependencies import get_current_user
from app.schemas.api_schemas import ChatRequest, CurrentUser
from app.services.llm_service import stream_completion
from app.services.rag_service import build_prompt
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
    """Stream a placeholder assistant response through the secured chat endpoint."""
    clean_query = sanitize(payload.query)
    prompt = build_prompt(clean_query, [])
    started_at = time.perf_counter()

    async def event_stream() -> AsyncIterator[str]:
        full_response = []
        async for token in stream_completion(prompt):
            full_response.append(token)
            yield sse_event("token", {"token": token})
        yield sse_event("citations", {"citations": []})
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        message_id = uuid.uuid4().hex
        logger.info(
            "chat.query",
            user_id=current_user.id,
            cache_hit=False,
            provider="local",
            latency_ms=latency_ms,
        )
        yield sse_event(
            "done",
            {
                "message_id": message_id,
                "latency_ms": latency_ms,
                "cache_hit": False,
                "provider": "local",
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
