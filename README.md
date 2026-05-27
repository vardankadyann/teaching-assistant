# RAG Teaching Assistant

An AI teaching assistant that answers student questions **grounded in your course materials** using Retrieval-Augmented Generation (RAG).

## Features

- **Document ingestion** — Upload PDF, Markdown, or plain text
- **Semantic search** — Local embeddings (`all-MiniLM-L6-v2`) + ChromaDB vector store
- **Three teaching modes**
  - **Explain** — Step-by-step explanations with check-for-understanding
  - **Socratic** — Guiding questions instead of direct answers
  - **Quiz** — Practice questions and feedback
- **Source citations** — See which excerpts supported each answer
- **Sample course** — ML intro notes load automatically on first run

## Architecture

```
Course files → Chunking → Embeddings → ChromaDB
                              ↓
Student question → Retrieve top-k chunks → LLM + context → Answer + sources
```

## Quick start

### 1. Backend

```bash
cd teaching-assistant/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY for full AI responses
uvicorn app.main:app --reload --port 8000
```

### 2. UI (pick one)

**Built-in (Python only)** — open [http://localhost:8000](http://localhost:8000) after starting the backend.

**React (optional)** — requires Node.js 18+:

```bash
cd teaching-assistant/frontend
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

### Without OpenAI

The app still runs: retrieval returns relevant excerpts. Set `OPENAI_API_KEY` in `backend/.env` for generated teaching responses.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Ask a question (body: `message`, `mode`, `history`) |
| `/api/ingest` | POST | Upload a document (multipart file) |
| `/api/ingest/sample` | POST | Reload sample ML materials |
| `/api/status` | GET | Index stats and API key status |
| `/api/index` | DELETE | Clear the knowledge base |

## Project layout

```
teaching-assistant/
├── backend/           # FastAPI + RAG pipeline
├── frontend/          # React chat UI
├── sample_materials/  # Demo course content
└── README.md
```

## Customization

- **Chunk size / overlap** — `CHUNK_SIZE`, `CHUNK_OVERLAP` in `.env`
- **Retrieval depth** — `TOP_K` (default 5)
- **Model** — `OPENAI_MODEL` (default `gpt-4o-mini`)
- **System prompts** — `backend/app/rag/chain.py`

## Deploy to production

- **[DEPLOY_VERCEL.md](DEPLOY_VERCEL.md)** — Vercel (serverless + Upstash Vector)
- **[DEPLOY.md](DEPLOY.md)** — Render, Fly.io, Railway, Docker, VPS

Quick test with Docker locally:

```bash
docker compose up --build
```

## Requirements

- Python 3.10+
- Node.js 18+ (optional React UI only)
- ~500MB disk for embedding model (downloaded on first run)
- OpenAI API key (optional but recommended)
