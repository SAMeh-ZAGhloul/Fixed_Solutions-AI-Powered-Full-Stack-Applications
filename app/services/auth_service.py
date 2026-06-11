import secrets
import time

import structlog

from app.config import Settings, get_settings
from app.schemas.api_schemas import CurrentUser
from app.services.database import fetch_one, get_db

logger = structlog.get_logger()
_SESSIONS: dict[str, tuple[str, int]] = {}


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
    """Create a process-local session token."""
    active_settings = settings or get_settings()
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + active_settings.session_ttl_seconds
    _SESSIONS[token] = (user.id, expires_at)
    async with get_db(active_settings) as db:
        await db.execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (int(time.time()), user.id))
        await db.commit()
    logger.info("auth.login", user_id=user.id)
    return token


async def get_user_for_token(token: str, settings: Settings | None = None) -> CurrentUser | None:
    """Resolve a session token to a current user."""
    _ = settings or get_settings()
    session = _SESSIONS.get(token)
    if session is None:
        return None
    user_id, expires_at = session
    if expires_at <= int(time.time()):
        _SESSIONS.pop(token, None)
        return None
    return await find_user_by_id(user_id)
