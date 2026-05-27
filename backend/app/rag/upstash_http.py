"""Lightweight Upstash Vector HTTP client with short timeouts (avoids SDK hangs)."""
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import settings

_TIMEOUT = httpx.Timeout(20.0, connect=6.0)
_HEADERS = {"Content-Type": "application/json"}


def _post(path: str, payload: Any = None) -> Dict[str, Any]:
    url = settings.upstash_vector_rest_url.rstrip("/") + path
    token = settings.upstash_vector_rest_token
    headers = {**_HEADERS, "Authorization": f"Bearer {token}"}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(url, headers=headers, json=payload if payload is not None else {})
        response.raise_for_status()
        body = response.json()
    if "error" in body:
        raise RuntimeError(body["error"])
    return body.get("result", body)


def ping() -> Dict[str, Any]:
    """Quick connectivity test (5–10s max)."""
    return _post("/info")


def upsert_vectors(vectors: List[dict], namespace: str) -> None:
    _post(
        f"/upsert/{namespace}" if namespace else "/upsert",
        {"vectors": vectors},
    )


def query_vectors(
    vector: List[float],
    top_k: int,
    namespace: str,
) -> List[dict]:
    payload = {
        "vector": vector,
        "topK": top_k,
        "includeMetadata": True,
        "includeVectors": False,
    }
    result = _post(
        f"/query/{namespace}" if namespace else "/query",
        payload,
    )
    if isinstance(result, list):
        return result
    return result.get("matches") or result.get("results") or []


def delete_namespace(namespace: str) -> None:
    _post(f"/delete-namespace/{namespace}")


def index_info() -> Tuple[int, int]:
    info = ping()
    chunk_count = int(info.get("vectorCount") or info.get("vector_count") or 0)
    if chunk_count == 0:
        return 0, 0
    dim = info.get("dimension") or info.get("vectorDimension")
    if dim and int(dim) != 384:
        raise RuntimeError(
            f"Upstash index dimension is {dim}, but fastembed needs 384. "
            "Create a new index with 384 dimensions (Cosine)."
        )
    return 1, chunk_count
