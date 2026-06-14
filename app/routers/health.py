from fastapi import APIRouter

from app.config import get_settings
from app.schemas.api_schemas import HealthComponent, HealthResponse
from app.services.chroma_client import get_chroma_client
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
        client = get_chroma_client(settings.chroma_path)
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

    components["session_store"] = HealthComponent(status="in_memory")
    components["query_cache"] = HealthComponent(status="in_memory")
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
