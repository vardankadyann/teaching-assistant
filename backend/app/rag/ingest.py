from pathlib import Path
from typing import Dict

from pypdf import PdfReader

from app.config import settings
from app.rag.chunking import chunk_text
from app.rag.store import get_store

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    raise ValueError(f"Unsupported file type: {suffix}")


def ingest_file(path: Path) -> int:
    text = extract_text(path)
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    store = get_store()
    return store.add_documents(chunks, source=path.name)


def ingest_directory(directory: Path) -> Dict[str, int]:
    results: Dict[str, int] = {}
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            results[path.name] = ingest_file(path)
    return results
