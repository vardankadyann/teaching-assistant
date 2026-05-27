import os
from typing import Optional, Union

from app.config import settings

COLLECTION_NAME = "course_materials"

_store: Optional[Union["ChromaStore", "UpstashStore"]] = None


def _use_upstash() -> bool:
    if settings.vector_backend == "upstash":
        return True
    if settings.vector_backend == "chroma":
        return False
    # Auto: Upstash on Vercel when credentials exist
    if os.environ.get("VERCEL"):
        return bool(
            settings.upstash_vector_rest_url and settings.upstash_vector_rest_token
        )
    return False


def get_store():
    global _store
    if _store is not None:
        return _store

    if _use_upstash():
        from app.rag.upstash_store import UpstashStore

        _store = UpstashStore()
    else:
        from app.rag.chroma_store import ChromaStore

        _store = ChromaStore()
    return _store
