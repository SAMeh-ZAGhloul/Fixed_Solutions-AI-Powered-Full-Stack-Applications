"""Shared ChromaDB client factory with telemetry disabled and singleton caching.

ChromaDB raises "An instance of Chroma already exists for ... with different
settings" when multiple PersistentClient instances point at the same directory
but were constructed with inconsistent Settings objects.  This module ensures
exactly one PersistentClient per path by caching clients in a module-level
dict, keyed on the resolved absolute path.
"""

from pathlib import Path

import chromadb
from chromadb.api import ClientAPI
from chromadb.config import Settings as ChromaSettings

_clients: dict[str, ClientAPI] = {}


def _make_client(path: str) -> ClientAPI:
    """Create a ChromaDB PersistentClient with all telemetry disabled.

    ChromaDB's bundled posthog telemetry is incompatible with newer
    posthog library versions, causing log spam. This factory suppresses it
    at every level.
    """
    return chromadb.PersistentClient(
        path=path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _resolve_path(path: Path | None) -> Path:
    """Resolve the effective ChromaDB storage path.

    Args:
        path: User-supplied path or None to use the config default.
    """
    if path is not None:
        return path.resolve()
    from app.config import get_settings  # noqa: late import to avoid circular

    return get_settings().chroma_path.resolve()


def get_chroma_client(path: Path | None = None) -> ClientAPI:
    """Return a singleton ChromaDB client for the given path.

    All callers that point at the same directory share one client instance,
    regardless of whether they pass an explicit ``Path`` or rely on the
    config default.

    Args:
        path: Optional custom ChromaDB storage path.  Defaults to config value.
    """
    resolved = _resolve_path(path)
    cache_key = str(resolved)

    if cache_key not in _clients:
        _clients[cache_key] = _make_client(cache_key)

    return _clients[cache_key]
