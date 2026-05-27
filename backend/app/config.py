import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    fastembed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./data/chroma"
    hf_cache_dir: str = "./data/huggingface"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_provider: str = "auto"  # auto | openai | fastembed | local
    vector_backend: str = "auto"  # auto | upstash | chroma
    upstash_vector_rest_url: str = ""
    upstash_vector_rest_token: str = ""
    upstash_namespace: str = "course_materials"
    top_k: int = 5
    chunk_size: int = 800
    chunk_overlap: int = 120
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    vercel: bool = False

    @field_validator(
        "openai_api_key",
        "upstash_vector_rest_url",
        "upstash_vector_rest_token",
        mode="before",
    )
    @classmethod
    def strip_quotes(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                return value[1:-1]
        return value

    @property
    def cors_origin_list(self) -> list:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        vercel_url = os.environ.get("VERCEL_URL")
        if vercel_url:
            origins.append(f"https://{vercel_url}")
        return origins

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_dir)

    @property
    def hf_cache_path(self) -> Path:
        return Path(self.hf_cache_dir)


def _configure_hf_cache() -> None:
    if settings.embedding_provider in ("openai", "fastembed"):
        return
    cache = settings.hf_cache_path.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache))
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(cache))


settings = Settings(vercel=bool(os.environ.get("VERCEL")))
_configure_hf_cache()
