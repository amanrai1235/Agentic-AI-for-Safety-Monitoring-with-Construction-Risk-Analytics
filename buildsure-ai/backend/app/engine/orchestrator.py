"""Agent orchestration — runs the agent network for a project in dependency order."""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..agents.base import AgentResult
from ..agents.compliance import ComplianceAgent
from ..agents.insurance import InsuranceAgent
from ..agents.reporting import ReportingAgent
from ..agents.safety import SafetyAgent
from ..agents.site_risk import SiteRiskAgent
from ..models import Project
from ..services.notifications import dispatch_alerts
from . import intelligence

SPECIALISTS = [SiteRiskAgent(), SafetyAgent(), ComplianceAgent(), InsuranceAgent()]
REPORTER = ReportingAgent()


def run_agent_network(db: Session, project: Project, report_type: str = "daily") -> dict:
    """Milestone 4 orchestration: specialists -> intelligence engine -> reporting -> notifications."""
    results: dict[str, AgentResult] = {}
    for agent in SPECIALISTS:
        results[agent.name] = agent.run(db, project)

    engine_output = intelligence.consolidate(results)

    report = REPORTER.compose(db, project, results, engine_output, report_type=report_type)
    results[REPORTER.name] = REPORTER.summarise(results)

    project.risk_score = engine_output["project_risk_score"]
    project.safety_score = results["safety_agent"].metrics.get("safety_score", 0)
    project.compliance_score = results["compliance_agent"].metrics.get("compliance_score", 0)
    project.insurance_exposure = results["insurance_agent"].metrics.get("total_exposure", 0)
    db.commit()

    notifications = dispatch_alerts(db, project, engine_output)

    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "engine": engine_output,
        "agents": {name: result.as_dict() for name, result in results.items()},
        "report": {"report_id": report.report_id, "title": report.title, "body": report.body},
        "notifications": notifications,
    }
