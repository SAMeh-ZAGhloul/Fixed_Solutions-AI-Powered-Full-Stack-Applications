import hashlib
import time
from copy import deepcopy
from typing import Any

from app.config import get_settings

_CACHE: dict[str, tuple[dict[str, Any], int]] = {}


def cache_key(query: str) -> str:
    """Build a non-PII cache key for a sanitized query."""
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return f"cache:query:{digest}"


async def get(query: str) -> dict[str, Any] | None:
    """Return a cached RAG response from the process-local cache."""
    value = _CACHE.get(cache_key(query))
    if value is None:
        return None
    response, expires_at = value
    if expires_at <= int(time.time()):
        _CACHE.pop(cache_key(query), None)
        return None
    return deepcopy(response)


async def set(query: str, response: dict[str, Any], ttl: int | None = None) -> None:
    """Cache a RAG response in memory for the current process lifetime."""
    settings = get_settings()
    expires_at = int(time.time()) + (ttl or settings.query_cache_ttl_seconds)
    _CACHE[cache_key(query)] = (deepcopy(response), expires_at)
