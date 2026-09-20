"""Agent execution endpoints — run one agent, or orchestrate the whole network."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..agents.compliance import ComplianceAgent
from ..agents.insurance import InsuranceAgent
from ..agents.safety import SafetyAgent
from ..agents.site_risk import SiteRiskAgent
from ..database import get_db
from ..engine.orchestrator import run_agent_network
from ..models import AgentRun, Project
from ..schemas import AgentRunOut

router = APIRouter(prefix="/api/agents", tags=["agents"])

REGISTRY = {
    "site-risk": SiteRiskAgent(),
    "safety": SafetyAgent(),
    "compliance": ComplianceAgent(),
    "insurance": InsuranceAgent(),
}


def _project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.get("")
def list_agents():
    return [
        {"key": key, "name": agent.name, "label": agent.label}
        for key, agent in REGISTRY.items()
    ] + [
        {"key": "reporting", "name": "reporting_agent", "label": "Reporting Agent"},
        {"key": "engine", "name": "risk_intelligence_engine", "label": "Construction Risk Intelligence Engine"},
    ]


@router.post("/{agent_key}/run/{project_id}")
def run_single_agent(agent_key: str, project_id: int, db: Session = Depends(get_db)):
    agent = REGISTRY.get(agent_key)
    if not agent:
        raise HTTPException(404, f"Unknown agent '{agent_key}'")
    return agent.run(db, _project(db, project_id)).as_dict()


@router.post("/run-network/{project_id}")
def run_network(project_id: int, report_type: str = "daily", db: Session = Depends(get_db)):
    """Milestone 4: full orchestration across all agents + intelligence engine."""
    return run_agent_network(db, _project(db, project_id), report_type=report_type)


@router.get("/runs", response_model=list[AgentRunOut])
def agent_runs(project_id: int | None = None, limit: int = 40, db: Session = Depends(get_db)):
    query = db.query(AgentRun)
    if project_id:
        query = query.filter(AgentRun.project_id == project_id)
    return query.order_by(AgentRun.created_at.desc()).limit(limit).all()


@router.get("/performance")
def agent_performance(project_id: int | None = None, db: Session = Depends(get_db)):
    """Powers the agent performance panel on the command centre."""
    query = db.query(AgentRun)
    if project_id:
        query = query.filter(AgentRun.project_id == project_id)
    runs = query.order_by(AgentRun.created_at.desc()).limit(200).all()

    summary: dict[str, dict] = {}
    for run in runs:
        entry = summary.setdefault(
            run.agent, {"agent": run.agent, "runs": 0, "findings": 0, "score": 0.0, "avg_ms": 0}
        )
        entry["runs"] += 1
        entry["findings"] += run.findings
        entry["score"] += run.score
        entry["avg_ms"] += run.duration_ms

    for entry in summary.values():
        entry["score"] = round(entry["score"] / entry["runs"], 1)
        entry["avg_ms"] = round(entry["avg_ms"] / entry["runs"])
    return list(summary.values())
