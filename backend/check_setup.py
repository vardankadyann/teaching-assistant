#!/usr/bin/env python3
"""Quick health check — fast Upstash ping, then embeddings."""
import sys

from app.config import settings
from app.rag.embeddings import _provider, embed_texts


def main() -> int:
    print("=== Teaching Assistant setup check ===\n")
    print(f"Embedding provider: {_provider()} (config: {settings.embedding_provider})")
    print(f"Vector backend:     {settings.vector_backend}")
    print(f"OpenAI key:         {'optional, set' if settings.openai_api_key else 'not set (OK)'}")

    use_upstash = settings.vector_backend == "upstash" or bool(
        settings.upstash_vector_rest_url
    )

    if use_upstash:
        print(f"Upstash URL:        {settings.upstash_vector_rest_url}")
        if not settings.upstash_vector_rest_token:
            print("\nFAIL: UPSTASH_VECTOR_REST_TOKEN missing in backend/.env")
            return 1
        try:
            print("Pinging Upstash (6s timeout)...", flush=True)
            from app.rag import upstash_http

            info = upstash_http.ping()
            count = info.get("vectorCount") or info.get("vector_count") or 0
            dim = info.get("dimension") or info.get("vectorDimension") or "?"
            print(f"Upstash:            OK ({count} vectors, dim={dim})")
            if str(dim) != "384" and dim != "?":
                print("WARN: Index should be 384 dimensions for fastembed.")
        except Exception as exc:
            print(f"\nFAIL: Upstash unreachable — {exc}")
            print(
                "\n  Local workaround — use ChromaDB instead (no cloud needed).\n"
                "  In backend/.env set:\n"
                "    VECTOR_BACKEND=chroma\n"
                "    EMBEDDING_PROVIDER=fastembed\n"
                "  (comment out UPSTASH_* lines)\n"
            )
            return 1
    else:
        try:
            from app.rag.store import get_store

            docs, chunks = get_store().stats()
            print(f"ChromaDB:           OK ({docs} docs, {chunks} chunks)")
        except Exception as exc:
            print(f"\nFAIL: {exc}")
            return 1

    try:
        print("Loading embedding model (first run ~30s)...", flush=True)
        vec = embed_texts(["test"])[0]
        print(f"Embeddings:         OK ({len(vec)} dims)")
    except Exception as exc:
        print(f"\nFAIL: Embeddings — {exc}")
        return 1

    print("\nAll checks passed. Run: cd .. && ./start.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
