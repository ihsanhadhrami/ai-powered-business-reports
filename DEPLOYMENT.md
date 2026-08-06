# Deploying the web app

This turns the CLI tool into a browser app with three pieces:

```
Browser → Cloudflare Worker (worker/)      static frontend + /api/* proxy
              └─ proxies /api/*  →  FastAPI backend (backend/), on Render/Fly/Railway/any Docker host
                                        └─ imports business_metrics.py, ai_insights.py,
                                           automated_email.py, config.py, utils/ unchanged
```

The Python report-generation logic is unchanged and still uses Gmail/SMTP via
`automated_email.py`. Cloudflare Workers can't run `smtplib`-based SMTP or the
optional local Hugging Face AI path, so that logic stays on a real Python host;
the Worker's job is just to serve the frontend and forward `/api/*` calls.

## 1. Local development

Run the backend and frontend side by side:

```bash
# Terminal 1 — backend (repo root)
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

`frontend/vite.config.ts` proxies `/api/*` to `http://localhost:8000` in dev,
so open http://localhost:5173 and everything works without any extra config.
Copy `.env.example` to `.env` at the repo root first if you want real email
sending or AI insights locally.

## 2. Deploy the backend

The backend is a standard Docker container — deployable anywhere. `backend/render.yaml`
is one concrete example (Render, free tier, no CLI needed); the same
`backend/Dockerfile` works unchanged on Fly.io, Railway, or a VPS.

**Render:**
1. Push this repo to GitHub.
2. In the Render dashboard: New → Blueprint → point at the repo (it reads `backend/render.yaml`).
3. Set the env vars Render prompts for: `EMAIL_SENDER`, `EMAIL_PASSWORD` (a
   Gmail [App Password](https://myaccount.google.com/apppasswords), not your
   real password), `EMAIL_RECIPIENTS`, `API_AUTH_TOKEN` (pick a random
   string), `ALLOWED_ORIGINS` (your Worker's URL, added after step 3 below —
   can be updated later).
4. Note the deployed URL, e.g. `https://business-reports-api.onrender.com`.

**Fly.io / Railway / a VPS:** build the same image —
`docker build -f backend/Dockerfile -t business-reports-api .` (build context
must be the repo root) — and set the same env vars.

## 3. Deploy the Cloudflare Worker (frontend + proxy)

```bash
cd frontend && npm install && npm run build   # produces frontend/dist
cd ../worker && npm install
npx wrangler login                             # one-time, opens a browser

# Point the Worker at your deployed backend:
npx wrangler secret put BACKEND_URL            # paste the Render/Fly/Railway URL
npx wrangler secret put API_AUTH_TOKEN         # same value set on the backend, if any

npx wrangler deploy
```

Wrangler prints the deployed URL (`https://business-reports-app.<subdomain>.workers.dev`
by default, or a custom domain if configured in the Cloudflare dashboard).
Add that URL to the backend's `ALLOWED_ORIGINS` env var so CORS allows it.

## 4. Verify

- `GET https://<worker-url>/api/health` → `{"status":"ok"}`
- Open `https://<worker-url>/` → the dashboard should load KPIs, charts, and
  the report preview from the live backend.
- Click "Generate Report", then "Send Report Now" (only enabled once
  `EMAIL_SENDER`/`EMAIL_PASSWORD` are set on the backend).

## Notes

- **`API_AUTH_TOKEN`** gates the sensitive routes (`/api/reports/preview`,
  `/api/reports/send`, `/api/data/upload`, `/api/config`, `/api/data`,
  `/api/charts/*`) behind an `X-API-Key` header — set it before exposing the
  backend publicly, since those routes send real email and can incur AI
  costs. Leave it unset for local development.
- **Scheduling**: this pass only wires up the manual, browser-driven flow —
  clicking "Generate Report" / "Send Report Now". Automating it (e.g. a daily
  send) is a fast-follow, most naturally done with a
  [Cloudflare Cron Trigger](https://developers.cloudflare.com/workers/configuration/cron-triggers/)
  on the Worker calling `POST /api/reports/send`, since Workers can't run the
  CLI's `run_report.py --schedule` long-lived loop.
- Creating the Render/Fly/Railway account and running `wrangler login`/`deploy`
  requires your own credentials — those steps can't be done for you.
