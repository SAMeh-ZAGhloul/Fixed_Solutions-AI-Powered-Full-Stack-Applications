import secrets
import time

import redis.asyncio as redis
import structlog

from app.config import Settings, get_settings
from app.schemas.api_schemas import CurrentUser
from app.services.database import fetch_one, get_db

logger = structlog.get_logger()


async def get_redis_client(settings: Settings | None = None) -> redis.Redis:
    """Create an async Redis client."""
    active_settings = settings or get_settings()
    return redis.from_url(active_settings.redis_url, decode_responses=True)


async def find_user_by_username(username: str) -> CurrentUser | None:
    """Find a user by username."""
    row = await fetch_one(
        "SELECT id, username, display_name, role FROM users WHERE username = ?",
        (username,),
    )
    if row is None:
        return None
    return CurrentUser(**dict(row))


async def find_user_by_id(user_id: str) -> CurrentUser | None:
    """Find a user by id."""
    row = await fetch_one(
        "SELECT id, username, display_name, role FROM users WHERE id = ?",
        (user_id,),
    )
    if row is None:
        return None
    return CurrentUser(**dict(row))


async def create_session(user: CurrentUser, settings: Settings | None = None) -> str:
    """Create a Redis-backed session token."""
    active_settings = settings or get_settings()
    token = secrets.token_urlsafe(32)
    client = await get_redis_client(active_settings)
    await client.setex(f"session:{token}", active_settings.session_ttl_seconds, user.id)
    await client.aclose()
    async with get_db(active_settings) as db:
        await db.execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (int(time.time()), user.id))
        await db.commit()
    logger.info("auth.login", user_id=user.id)
    return token


async def get_user_for_token(token: str, settings: Settings | None = None) -> CurrentUser | None:
    """Resolve a session token to a current user."""
    active_settings = settings or get_settings()
    client = await get_redis_client(active_settings)
    user_id = await client.get(f"session:{token}")
    await client.aclose()
    if not user_id:
        return None
    return await find_user_by_id(user_id)
