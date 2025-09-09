# MBTIverse — 16 MBTI Agents + Meta-Reviewer (FastAPI + React)

Paste a news brief, get reactions from **16 MBTI-style agents** and a **Meta Reviewer** that synthesizes the panel.  
Backend: **FastAPI** (with Swagger). Frontend: **Vite + React + Tailwind**.

---

## ✨ Features

- **/full_pipeline**: run multiple agents and return a panel + meta-review in one call.
- **Clean, white UI** (“MBTIverse Panel”):
  - Agent cards with subtle colors/icons.
  - Meta-review rendered as **Markdown** (headings, bullets, tables).
  - If meta returns **structured JSON**, it’s presented as tidy sections automatically.
- **Hard character cap** for meta via `meta_char_limit` (server-side truncation on sentence boundary).
- Swagger docs at **`/docs`**.

---

## 🗂️ Repo layout

```
.
├─ server.py                 # FastAPI app (Swagger at /docs)
├─ agents/
│  ├─ personas.py            # 16 MBTI agents (ISTJ … ENTJ)
│  └─ meta_reviewer.py       # MetaReviewerAgent.review(...)
└─ mbitverse-ui/             # Vite + React + Tailwind frontend
   ├─ src/
   │  ├─ MbitverseWhitePanel.tsx
   │  ├─ App.tsx
   │  ├─ main.tsx
   │  └─ index.css
   ├─ vite.config.ts
   ├─ tailwind.config.cjs
   ├─ postcss.config.cjs
   └─ package.json
```

> If your paths differ, adjust accordingly.

---

## 🔧 Requirements

- **Python** 3.10+ (3.11 recommended)
- **Node.js** ≥ 20.16.0 (≥ **20.19.0** recommended to silence engine warnings)
- **npm** 10+

---

## 🚀 Quick start (development)

### 1) Backend (FastAPI)

```bash
# from the repo root
python -m venv venv && source venv/bin/activate    # or your preferred env
pip install -r requirements.txt                    # ensure fastapi, uvicorn are included
uvicorn server:app --reload --port 8000
```

Open **http://localhost:8000/docs** and confirm `POST /full_pipeline` is listed.

### 2) Frontend (Vite + React)

```bash
cd mbitverse-ui
npm install
npm run dev
```

Open **http://localhost:5173**.

#### Dev proxy (recommended)
`mbitverse-ui/vite.config.ts` proxies API calls to FastAPI:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/full_pipeline": { target: "http://localhost:8000", changeOrigin: true },
      "/agents": { target: "http://localhost:8000", changeOrigin: true },
      "/reaction": { target: "http://localhost:8000", changeOrigin: true }
    }
  }
});
```

This lets the UI `fetch("/full_pipeline")` with no CORS setup.

> **Alternative:** skip the proxy and set `VITE_API_BASE=http://localhost:8000` (see “Config” below), plus add CORS middleware in FastAPI.

---

## ⚙️ Frontend setup details

Install UI deps if you’re wiring from scratch:

```bash
cd mbitverse-ui
npm i react-markdown remark-gfm
npm i -D tailwindcss postcss autoprefixer @tailwindcss/typography
```

**tailwind.config.cjs**
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [require("@tailwindcss/typography")]
};
```

**postcss.config.cjs**
```js
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } };
```

**src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body, #root { height: 100%; background: #fff; }
```

The main UI lives in **`src/MbitverseWhitePanel.tsx`** and is rendered by `App.tsx`.

---

## 🧠 API summary

**Endpoints**
- `GET /agents` → `{ count, agents }`
- `POST /reaction/{agent_code}` → `{ personality, reaction }`
- `POST /full_pipeline` → panel response (see below)

**Request: `MultiAgentRequest`**
```json
{
  "news": "ECB hints at rate cuts...",
  "news_lines": ["optional", "alternative"],      // either 'news' or 'news_lines'
  "agents": ["ISTJ", "ENFP"],                      // omit for all 16
  "temperature": 0.4,
  "top_p": 0.9,
  "max_tokens": 512,
  "meta_char_limit": 1200                          // hard cap for meta review (default 1200)
}
```

**Response: `PanelResponse`**
```json
{
  "news": "...",
  "results": [
    { "personality": "ISTJ", "reaction": "..." },
    { "personality": "ENFP", "reaction": "..." }
  ],
  "meta_review": "markdown string or structured JSON string",
  "errors": { "ISTP": "TimeoutError: ..." }
}
```

**Curl sanity test**
```bash
curl -s -X POST "http://localhost:8000/full_pipeline"   -H "Content-Type: application/json"   -d '{"news":"NVIDIA unveils an energy-efficient GPU...", "meta_char_limit":1200}' | jq .
```

---

## ✂️ Meta Reviewer character limit

To avoid truncated or overly long meta reviews, the server supports a **hard character cap**:

- **Request field**: `meta_char_limit` (default **1200**, min 200, max 8000).
- **Soft limit** is passed into the meta reviewer prompt when supported.
- **Hard limit** clamps the final text on a sentence boundary and appends `…` if needed.

> You can change the default and logic in `server.py` (`_clamp_chars` + `_run_panel`).

---

## 🔒 CORS / direct API base (optional)

If you don’t use the Vite proxy, set an API base and enable CORS:

**Frontend:** `mbitverse-ui/.env`
```
VITE_API_BASE=http://localhost:8000
```

Use it in your fetch calls (add a tiny wrapper), and add CORS to **FastAPI**:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"], allow_headers=["*"],
)
```

---

## 📦 Production

Build the React app and serve it from FastAPI for a single-origin deployment.

**Build**
```bash
cd mbitverse-ui
npm run build
```

**Mount in `server.py`**
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.mount("/app", StaticFiles(directory="mbitverse-ui/dist", html=True), name="app")

@app.get("/")
def root():
    return FileResponse(os.path.join("mbitverse-ui", "dist", "index.html"))
```

Run:
```bash
uvicorn server:app --port 8000
```

Open **http://localhost:8000**.

---

## 🧰 Troubleshooting

- **404 on `/full_pipeline`**  
  You’re likely running the wrong module. Start Uvicorn from the folder containing `server.py`:
  ```bash
  uvicorn server:app --reload --port 8000
  ```
  Confirm at `/docs` that `full_pipeline` exists.

- **CORS errors**  
  Use the Vite proxy (recommended) or enable CORS as shown above.

- **Node engine warnings (EBADENGINE)**  
  Upgrade Node to ≥ **20.19.0**. Warnings are harmless, but upgrading silences them.

- **Tailwind plugin error (`typography is not defined`)**  
  Use `plugins: [require("@tailwindcss/typography")]` in `tailwind.config.cjs`.

---

## 🤝 Contributing

PRs welcome! Please:
1. Keep the panel fast and minimal.
2. Update Swagger examples + this README if you change API shapes.
3. Avoid heavy state libraries for this simple UI.

---

## 📄 License

MIT © MBTIverse Contributors

---

