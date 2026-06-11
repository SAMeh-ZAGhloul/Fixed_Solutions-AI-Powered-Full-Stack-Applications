import hashlib
import json
from typing import Any

import redis.asyncio as redis
import structlog

from app.config import Settings, get_settings

logger = structlog.get_logger()


def cache_key(query: str) -> str:
    """Build a non-PII Redis cache key for a sanitized query."""
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return f"cache:query:{digest}"


async def get(query: str, settings: Settings | None = None) -> dict[str, Any] | None:
    """Return a cached RAG response if Redis is available and the key exists."""
    active_settings = settings or get_settings()
    client = redis.from_url(active_settings.redis_url, decode_responses=True)
    try:
        value = await client.get(cache_key(query))
    except redis.ConnectionError as exc:
        logger.warning("cache.unavailable", error=str(exc))
        return None
    finally:
        await client.aclose()
    return json.loads(value) if value else None


async def set(query: str, response: dict[str, Any], ttl: int | None = None) -> None:
    """Cache a RAG response, degrading cleanly when Redis is unavailable."""
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.setex(cache_key(query), ttl or settings.query_cache_ttl_seconds, json.dumps(response))
    except redis.ConnectionError as exc:
        logger.warning("cache.unavailable", error=str(exc))
    finally:
        await client.aclose()
