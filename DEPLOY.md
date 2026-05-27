# Deploy the Teaching Assistant

The app ships as a **Docker** container (FastAPI + UI + embeddings + ChromaDB).

**Requirements for production**

| Item | Notes |
|------|--------|
| `OPENAI_API_KEY` | Required for full AI answers |
| Persistent disk | Keeps uploaded docs & vector DB across restarts |
| ~2 GB RAM | Embedding model + ChromaDB |
| Build time | First Docker build ~10–15 min (downloads PyTorch) |

---

## Option 1: Render (recommended, free tier available)

1. Push the project to **GitHub** (do not commit `backend/.env`).

2. Go to [render.com](https://render.com) → **New** → **Blueprint** → connect the repo.

3. Render reads `render.yaml` automatically.

4. Set secrets in the dashboard:
   - `OPENAI_API_KEY` = your key
   - `CORS_ORIGINS` = `https://YOUR-SERVICE.onrender.com`

5. Deploy. Open the service URL.

**Note:** Free tier sleeps when idle; first request after sleep can take 1–2 minutes.

---

## Option 2: Fly.io

```bash
cd teaching-assistant
fly auth login
fly launch --no-deploy    # use existing fly.toml
fly volumes create teaching_assistant_data --size 1
fly secrets set OPENAI_API_KEY=sk-your-key
fly secrets set CORS_ORIGINS=https://YOUR-APP.fly.dev
fly deploy
```

Open `https://YOUR-APP.fly.dev`.

---

## Option 3: Railway

1. Push to GitHub.
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**.
3. Railway detects the `Dockerfile`.
4. Add a **Volume** mounted at `/data`.
5. Variables:
   ```
   OPENAI_API_KEY=sk-...
   CHROMA_PERSIST_DIR=/data/chroma
   HF_CACHE_DIR=/data/huggingface
   CORS_ORIGINS=https://your-app.up.railway.app
   PORT=8000
   ```

---

## Option 4: Any VPS / cloud VM (Docker)

```bash
git clone <your-repo> teaching-assistant
cd teaching-assistant
cp backend/.env.example backend/.env
# edit backend/.env

docker compose up -d --build
```

App runs at `http://YOUR_SERVER_IP:8000`.

Put **nginx** or **Caddy** in front for HTTPS.

---

## Option 5: Google Cloud Run

```bash
gcloud run deploy teaching-assistant \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars CHROMA_PERSIST_DIR=/tmp/chroma,HF_CACHE_DIR=/tmp/hf \
  --set-secrets OPENAI_API_KEY=openai-key:latest
```

Cloud Run is **ephemeral** unless you attach a volume (gen2) — uploads may be lost on redeploy. Prefer Render/Fly with a disk for this app.

---

## Environment variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | `sk-...` | LLM responses |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `CHROMA_PERSIST_DIR` | `/data/chroma` | Vector DB path |
| `HF_CACHE_DIR` | `/data/huggingface` | Embedding model cache |
| `CORS_ORIGINS` | `https://myapp.onrender.com` | Allowed browser origins |
| `PORT` | `8000` | Set automatically on most platforms |

---

## After deploy

1. Open your URL — the UI is served at `/`.
2. Click **Reload sample course** or upload PDFs/MD/TXT.
3. Ask a question in Explain / Socratic / Quiz mode.

---

## Security checklist

- Never commit `backend/.env` or API keys to Git.
- Set `CORS_ORIGINS` to your real domain only.
- Rotate keys if they were ever committed or shared.
