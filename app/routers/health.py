import time
from typing import cast

import chromadb
import redis.asyncio as redis
from fastapi import APIRouter

from app.config import get_settings
from app.schemas.api_schemas import HealthComponent, HealthResponse
from app.services.database import sqlite_healthcheck

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return component health for local dependencies."""
    settings = get_settings()
    components: dict[str, HealthComponent] = {}

    try:
        sqlite_healthcheck(settings)
        components["sqlite"] = HealthComponent(status="ok")
    except Exception:
        components["sqlite"] = HealthComponent(status="unavailable")

    try:
        client = chromadb.PersistentClient(path=str(settings.chroma_path))
        collections = client.list_collections()
        vector_count = 0
        for collection in collections:
            vector_count += collection.count()
        components["chromadb"] = HealthComponent(
            status="ok",
            collection_count=len(collections),
            vector_count=vector_count,
        )
    except Exception:
        components["chromadb"] = HealthComponent(status="unavailable")

    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    start = time.perf_counter()
    try:
        await cast("redis.Redis", redis_client).ping()
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        components["redis"] = HealthComponent(status="ok", ping_ms=elapsed_ms)
    except redis.ConnectionError:
        components["redis"] = HealthComponent(status="unavailable")
    finally:
        await redis_client.aclose()

    components["llm_local"] = HealthComponent(status="degraded")
    components["llm_cloud"] = HealthComponent(
        status="configured" if settings.openrouter_api_key else "not_configured"
    )
    status = (
        "ok"
        if all(c.status in {"ok", "configured", "not_configured", "degraded"} for c in components.values())
        else "degraded"
    )
    return HealthResponse(status=status, components=components, version=settings.app_version)
