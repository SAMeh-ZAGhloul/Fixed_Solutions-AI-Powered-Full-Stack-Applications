from collections.abc import AsyncIterator
from typing import Any

import httpx
import structlog
from litellm import acompletion

from app.config import get_settings

logger = structlog.get_logger()

# How long to wait for the local LLM to respond before falling back.
_LOCAL_TIMEOUT_S = 5

# Maximum time for the entire LLM call (local or remote).
_LLM_TIMEOUT_S = 60


async def _try_local_llm(prompt: str) -> Any:
    """Attempt to stream completion from the local llama.cpp endpoint.

    Returns an async iterator if the connection succeeds, or ``None``
    if the local endpoint is unreachable (so the caller can fall back).
    """
    settings = get_settings()

    # Quick connectivity check – avoids httpx defaults (~30 s timeout).
    try:
        async with httpx.AsyncClient(timeout=_LOCAL_TIMEOUT_S) as client:
            resp = await client.get(f"{settings.local_llm_base_url}/health")
            resp.raise_for_status()
    except Exception as exc:
        logger.warning("llm.local_unreachable", reason=str(exc))
        return None

    logger.info("llm.stream_start", provider="local")

    response = await acompletion(
        model="openai/local-model",
        base_url=settings.local_llm_base_url,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_tokens=1024,
        temperature=0.7,
        timeout=_LLM_TIMEOUT_S,
    )

    return response


async def _try_openrouter(prompt: str) -> Any:
    """Stream completion from OpenRouter."""
    settings = get_settings()
    if not settings.openrouter_api_key:
        logger.warning("llm.openrouter_not_configured")
        return None

    logger.info("llm.stream_start", provider="openrouter")

    response = await acompletion(
        model=f"openrouter/{settings.openrouter_model}",
        api_key=settings.openrouter_api_key,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_tokens=1024,
        temperature=0.7,
        timeout=_LLM_TIMEOUT_S,
    )
    return response


async def _stream_response(
    response: Any,
    provider: str,
) -> AsyncIterator[str]:
    """Stream tokens from a LiteLLM response object."""
    token_count = 0
    try:
        async for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
                    token_count += 1
    finally:
        logger.info("llm.stream_end", provider=provider, token_count=token_count)


async def stream_completion(prompt: str) -> AsyncIterator[str]:
    """Stream tokens from the configured LLM provider.

    When ``llm_provider`` is ``"local"``, a quick health-check
    (5 s timeout) is made first.  If the local server is unreachable,
    the request falls back to OpenRouter.

    Yields:
        Individual tokens from the LLM response.
    """
    settings = get_settings()

    if settings.llm_provider == "local":
        response = await _try_local_llm(prompt)
        if response is not None:
            async for token in _stream_response(response, "local"):
                yield token
            return

        # Local LLM unreachable – fall through to OpenRouter below.

    # OpenRouter attempt
    response = await _try_openrouter(prompt)
    if response is not None:
        async for token in _stream_response(response, "openrouter"):
            yield token
        return

    # Neither provider worked
    yield "Error: No LLM provider available. Configure OPENROUTER_API_KEY or start the local LLM."
