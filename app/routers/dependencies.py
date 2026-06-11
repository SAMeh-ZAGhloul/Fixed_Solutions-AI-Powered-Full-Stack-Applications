from fastapi import Depends, Header, HTTPException, status

from app.schemas.api_schemas import CurrentUser
from app.services.auth_service import get_user_for_token


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    """Resolve the bearer token and return the authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    token = authorization.removeprefix("Bearer ").strip()
    user = await get_user_for_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require an authenticated admin user."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
