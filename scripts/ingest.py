import argparse
import asyncio
import uuid
from pathlib import Path

import structlog

from app.config import Settings
from app.services.database import get_db
from app.services.ingest_service import (
    chunk_text,
    parse_document,
    write_to_chroma,
    write_to_sqlite,
)

logger = structlog.get_logger()


async def ingest_file(file_path: Path, settings: Settings) -> None:
    """Ingest a single document file."""
    try:
        logger.info("ingest.start", file_path=str(file_path))
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Create document record
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
                    str(file_path),
                    file_path.name,
                    file_path.suffix.lower().lstrip("."),
                    file_path.stat().st_size,
                    "pending",
                    "cli",  # Mark as CLI-ingested
                    now,
                ),
            )
            await db.commit()
        
        # Parse document
        raw_text, page_map = parse_document(file_path)
        
        # Chunk text
        chunks = chunk_text(raw_text, chunk_size=500, overlap=50)
        
        if not chunks:
            logger.warning("ingest.no_chunks", file_path=str(file_path))
            return
        
        # Write to ChromaDB and SQLite
        await write_to_chroma(document_id, file_path.name, chunks, settings)
        await write_to_sqlite(document_id, file_path.name, chunks, "cli", settings)
        
        logger.info(
            "ingest.success",
            file_path=str(file_path),
            document_id=document_id,
            chunk_count=len(chunks),
        )
    
    except Exception as e:
        logger.error("ingest.failed", file_path=str(file_path), error=str(e))
        raise


async def main() -> None:
    """Batch ingest documents from a directory."""
    parser = argparse.ArgumentParser(description="Batch ingest documents into ChromaDB + SQLite.")
    parser.add_argument("--dir", default="data/uploads/", help="Directory containing documents")
    args = parser.parse_args()
    
    upload_dir = Path(args.dir)
    files = [
        path for path in upload_dir.glob("*")
        if path.suffix.lower() in {".pdf", ".txt", ".md"} and path.is_file()
    ]
    
    if not files:
        print(f"No ingestable files found in {upload_dir}")
        return
    
    print(f"Found {len(files)} ingestable files. Starting batch ingestion...")
    
    settings = Settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    
    for i, file_path in enumerate(files, 1):
        try:
            await ingest_file(file_path, settings)
            print(f"[{i}/{len(files)}] ✓ {file_path.name}")
        except Exception as e:
            print(f"[{i}/{len(files)}] ✗ {file_path.name}: {e}")
    
    print("Batch ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())

