# Business Reports — Frontend

React + TypeScript + Vite + Tailwind CSS. Talks to the FastAPI backend in
`../backend/` over `/api/*` (proxied in dev by `vite.config.ts`, and by the
Cloudflare Worker in `../worker/` in production).

```bash
npm install
npm run dev      # http://localhost:5173, expects the backend on :8000
npm run build    # outputs dist/, consumed by ../worker
```

See `../DEPLOYMENT.md` for the full deployment flow.
