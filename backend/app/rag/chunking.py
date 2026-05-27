from typing import List


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            break_at = chunk.rfind(". ")
            if break_at > chunk_size // 2:
                chunk = chunk[: break_at + 1]
                end = start + len(chunk)

        chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return [c for c in chunks if c]
