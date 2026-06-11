from collections.abc import AsyncIterator

import structlog
from litellm import acompletion

from app.config import get_settings

logger = structlog.get_logger()


async def stream_completion(prompt: str) -> AsyncIterator[str]:
    """Stream tokens from the configured LLM provider.
    
    Routes to local LLM first (via llama-cpp-python), then falls back to OpenRouter.
    
    Args:
        prompt: The augmented RAG prompt (with context and question boundaries).
        
    Yields:
        Individual tokens from the LLM response.
    """
    settings = get_settings()
    
    try:
        # Try local LLM first via llama-cpp-python endpoint
        if settings.llm_provider == "local":
            logger.info("llm.stream_start", provider="local")
            
            # LiteLLM format for local llama.cpp server
            response = await acompletion(
                model="openai/local-model",  # LiteLLM proxy format
                base_url=settings.local_llm_base_url,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=1024,
                temperature=0.7,
            )
            
            # Stream tokens from the AsyncIterator response
            token_count = 0
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        token_count += 1
            
            logger.info("llm.stream_end", provider="local", token_count=token_count)
        
        else:
            # OpenRouter fallback (requires API key and model)
            if not settings.openrouter_api_key:
                logger.warning("llm.openrouter_not_configured")
                yield "LLM provider not configured. Please set OPENROUTER_API_KEY."
                return
            
            logger.info("llm.stream_start", provider="openrouter")
            
            response = await acompletion(
                model=f"openrouter/{settings.openrouter_model}",
                api_key=settings.openrouter_api_key,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=1024,
                temperature=0.7,
            )
            
            token_count = 0
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                        token_count += 1
            
            logger.info("llm.stream_end", provider="openrouter", token_count=token_count)
    
    except Exception as e:
        logger.error("llm.stream_failed", error=str(e), provider=settings.llm_provider)
        yield f"Error: {str(e)}"
