from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TeachingMode(str, Enum):
    EXPLAIN = "explain"
    SOCRATIC = "socratic"
    QUIZ = "quiz"


class SourceChunk(BaseModel):
    text: str
    source: str
    score: Optional[float] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    mode: TeachingMode = TeachingMode.EXPLAIN
    history: List[dict] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    mode: TeachingMode


class IngestResponse(BaseModel):
    filename: str
    chunks_added: int
    message: str


class StatusResponse(BaseModel):
    document_count: int
    chunk_count: int
    has_openai_key: bool
    collection_name: str
