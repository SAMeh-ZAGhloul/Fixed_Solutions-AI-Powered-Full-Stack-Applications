import uuid

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.routers.dependencies import get_current_user, require_admin
from app.schemas.api_schemas import (
    CurrentUser,
    DocumentItem,
    DocumentListResponse,
    DocumentUploadResponse,
)
from app.services.database import fetch_all, get_db
from app.services.chroma_client import get_chroma_client
from app.services.ingest_service import (
    chunk_text,
    parse_document,
    write_to_chroma,
    write_to_sqlite,
)

router = APIRouter(prefix="/documents", tags=["documents"])
logger = structlog.get_logger()


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
    """Upload and ingest a document into ChromaDB and SQLite."""
    settings = get_settings()
    
    # Validate file type
    filename = file.filename or "unknown"
    suffix = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    if suffix not in {"pdf", "txt", "md"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: pdf, txt, md",
        )
    
    # Read and validate file size
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_bytes / 1024 / 1024:.0f}MB limit",
        )
    
    # Save file temporarily
    document_id = str(uuid.uuid4())
    temp_path = settings.upload_dir / f"{document_id}.{suffix}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path.write_bytes(file_bytes)
    
    try:
        # Create document record in SQLite
        import time
        now = int(time.time())
        
        async with get_db(settings) as db:
            await db.execute(
                """
                INSERT INTO documents
                (id, filename, original_name, file_type, file_size_bytes, status, uploaded_by, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    str(temp_path),
                    filename,
                    suffix,
                    len(file_bytes),
                    "pending",
                    admin_user.id,
                    now,
                ),
            )
            await db.commit()
        
        # Parse document
        raw_text, page_map = parse_document(temp_path)
        
        # Chunk text
        chunks = chunk_text(raw_text, chunk_size=500, overlap=50)
        
        if not chunks:
            raise ValueError("Document produced no chunks")
        
        # Write to ChromaDB and SQLite
        await write_to_chroma(document_id, filename, chunks, settings)
        await write_to_sqlite(document_id, filename, chunks, admin_user.id, settings)
        
        logger.info(
            "document.uploaded",
            document_id=document_id,
            filename=filename,
            chunk_count=len(chunks),
            user_id=admin_user.id,
        )
        
        # Clean up temp file
        temp_path.unlink()
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            status="indexed",
            chunk_count=len(chunks),
        )
    
    except Exception as e:
        logger.error(
            "document.upload_failed",
            document_id=document_id,
            filename=filename,
            error=str(e),
        )
        # Mark as failed in database
        try:
            async with get_db(settings) as db:
                await db.execute(
                    "UPDATE documents SET status = ? WHERE id = ?",
                    ("failed", document_id),
                )
                await db.commit()
        except Exception:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    admin_user: CurrentUser = Depends(require_admin),
) -> dict[str, object]:
    """Delete a document and associated vectors."""
    settings = get_settings()
    
    try:
        # Delete from ChromaDB
        client = get_chroma_client(settings.chroma_path)
        try:
            client.delete_collection(name=f"doc_{document_id}")
        except Exception:
            pass  # Collection may not exist
        
        # Delete from SQLite
        async with get_db(settings) as db:
            # Delete chunks
            await db.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
            # Delete document
            await db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            await db.commit()
        
        logger.info("document.deleted", document_id=document_id, user_id=admin_user.id)
        
        return {"status": "deleted", "document_id": document_id}
    
    except Exception as e:
        logger.error("document.delete_failed", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )

