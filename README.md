# MBTIverse

A compact system for analyzing a news brief through **16 MBTI-style agents** plus a **Meta Reviewer**.  
Backend: **FastAPI** (with Swagger). Frontend: **Vite + React + Tailwind**.

---

## 1) Overview

- **Endpoint-first**: `POST /full_pipeline` returns agent reactions and a meta synthesis in a single call.
- **Clean UI**: a white, professional panel that accepts text and renders:
  - 16 agent cards (subtle color + icon per type)
  - Meta Reviewer output as Markdown (tables/lists supported), or as tidy sections if JSON is returned.
- **Guardrails**: `meta_char_limit` lets you cap Meta Reviewer output by characters (hard clamp on server).

**Repo layout**
```
server.py                 # FastAPI app (Swagger at /docs)
agents/
  personas.py             # 16 agents (ISTJ…ENTJ)
  meta_reviewer.py        # MetaReviewerAgent.review(...)
mbitverse-ui/             # Vite + React + Tailwind panel
  src/
    MbitverseWhitePanel.tsx
    App.tsx
    main.tsx
    index.css
  vite.config.ts
  tailwind.config.cjs
  postcss.config.cjs
```

---

## 2) Quickstart (Development)

### Backend
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

### Frontend
```bash
cd mbitverse-ui
npm install
npm run dev
# UI: http://localhost:5173
```

**Dev proxy (recommended)** – `mbitverse-ui/vite.config.ts`:
```ts
server: {
  proxy: {
    "/full_pipeline": { target: "http://localhost:8000", changeOrigin: true },
    "/agents": { target: "http://localhost:8000", changeOrigin: true },
    "/reaction": { target: "http://localhost:8000", changeOrigin: true }
  }
}
```

> Without a proxy, set `VITE_API_BASE=http://localhost:8000` and enable CORS in FastAPI.

**Requirements**: Python 3.10+, Node 20.16+ (20.19+ recommended), npm 10+.

---

## 3) API (essentials)

**`POST /full_pipeline`** → returns:
```json
{
  "news": "...",
  "results": [{ "personality": "INTJ", "reaction": "..." }],
  "meta_review": "markdown or JSON string",
  "errors": { "ISTP": "TimeoutError: ..." }
}
```

**Body fields (subset):**
- `news` *(string)* or `news_lines` *(list of strings)*
- `agents` *(array, optional)* — omit for all 16
- `temperature`, `top_p`, `max_tokens` *(optional)*
- `meta_char_limit` *(int, optional; default 1200)* — hard character cap for meta

**Curl**
```bash
curl -s -X POST http://localhost:8000/full_pipeline   -H "Content-Type: application/json"   -d '{"news":"NVIDIA unveils an energy‑efficient GPU...", "meta_char_limit": 1200}'
```

---

## 4) Production

Build the UI and serve it from FastAPI for a single-origin app:

```bash
cd mbitverse-ui && npm run build
```

In `server.py`:
```py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.mount("/app", StaticFiles(directory="mbitverse-ui/dist", html=True), name="app")

@app.get("/")
def root():
    return FileResponse(os.path.join("mbitverse-ui", "dist", "index.html"))
```
Run: `uvicorn server:app --port 8000` → open http://localhost:8000

---

## 5) Troubleshooting (quick)

- **404 `/full_pipeline`**: run Uvicorn from the folder containing `server.py`. Check `/docs` lists the route.
- **CORS**: use the dev proxy (above) or add FastAPI CORS for `http://localhost:5173`.
- **Tailwind Typography error**: use `plugins: [require("@tailwindcss/typography")]` in `tailwind.config.cjs`.

---

## License

MIT © MBTIverse Contributors
