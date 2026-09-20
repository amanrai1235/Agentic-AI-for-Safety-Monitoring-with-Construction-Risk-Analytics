# Running BuildSure AI

You need **Python 3.10+** and **Node 18+**. Nothing else — the demo database is SQLite and
notifications run in log-only mode, so no API keys, no internet, no cloud account.

## Windows

```bat
cd buildsure-ai
run.bat
```

`run.bat` creates the virtualenv, installs everything, seeds the database, opens the API in
its own window and starts the React app. Then open **http://localhost:5173**.

## macOS / Linux

```bash
cd buildsure-ai
./start.sh
```

Then open **http://localhost:5173**.

## Manual, two terminals (what the scripts do)

Terminal 1 — backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python -m app.seed                 # 3 sites of demo data; add --reset to wipe and redo
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:

```bash
cd frontend
npm install
npm run dev
```

| URL | What it is |
|---|---|
| http://localhost:5173 | the platform |
| http://localhost:8000/docs | interactive API docs (Swagger) |
| http://localhost:8000/api/health | service check |

The Vite dev server proxies `/api` to port 8000, so you don't configure anything.

## Optional: live data while you present

A third terminal streams new hazards, PPE detections and incidents into the platform:

```bash
cd backend
source .venv/bin/activate
python -m app.simulate --interval 5
```

Press **Go live** in the app header — the dashboards poll every 10 seconds, so numbers,
heat map cells and alerts move on screen while you talk.

## One server instead of two

```bash
cd frontend && npm run build
cd ../backend && uvicorn app.main:app --port 8000
```

The API now serves the built React app at **http://localhost:8000** — use this for the
final submission or any deployment.

## Docker (Postgres + API + nginx)

```bash
docker compose up --build
```

App on **http://localhost:3000**, API on **http://localhost:8000**, Postgres on 5432.

## Make targets

```
make install   make seed    make api     make web
make build     make test    make demo    make clean
```

## Demo route for an evaluation

1. **Command centre** — project risk score, the four agent scores behind it, recommended
   actions and recurring patterns.
2. Press **Run agent network** — all five agents execute live, scores and alerts rewrite.
3. **Site risk** — inherent vs residual heat map; close out a hazard and watch the matrix change.
4. **Safety** — PPE compliance per type, incident trend, mark a violation corrected.
5. **Compliance** / **Insurance** — regulatory register with filters, claim exposure.
6. **Projects** — log a hazard through the form, then return to Site risk: form → API →
   database → agent → heat map → alert, the whole path in about ten seconds.
7. **Reports & alerts** — generate a daily or executive report; it is written by the
   Reporting Agent from that run's findings, not a template.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Could not reach the backend" on screen | the API isn't running — start uvicorn in the backend folder |
| `Address already in use` | something else holds 8000/5173: `uvicorn app.main:app --port 8001` and set `VITE_API_URL=http://localhost:8001` in `frontend/.env` |
| `ModuleNotFoundError: app` | run uvicorn from inside `backend/`, not the project root |
| `uvicorn: command not found` | the virtualenv isn't active, or use `python -m uvicorn app.main:app` |
| Dashboards look empty | database not seeded: `python -m app.seed --reset` |
| Scores look odd after demoing | reseed with `python -m app.seed --reset` for a clean starting state |
| npm errors on install | Node is below 18: `node -v`, then update |
