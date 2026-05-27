import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import (
    ChatRequest,
    ChatResponse,
    IngestResponse,
    StatusResponse,
    TeachingMode,
)
from app.rag.chain import chat
from app.rag.ingest import SUPPORTED_EXTENSIONS, ingest_directory, ingest_file
from app.rag.store import COLLECTION_NAME, get_store

app = FastAPI(
    title="Teaching Assistant API",
    description="RAG-based AI teaching assistant for course materials",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_materials"
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/status", response_model=StatusResponse)
def status():
    try:
        _ensure_sample_materials()
    except Exception:
        pass
    store = get_store()
    doc_count, chunk_count = store.stats()
    return StatusResponse(
        document_count=doc_count,
        chunk_count=chunk_count,
        has_openai_key=bool(settings.openai_api_key),
        collection_name=COLLECTION_NAME,
    )


@app.post("/api/chat", response_model=ChatResponse)
def ask(request: ChatRequest):
    answer, sources = chat(
        message=request.message,
        mode=request.mode,
        history=request.history,
    )
    return ChatResponse(answer=answer, sources=sources, mode=request.mode)


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported type. Use: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        count = ingest_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return IngestResponse(
        filename=file.filename or "upload",
        chunks_added=count,
        message=f"Indexed {count} chunks from {file.filename}",
    )


@app.post("/api/ingest/sample")
def ingest_sample():
    if not SAMPLE_DIR.exists():
        raise HTTPException(status_code=404, detail="Sample materials folder not found")

    results = ingest_directory(SAMPLE_DIR)
    total = sum(results.values())
    return {
        "files": results,
        "total_chunks": total,
        "message": f"Loaded {len(results)} sample files ({total} chunks)",
    }


@app.delete("/api/index")
def clear_index():
    get_store().clear()
    return {"message": "Knowledge base cleared"}


def _ensure_sample_materials() -> None:
    store = get_store()
    if store.is_empty() and SAMPLE_DIR.exists():
        ingest_directory(SAMPLE_DIR)

