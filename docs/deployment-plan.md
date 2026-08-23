# TableMate AI — Deployment Plan

> **Backend:** Railway (FastAPI + Uvicorn)  
> **Frontend:** Vercel (Next.js 14)  
> **Dataset:** Bundled with the backend container via Railway volume / repo

---

## Architecture Overview

```
Browser
  │
  ▼
Vercel (Next.js frontend)
  │  /api/* rewrites (next.config.ts proxy)
  ▼
Railway (FastAPI backend)
  │  loads dataset from /data/zomato_preprocessed.csv
  ▼
Groq Cloud API  ←  GROQ_API_KEY env var
```

The Next.js API proxy rewrites `/api/*` → Railway URL, so the browser never calls the Railway URL directly. **No CORS needed in production.**

---

## Part 1 — Backend on Railway

### 1.1 Files to create

#### `Procfile`
```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

#### `runtime.txt`
```
python-3.11
```

#### `requirements.txt` *(already exists — verify these are present)*
```
fastapi
uvicorn[standard]
pydantic
pandas
groq
python-dotenv
```

---

### 1.2 Railway deployment steps

1. **Push code to GitHub** (all phases committed)

2. **Go to** [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**

3. **Select** `zomato-restaurant_recommender` repo → Railway auto-detects Python

4. **Set environment variables** in Railway dashboard → Settings → Variables:

   | Variable | Value |
   |---|---|
   | `GROQ_API_KEY` | `your_groq_key_here` |
   | `GROQ_MODEL` | `openai/gpt-oss-20b` |
   | `PYTHONIOENCODING` | `utf-8` |

5. **Railway auto-assigns** a public URL like:  
   `https://zomato-restaurant-recommender.up.railway.app`

6. **Verify** the deployment:
   ```
   GET https://your-app.up.railway.app/health
   → {"status":"ok","restaurants_loaded":9565}
   ```

---

### 1.3 Dataset on Railway

The preprocessed CSV (`data/zomato_preprocessed.csv`) must be committed to git **or** regenerated at startup.

**Option A (recommended) — commit the preprocessed CSV:**
```bash
# Remove from .gitignore if present, then commit
git add data/zomato_preprocessed.csv
git commit -m "chore: include preprocessed dataset for Railway deployment"
```

**Option B — regenerate at startup via `nixpacks.toml`:**
```toml
# nixpacks.toml (create at project root)
[phases.build]
cmds = ["pip install -r requirements.txt", "python src/ingest.py"]
```

---

## Part 2 — Frontend on Vercel

### 2.1 `next.config.ts` proxy (already configured)

The `API_URL` env var is read at build time — no code change needed:

```ts
// frontend/next.config.ts
async rewrites() {
  return [{
    source: "/api/:path*",
    destination: `${process.env.API_URL ?? "http://127.0.0.1:8000"}/api/:path*`,
  }];
}
```

---

### 2.2 Vercel deployment steps

1. **Go to** [vercel.com](https://vercel.com) → **Add New Project** → **Import Git Repository**

2. **Select** `zomato-restaurant_recommender` repo

3. **Configure project:**

   | Setting | Value |
   |---|---|
   | **Root Directory** | `frontend` |
   | **Framework Preset** | Next.js (auto-detected) |
   | **Build Command** | `npm run build` |
   | **Output Directory** | `.next` (default) |
   | **Install Command** | `npm install` |

4. **Set environment variables** in Vercel → Settings → Environment Variables:

   | Variable | Value | Environment |
   |---|---|---|
   | `API_URL` | `https://your-app.up.railway.app` | Production, Preview |
   | `NEXT_PUBLIC_API_URL` | `https://your-app.up.railway.app` | Production, Preview |

5. **Deploy** → Vercel publishes to:  
   `https://zomato-restaurant-recommender.vercel.app`

---

### 2.3 Update CORS for production (backend)

Once you have the Vercel URL, update `api/main.py` CORS:

```python
ALLOWED_ORIGINS = [
    "https://zomato-restaurant-recommender.vercel.app",
    "https://*.vercel.app",    # preview deployments
    "http://localhost:3000",   # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

> **Note:** Since all frontend requests go through the Vercel proxy, the browser never hits Railway directly — CORS errors won't occur in production. This update is only needed for direct API access (e.g. Swagger docs, curl).

---

## Part 3 — Environment Files Summary

### Backend (Railway env vars)
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=openai/gpt-oss-20b
PYTHONIOENCODING=utf-8
```

### Frontend (Vercel env vars)
```env
API_URL=https://your-app.up.railway.app
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

### Local dev (already configured)
```env
# .env  (project root)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
API_URL=http://127.0.0.1:8000
```

---

## Part 4 — Pre-deployment Checklist

### Before pushing to GitHub
- [ ] `.env` and `.env.local` are in `.gitignore` (never commit API keys)
- [ ] `data/zomato_preprocessed.csv` is committed (or `nixpacks.toml` added)
- [ ] `Procfile` created at project root
- [ ] `requirements.txt` has all backend deps
- [ ] `frontend/node_modules/` is in `.gitignore`
- [ ] `frontend/.next/` is in `.gitignore`

### Before deploying Railway
- [ ] `GROQ_API_KEY` set in Railway env vars
- [ ] `GET /health` returns `{"status":"ok","restaurants_loaded":9565}`
- [ ] `POST /api/recommend` returns restaurant JSON

### Before deploying Vercel
- [ ] `API_URL` points to live Railway URL (no trailing slash)
- [ ] Root directory set to `frontend/` in Vercel settings
- [ ] Local production build passes: `cd frontend && npm run build`
- [ ] TypeScript compiles cleanly: `npx tsc --noEmit`

### Post-deployment smoke test
- [ ] `https://your-vercel-app.vercel.app` loads TableMate AI UI
- [ ] Location dropdown populates (calls Railway `/api/locations`)
- [ ] Get Recommendations returns real Groq AI results
- [ ] Bookmarks persist across page refreshes (localStorage)
- [ ] Responsive layout works on mobile

---

## Part 5 — Command Reference

```bash
# Local development
venv\Scripts\uvicorn.exe api.main:app --host 127.0.0.1 --port 8000  # backend
cd frontend && npm run dev                                             # frontend → localhost:3000

# Production build test (before pushing)
cd frontend
npm run build       # must complete with 0 errors
npm run start       # test production build at localhost:3000

# TypeScript check
npx tsc --noEmit

# Git push
git add .
git commit -m "feat: complete Phase 8 Next.js frontend + deployment config"
git push origin main
```

---

## Part 6 — Estimated Deployment Time

| Step | Time |
|---|---|
| Create `Procfile` + `runtime.txt`, push to GitHub | 5 min |
| Railway auto-deploy + health check | 3–5 min |
| Vercel import + set env vars + deploy | 3–5 min |
| Update CORS + re-deploy Railway | 2 min |
| End-to-end smoke test | 5 min |
| **Total** | **~18–20 min** |
