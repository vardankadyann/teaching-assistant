import uuid
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embeddings import embed_texts

COLLECTION_NAME = "course_materials"


class ChromaStore:
    def __init__(self) -> None:
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(settings.chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def is_empty(self) -> bool:
        return self._collection.count() == 0

    def add_documents(
        self,
        texts: List[str],
        source: str,
        metadatas: Optional[List[dict]] = None,
    ) -> int:
        if not texts:
            return 0

        ids = [str(uuid.uuid4()) for _ in texts]
        embeddings = embed_texts(texts)
        meta = metadatas or [{"source": source} for _ in texts]
        for m in meta:
            m.setdefault("source", source)

        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=meta,
        )
        return len(texts)

    def query(self, question: str, top_k: Optional[int] = None) -> List[dict]:
        k = top_k or settings.top_k
        if self._collection.count() == 0:
            return []

        query_embedding = embed_texts([question])[0]
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        dists = results["distances"][0] if results["distances"] else []

        chunks = []
        for doc, meta, dist in zip(docs, metas, dists):
            similarity = 1 - dist if dist is not None else None
            chunks.append(
                {
                    "text": doc,
                    "source": meta.get("source", "unknown"),
                    "score": round(similarity, 4) if similarity is not None else None,
                }
            )
        return chunks

    def stats(self) -> Tuple[int, int]:
        count = self._collection.count()
        if count == 0:
            return 0, 0

        all_meta = self._collection.get(include=["metadatas"])
        sources = {m.get("source", "") for m in (all_meta.get("metadatas") or [])}
        return len(sources), count

    def clear(self) -> None:
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
