# Deploy on Vercel (no OpenAI credits required)

> **Local dev tip:** Use `VECTOR_BACKEND=chroma` in `backend/.env` (default now).
> Use Upstash only on Vercel — avoids slow/hanging cloud connections on your Mac.


Uses **free local embeddings** (FastEmbed) + **Upstash Vector**. Answers come from your course materials; OpenAI is optional.

---

## 1. Create Upstash Vector index

[console.upstash.com](https://console.upstash.com) → **Vector** → **Create Index**

| Setting | Value |
|---------|--------|
| Name | `teaching-assistant` |
| **Dimensions** | **384** |
| **Similarity** | **Cosine** |

> If you previously used **1536** dimensions (OpenAI), create a **new** index with **384**.

Copy `UPSTASH_VECTOR_REST_URL` and `UPSTASH_VECTOR_REST_TOKEN`.

---

## 2. Push to GitHub

```bash
cd teaching-assistant
git add .
git commit -m "Deploy without OpenAI"
git push
```

Do not commit `backend/.env`.

---

## 3. Deploy on Vercel

1. [vercel.com/new](https://vercel.com/new) → import repo  
2. **Environment variables** (Production):

| Name | Value |
|------|--------|
| `UPSTASH_VECTOR_REST_URL` | from Upstash |
| `UPSTASH_VECTOR_REST_TOKEN` | from Upstash |
| `VECTOR_BACKEND` | `upstash` |
| `EMBEDDING_PROVIDER` | `fastembed` |

`OPENAI_API_KEY` is **optional** — skip it for now.

3. **Deploy**

Or with CLI:

```bash
npx vercel --prod
```

---

## 4. Use the app

1. Open `https://YOUR-PROJECT.vercel.app`  
2. **Reload sample course**  
3. Ask a question — answers use retrieved excerpts from your materials  

---

## Vercel env vars summary

**Required**

- `UPSTASH_VECTOR_REST_URL`
- `UPSTASH_VECTOR_REST_TOKEN`
- `VECTOR_BACKEND=upstash`
- `EMBEDDING_PROVIDER=fastembed`

**Optional**

- `OPENAI_API_KEY` — enables full AI-generated teaching responses later

---

## Troubleshooting

| Issue | Fix |
|--------|-----|
| Dimension mismatch | New Upstash index with **384** dimensions |
| Function too large / timeout | Pro plan or wait for cold start; memory set to 3008 MB in `vercel.json` |
| Empty answers | Click **Reload sample course** |
| 500 on first request | Wait ~30s (model loading), retry |
