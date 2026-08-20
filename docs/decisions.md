# Architecture decisions

A running log of *why* things are shaped the way they are, not just *how* they
work — the how is in the code and `DEPLOYMENT.md`; the reasoning behind each
choice tends to get lost once it's only in chat history. New entries go at
the bottom.

## Web app: Python backend stays separate from the Cloudflare Worker

The Worker (`worker/`) only serves the built frontend and proxies `/api/*` to
a separately-hosted FastAPI backend (`backend/`) — it does not run the report
logic itself. Cloudflare Workers run on V8 isolates: no raw socket access
(so `automated_email.py`'s `smtplib`/STARTTLS flow can't run there), and no
room for the optional local Hugging Face path (`transformers`/`torch` are
far too large for a Worker's size/CPU limits). Rewriting the mail-sending and
AI logic to fit Workers' constraints was considered and rejected — it would
mean maintaining two implementations of the same logic. Keeping Python
unchanged and adding a thin proxy was less work and zero regression risk to
the already-tested pipeline.

## `report_builder.py`: one shared pipeline for CLI and API

`run_report.py` (CLI) and `backend/main.py` (API) both need "load KPIs →
generate insights → build email content." This used to be written out
separately in each (`generate_and_send_report()`'s steps 2-4, and
`backend/main.py`'s `_build_report()`) — same logic, two places that could
silently drift apart. `report_builder.build_report(df)` is now the single
implementation both call. The CLI's per-step progress messages still print,
just from the single result afterward rather than interleaved with each
step — a deliberate small UX trade-off (no incremental output during a slow
AI call) in exchange for not having two copies of the pipeline.

## `automated_email.py` keeps using Gmail/SMTP, not a transactional email API

Considered switching to an HTTP-based transactional email provider (Resend,
SendGrid, Postmark) since that's the more "cloud-native" choice and would
have been required if the backend logic had moved into the Worker. Since the
Python backend stays on a real server (see above), `smtplib` still works
fine, and switching providers would mean re-plumbing credentials and losing
the existing Gmail App Password setup for no functional gain. Revisit if the
backend ever needs to run somewhere that blocks outbound SMTP.

## `API_AUTH_TOKEN` defaults to empty (auth disabled) unless set

Mirrors the existing pattern in `config.py` (`AI_ENABLED`, `USE_LOCAL_MODEL`
also default off) — local development and testing should need zero setup.
The trade-off: `/api/reports/send`, `/api/reports/preview`, and
`/api/data/upload` are unauthenticated until an operator explicitly sets
`API_AUTH_TOKEN` before deploying publicly. This is a real gap if someone
deploys without reading `DEPLOYMENT.md`'s note about it — acceptable for now
since this is a single-operator internal tool, not something to leave
unset for a multi-tenant deployment.

## CSV upload mutates `config.DATA_SOURCE["path"]` in-process

`POST /api/data/upload` writes the file to `data/uploaded.csv` and points
`config.DATA_SOURCE["path"]` at it for the rest of the process's lifetime,
rather than threading a "current dataset" parameter through every endpoint.
This is a deliberate single-user simplicity trade-off: it works because
there's one operator and one backend process. It would race under
concurrent multi-user use (two people uploading different files would each
silently make their upload "the" current dataset for everyone) — not a
concern at this project's current scale, but the reason a real multi-tenant
version would need per-session or per-request data handling instead of a
shared global path.

## Fly.io is the documented default backend host (not Render)

Both work — `backend/Dockerfile` is host-agnostic — but Fly.io was chosen as
the primary documented path per explicit preference, with Render kept as a
documented alternative (`backend/render.yaml`) rather than removed, since
it's still a valid option and was the original default.

## Frontend design system follows a semrush.com reference

Requested explicitly, not a default choice: bold oversized headlines, pill
buttons, a violet/lime/mint palette, bento-style KPI tiles, and the
vertical-bar "waveform" motif (`WaveBars.tsx`) all trace back to
user-supplied screenshots of semrush.com, translated onto this app's actual
sections (hero → KPI strip → highlight tiles → report preview panel → dark
send-CTA).
