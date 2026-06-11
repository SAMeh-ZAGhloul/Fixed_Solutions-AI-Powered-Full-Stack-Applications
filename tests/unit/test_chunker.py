import pytest

from app.services.ingest_service import Chunk, chunk_text


def test_chunk_respects_size() -> None:
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(len(chunk.text.split()) <= 500 for chunk in chunks)


def test_chunk_overlap() -> None:
    text = "A B C D E F G H I J"
    chunks = chunk_text(text, chunk_size=3, overlap=1)
    assert chunks[0].text.split()[-1] == chunks[1].text.split()[0]


def test_chunk_rejects_bad_overlap() -> None:
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("hello world", chunk_size=10, overlap=10)
