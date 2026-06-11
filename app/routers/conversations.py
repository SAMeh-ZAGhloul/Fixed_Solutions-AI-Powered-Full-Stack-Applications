from fastapi import APIRouter, Depends

from app.routers.dependencies import get_current_user
from app.schemas.api_schemas import CurrentUser

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    """Return conversation list placeholder for the authenticated user."""
    _ = (limit, offset, current_user)
    return {"conversations": [], "total": 0}


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    """Return message history placeholder for the authenticated user."""
    _ = (conversation_id, current_user)
    return {"messages": []}
