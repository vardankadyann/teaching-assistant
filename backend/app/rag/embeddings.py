from functools import lru_cache
from typing import List

from app.config import settings


def _provider() -> str:
    if settings.embedding_provider != "auto":
        return settings.embedding_provider
    if settings.openai_api_key and not settings.openai_api_key.startswith("sk-your"):
        return "openai"
    if settings.vercel:
        return "fastembed"
    return "fastembed"


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    provider = _provider()
    if provider == "openai":
        return _embed_openai(texts)
    if provider == "fastembed":
        return _embed_fastembed(texts)
    return _embed_local(texts)


def _embed_openai(texts: List[str]) -> List[List[float]]:
    from openai import OpenAI

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(
        input=texts,
        model=settings.openai_embedding_model,
    )
    return [item.embedding for item in response.data]


@lru_cache(maxsize=1)
def _get_fastembed_model():
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=settings.fastembed_model)


def _embed_fastembed(texts: List[str]) -> List[List[float]]:
    model = _get_fastembed_model()
    return [vec.tolist() for vec in model.embed(texts)]


@lru_cache(maxsize=1)
def _get_local_model():
    from sentence_transformers import SentenceTransformer

    settings.hf_cache_path.mkdir(parents=True, exist_ok=True)
    return SentenceTransformer(
        settings.embedding_model,
        cache_folder=str(settings.hf_cache_path),
    )


def _embed_local(texts: List[str]) -> List[List[float]]:
    model = _get_local_model()
    vectors = model.encode(texts, show_progress_bar=False)
    return [v.tolist() for v in vectors]
