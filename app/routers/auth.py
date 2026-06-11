from fastapi import APIRouter, HTTPException, status

from app.schemas.api_schemas import LoginRequest, LoginResponse
from app.services.auth_service import create_session, find_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    """Create a Redis-backed session for an existing user."""
    user = await find_user_by_username(payload.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    token = await create_session(user)
    return LoginResponse(
        session_token=token,
        user_id=user.id,
        display_name=user.display_name,
        role=user.role,
    )
