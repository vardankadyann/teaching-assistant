import uuid
from typing import List, Optional, Tuple

from app.config import settings
from app.rag import upstash_http
from app.rag.embeddings import embed_texts

COLLECTION_NAME = "course_materials"


class UpstashStore:
    def __init__(self) -> None:
        if not settings.upstash_vector_rest_url or not settings.upstash_vector_rest_token:
            raise RuntimeError(
                "Upstash not configured. Set UPSTASH_VECTOR_REST_URL and "
                "UPSTASH_VECTOR_REST_TOKEN from console.upstash.com (same index)."
            )
        if "-vector.upstash.io" not in settings.upstash_vector_rest_url:
            raise RuntimeError("Invalid UPSTASH_VECTOR_REST_URL (must end with -vector.upstash.io)")

    def is_empty(self) -> bool:
        return self.stats()[1] == 0

    def add_documents(
        self,
        texts: List[str],
        source: str,
        metadatas: Optional[List[dict]] = None,
    ) -> int:
        if not texts:
            return 0

        embeddings = embed_texts(texts)
        vectors = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            meta = dict(metadatas[i]) if metadatas else {}
            meta.setdefault("source", source)
            meta["text"] = text
            vectors.append(
                {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "metadata": meta,
                    "data": text,
                }
            )

        upstash_http.upsert_vectors(vectors, settings.upstash_namespace)
        return len(texts)

    def query(self, question: str, top_k: Optional[int] = None) -> List[dict]:
        k = top_k or settings.top_k
        _, total = self.stats()
        if total == 0:
            return []

        query_embedding = embed_texts([question])[0]
        results = upstash_http.query_vectors(
            query_embedding,
            min(k, total),
            settings.upstash_namespace,
        )

        chunks = []
        for item in results:
            meta = item.get("metadata") or {}
            score = item.get("score")
            chunks.append(
                {
                    "text": meta.get("text") or item.get("data") or "",
                    "source": meta.get("source", "unknown"),
                    "score": round(score, 4) if score is not None else None,
                }
            )
        return chunks

    def stats(self) -> Tuple[int, int]:
        return upstash_http.index_info()

    def clear(self) -> None:
        upstash_http.delete_namespace(settings.upstash_namespace)
