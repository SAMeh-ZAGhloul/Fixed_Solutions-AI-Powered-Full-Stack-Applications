from dataclasses import dataclass


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
