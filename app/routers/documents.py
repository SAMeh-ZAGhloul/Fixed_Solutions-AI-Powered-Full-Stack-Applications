from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.routers.dependencies import get_current_user, require_admin
from app.schemas.api_schemas import (
    CurrentUser,
    DocumentItem,
    DocumentListResponse,
    DocumentUploadResponse,
)
from app.services.database import fetch_all

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents(_: CurrentUser = Depends(get_current_user)) -> DocumentListResponse:
    """List indexed document metadata."""
    rows = await fetch_all(
        """
        SELECT id, original_name, file_type, chunk_count, status, uploaded_at, indexed_at
        FROM documents
        ORDER BY uploaded_at DESC
        """
    )
    documents = [DocumentItem(**dict(row)) for row in rows]
    return DocumentListResponse(documents=documents, total=len(documents))


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    admin_user: CurrentUser = Depends(require_admin),
) -> DocumentUploadResponse:
    """Validate document uploads before Phase 2 ingestion is wired."""
    _ = admin_user
    settings = get_settings()
    suffix = (file.filename or "").rsplit(".", maxsplit=1)[-1].lower()
    if suffix not in {"pdf", "txt", "md"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: pdf, txt, md",
        )
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds 50MB limit",
            )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document ingestion is scheduled for Phase 2",
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    admin_user: CurrentUser = Depends(require_admin),
) -> dict[str, object]:
    """Delete a document and associated vectors once ingestion exists."""
    _ = (document_id, admin_user)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete is scheduled for Phase 2",
    )
