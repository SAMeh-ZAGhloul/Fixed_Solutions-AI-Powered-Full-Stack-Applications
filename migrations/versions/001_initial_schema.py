"""Initial SQLite schema.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-06-11
"""
from collections.abc import Sequence

from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id           TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            username     TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            role         TEXT NOT NULL DEFAULT 'agent' CHECK(role IN ('agent', 'admin')),
            created_at   INTEGER NOT NULL DEFAULT (unixepoch()),
            last_seen_at INTEGER
        )
        """
    )
    op.execute(
        """
        CREATE TABLE documents (
            id               TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            filename         TEXT NOT NULL,
            original_name    TEXT NOT NULL,
            file_type        TEXT NOT NULL CHECK(file_type IN ('pdf', 'txt', 'md')),
            file_size_bytes  INTEGER NOT NULL,
            chunk_count      INTEGER DEFAULT 0,
            status           TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','indexed','failed')),
            uploaded_by      TEXT NOT NULL REFERENCES users(id),
            uploaded_at      INTEGER NOT NULL DEFAULT (unixepoch()),
            indexed_at       INTEGER
        )
        """
    )
    op.execute(
        """
        CREATE TABLE conversations (
            id         TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            user_id    TEXT NOT NULL REFERENCES users(id),
            title      TEXT,
            created_at INTEGER NOT NULL DEFAULT (unixepoch()),
            updated_at INTEGER NOT NULL DEFAULT (unixepoch())
        )
        """
    )
    op.execute(
        """
        CREATE TABLE messages (
            id              TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            conversation_id TEXT NOT NULL REFERENCES conversations(id),
            role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content         TEXT NOT NULL,
            citations       TEXT DEFAULT '[]',
            llm_provider    TEXT,
            latency_ms      REAL,
            cache_hit       INTEGER DEFAULT 0 CHECK(cache_hit IN (0,1)),
            created_at      INTEGER NOT NULL DEFAULT (unixepoch())
        )
        """
    )
    op.execute(
        """
        CREATE TABLE document_chunks (
            id           TEXT PRIMARY KEY,
            document_id  TEXT NOT NULL REFERENCES documents(id),
            chunk_index  INTEGER NOT NULL,
            chunk_text   TEXT NOT NULL,
            token_count  INTEGER,
            page_number  INTEGER,
            created_at   INTEGER NOT NULL DEFAULT (unixepoch())
        )
        """
    )
    op.create_index("idx_conversations_user_id", "conversations", ["user_id"])
    op.create_index("idx_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("idx_messages_created_at", "messages", ["created_at"])
    op.create_index("idx_documents_status", "documents", ["status"])
    op.create_index("idx_document_chunks_document_id", "document_chunks", ["document_id"])
    op.execute(
        """
        INSERT INTO users (username, display_name, role)
        VALUES ('admin', 'Admin User', 'admin'), ('agent', 'Support Agent', 'agent')
        """
    )


def downgrade() -> None:
    op.drop_index("idx_document_chunks_document_id", table_name="document_chunks")
    op.drop_index("idx_documents_status", table_name="documents")
    op.drop_index("idx_messages_created_at", table_name="messages")
    op.drop_index("idx_messages_conversation_id", table_name="messages")
    op.drop_index("idx_conversations_user_id", table_name="conversations")
    op.drop_table("document_chunks")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("documents")
    op.drop_table("users")
