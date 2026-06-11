from collections.abc import AsyncIterator

from app.config import get_settings


async def stream_completion(prompt: str) -> AsyncIterator[str]:
    """Stream tokens from the configured LLM provider.

    Phase 1 keeps this as a deterministic local fallback so the HTTP layer can
    be exercised before LiteLLM wiring lands in the RAG phase.
    """
    _ = prompt
    settings = get_settings()
    yield (
        "I don't have enough information to answer that."
        if settings.llm_provider in {"local", "openrouter"}
        else "LLM provider is not configured."
    )
