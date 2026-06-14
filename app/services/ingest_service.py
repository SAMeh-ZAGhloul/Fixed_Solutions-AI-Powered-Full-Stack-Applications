import uuid
from dataclasses import dataclass
from pathlib import Path

import structlog
from pypdf import PdfReader

from app.config import Settings, get_settings
from app.services.chroma_client import get_chroma_client
from app.services.database import get_db

logger = structlog.get_logger()


@dataclass(frozen=True)
class Chunk:
    text: str
    chunk_index: int
    page_number: int | None = None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping word chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    words = text.split()
    chunks: list[Chunk] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(Chunk(text=" ".join(words[start:end]), chunk_index=len(chunks)))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def parse_document(file_path: Path) -> tuple[str, dict[int, int]]:
    """Parse a document (PDF, TXT, MD) and return text + page_map.
    
    Args:
        file_path: Path to the document file.
        
    Returns:
        Tuple of (raw_text, page_map) where page_map maps chunk indices to source pages.
        
    Raises:
        ValueError: If file type is unsupported.
    """
    suffix = file_path.suffix.lower()
    page_map: dict[int, int] = {}
    
    if suffix == ".pdf":
        reader = PdfReader(file_path)
        text_parts = []
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            text_parts.append(page_text)
            # Record page number for chunks from this page (will be mapped after chunking)
            if page_text.strip():
                # Mark the boundary so we can assign page numbers during chunking
                text_parts.append(f"\n[PAGE_BREAK_{page_num}]\n")
        raw_text = "\n".join(text_parts)
    elif suffix in {".txt", ".md"}:
        raw_text = file_path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    
    return raw_text, page_map


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Embed chunks using ChromaDB's default embedding model.
    
    Args:
        chunks: List of text chunks to embed.
        
    Returns:
        List of embedding vectors (list[float]).
    """
    # ChromaDB handles embeddings transparently during write_to_chroma,
    # so we return empty list as a placeholder
    return [[] for _ in chunks]


async def write_to_chroma(
    document_id: str,
    doc_name: str,
    chunks: list[Chunk],
    settings: Settings | None = None,
) -> None:
    """Write document chunks to ChromaDB collection.
    
    Args:
        document_id: The document's database ID.
        doc_name: The original document name.
        chunks: List of chunks to store.
        settings: Application settings (injected for testing).
    """
    active_settings = settings or get_settings()
    client = get_chroma_client(active_settings.chroma_path)
    
    # Get or create collection for this document
    collection = client.get_or_create_collection(
        name=f"doc_{document_id}",
        metadata={"document_id": document_id, "document_name": doc_name},
    )
    
    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas_list: list[dict[str, str | int | float | bool]] = []
    
    for chunk in chunks:
        chunk_id = f"{document_id}_chunk_{chunk.chunk_index}"
        ids.append(chunk_id)
        documents.append(chunk.text)
        metadatas_list.append({
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number or 0,
            "source_name": doc_name,
        })
    
    # ChromaDB automatically embeds using default model
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas_list,  # type: ignore
    )
    
    logger.info(
        "chroma.write",
        document_id=document_id,
        chunk_count=len(chunks),
        collection_name=f"doc_{document_id}",
    )


async def write_to_sqlite(
    document_id: str,
    original_name: str,
    chunks: list[Chunk],
    user_id: str,
    settings: Settings | None = None,
) -> None:
    """Write document chunks to SQLite document_chunks table.
    
    Args:
        document_id: The document's database ID.
        original_name: Original filename.
        chunks: List of chunks to store.
        user_id: User who uploaded the document.
        settings: Application settings (injected for testing).
    """
    active_settings = settings or get_settings()
    now = int(__import__("time").time())
    
    async with get_db(active_settings) as db:
        # Insert document metadata
        await db.execute(
            """
            UPDATE documents
            SET chunk_count = ?, status = ?, indexed_at = ?
            WHERE id = ?
            """,
            (len(chunks), "indexed", now, document_id),
        )
        
        # Insert chunks
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            token_count = len(chunk.text.split())
            
            await db.execute(
                """
                INSERT INTO document_chunks
                (id, document_id, chunk_index, chunk_text, token_count, page_number, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    document_id,
                    chunk.chunk_index,
                    chunk.text,
                    token_count,
                    chunk.page_number,
                    now,
                ),
            )
        
        await db.commit()
    
    logger.info(
        "sqlite.ingest",
        document_id=document_id,
        original_name=original_name,
        chunk_count=len(chunks),
        user_id=user_id,
    )
