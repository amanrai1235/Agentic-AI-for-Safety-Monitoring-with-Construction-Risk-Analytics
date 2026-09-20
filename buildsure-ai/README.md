# BuildSure AI — Agentic Construction Risk Intelligence Platform

Full implementation of the project spec: five specialist AI agents, a construction risk
intelligence engine, five dashboards and a notification/escalation workflow.

- **Backend** — FastAPI + SQLAlchemy (SQLite by default, Postgres ready)
- **Frontend** — React 18 + Vite + Tailwind + Recharts
- **Database** — the exact schema from section 9 of the spec (projects, site_risks,
  safety_incidents, ppe_violations, compliance_checks, insurance_cases, reports, alerts)
  plus `agent_runs` for the agent audit trail

## Run it

Full instructions, including Windows, Docker and troubleshooting, are in
[RUNNING.md](RUNNING.md).

```bash
# option 1 — one command (Windows: run.bat)
./start.sh

# option 2 — two terminals
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed                 # 3 projects of realistic site data
uvicorn app.main:app --reload      # http://localhost:8000/docs

cd frontend
npm install
npm run dev                        # http://localhost:5173
```

For a single-server deployment, run `npm run build` in `frontend/` — the API then serves
the built React app at `http://localhost:8000`.

Tests: `cd backend && python -m pytest`.
Live demo data: `python -m app.simulate --interval 5`, then press **Go live** in the app header.

## How the agent network works

```
site data ──► Site Risk Agent ──┐
              Safety Agent ─────┤
              Compliance Agent ─┼──► Risk Intelligence Engine ──► Reporting Agent ──► dashboards
              Insurance Agent ──┘         (consolidate, score,         (daily,        + alerts
                                           predict, rank)           executive, audit)
```

Every agent implements the same contract (`app/agents/base.py`): it analyses the project
data and returns an `AgentResult` with a 0–100 score, findings, metrics and
recommendations. The orchestrator (`app/engine/orchestrator.py`) runs the four
specialists, consolidates them, writes a report, updates project scores and dispatches
notifications — that is the Milestone 4 "agent orchestration" deliverable.

| Agent | What it reasons over | Key output |
|---|---|---|
| Site Risk | hazards, zones, probability × impact | site risk score, 5×5 heat map, hot zones |
| Safety | PPE detections, incidents, lost days | PPE compliance rate, accident-prone zones |
| Compliance | regulatory register, inspections | compliance score, audit readiness |
| Insurance | claims, incident load, open hazards | exposure, risk band, claim risk scores |
| Reporting | all of the above | daily / executive / audit documents |

The intelligence engine weights the specialists (site 35%, safety 30%, compliance 20%,
insurance 15%), counts severity pressure to forecast incidents for the next 30 days,
detects recurring patterns across agents, and ranks the actions that move the score most.

## Screens (mapped to the milestones)

| Milestone | Screen | Route |
|---|---|---|
| 1 — site risk monitoring | Site risk dashboard: active risks, hot zones, inherent vs residual heat map, hazard panel | `/site-risk` |
| 2 — safety intelligence | Safety dashboard: PPE compliance by type, incident trend, open violations | `/safety` |
| 3 — compliance & insurance | Compliance dashboard + regulatory register; insurance exposure and claim register | `/compliance`, `/insurance` |
| 4 — reporting & deployment | Command centre: project risk score, agent collaboration, escalations, portfolio roll-up; report generation | `/`, `/reports` |

## API surface

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | service check |
| GET/POST | `/api/projects` | site register |
| GET/POST/PATCH | `/api/risks` | hazard ingestion and close-out |
| GET/POST/PATCH | `/api/ppe-violations` | PPE detections |
| GET/POST | `/api/incidents` | safety incidents |
| GET/POST/PATCH | `/api/compliance-checks` | regulatory register |
| GET/POST | `/api/insurance-cases` | claims |
| POST | `/api/agents/{agent}/run/{project_id}` | run one agent |
| POST | `/api/agents/run-network/{project_id}` | run the full network + engine + report |
| GET | `/api/agents/runs`, `/api/agents/performance` | agent audit trail and performance |
| GET | `/api/dashboards/{site-risk,safety,compliance,insurance,executive}/{id}` | dashboard read models |
| GET | `/api/dashboards/portfolio` | cross-project roll-up |
| GET/POST | `/api/reports`, `/api/reports/generate/{id}` | documentation |
| GET/PATCH | `/api/alerts` | alert log and acknowledgement |

Interactive docs at `http://localhost:8000/docs`.

## Notifications

`app/services/notifications.py` routes alerts by severity — critical goes to email, SMS,
Teams and the dashboard, and escalates site engineer → safety officer → project manager →
HSE director. With no credentials in `.env` it runs in log-only mode, so the demo works
offline; add SMTP/webhook values to send for real.

## Project layout

```
backend/
  app/
    agents/       site_risk, safety, compliance, insurance, reporting (+ base contract)
    engine/       intelligence.py (risk engine), orchestrator.py
    routers/      projects, site, governance, agents, dashboards, reporting
    services/     notifications.py
    models.py schemas.py database.py config.py seed.py main.py
  tests/test_api.py
frontend/
  src/
    components/   Layout, Primitives (KPI, panel, meter, dial), RiskMatrix
    pages/        CommandCentre, SiteRisk, Safety, Compliance, Insurance, Reports, Projects
    lib/          api.js, useData.js, format.js
```

## Notes for the demo

- "Run agent network" in the header executes all five agents live and rewrites the scores,
  alerts and report — good thing to press while presenting.
- Logging a hazard on the Projects screen shows the data path end to end: form → API →
  database → agent → heat map → alert.
- The seed data covers three sites with different risk profiles so the portfolio table
  is not uniform.
