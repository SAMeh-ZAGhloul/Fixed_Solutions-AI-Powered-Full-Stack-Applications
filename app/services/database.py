import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiosqlite

from app.config import Settings, get_settings


def sqlite_path_from_url(database_url: str) -> Path:
    """Extract a local SQLite path from an async SQLAlchemy URL."""
    prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("Only local sqlite+aiosqlite URLs are supported")
    return Path(database_url.removeprefix(prefix))


@asynccontextmanager
async def get_db(settings: Settings | None = None) -> AsyncIterator[aiosqlite.Connection]:
    """Yield an async SQLite connection with row dictionaries enabled."""
    active_settings = settings or get_settings()
    db_path = sqlite_path_from_url(active_settings.database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = await aiosqlite.connect(db_path)
    connection.row_factory = aiosqlite.Row
    await connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        await connection.close()


async def fetch_one(query: str, params: tuple[Any, ...] = ()) -> aiosqlite.Row | None:
    """Execute a parameterised query and return one row."""
    async with get_db() as db:
        cursor = await db.execute(query, params)
        return await cursor.fetchone()


async def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[aiosqlite.Row]:
    """Execute a parameterised query and return all rows."""
    async with get_db() as db:
        cursor = await db.execute(query, params)
        return list(await cursor.fetchall())


def sqlite_healthcheck(settings: Settings | None = None) -> bool:
    """Check whether SQLite is reachable."""
    active_settings = settings or get_settings()
    db_path = sqlite_path_from_url(active_settings.database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute("SELECT 1")
    return True
