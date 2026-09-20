"""Dashboard read models — one endpoint per milestone screen."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..agents.compliance import ComplianceAgent
from ..agents.insurance import InsuranceAgent
from ..agents.safety import SafetyAgent
from ..agents.site_risk import SiteRiskAgent
from ..database import get_db
from ..engine import intelligence
from ..models import Alert, PPEViolation, Project, SiteRisk
from ..services.notifications import ESCALATION_ORDER

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])

site_agent = SiteRiskAgent()
safety_agent = SafetyAgent()
compliance_agent = ComplianceAgent()
insurance_agent = InsuranceAgent()


def _project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.get("/site-risk/{project_id}")
def site_risk_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _project(db, project_id)
    result = site_agent.run(db, project, persist=False)
    risks = (
        db.query(SiteRisk)
        .filter(SiteRisk.project_id == project_id, SiteRisk.status != "closed")
        .order_by(SiteRisk.detected_at.desc())
        .limit(12)
        .all()
    )
    return {
        "project": project.project_name,
        "metrics": result.metrics,
        "summary": result.summary,
        "findings": [f.as_dict() for f in result.findings],
        "recommendations": result.recommendations,
        "recent_risks": [
            {
                "risk_id": r.risk_id,
                "risk_type": r.risk_type,
                "zone": r.zone,
                "description": r.description,
                "severity": r.severity,
                "probability": r.probability,
                "impact": r.impact,
                "detected_at": r.detected_at,
                "source": r.source,
            }
            for r in risks
        ],
    }


@router.get("/safety/{project_id}")
def safety_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _project(db, project_id)
    result = safety_agent.run(db, project, persist=False)
    violations = (
        db.query(PPEViolation)
        .filter(PPEViolation.project_id == project_id, PPEViolation.resolved.is_(False))
        .order_by(PPEViolation.timestamp.desc())
        .limit(12)
        .all()
    )
    return {
        "project": project.project_name,
        "metrics": result.metrics,
        "summary": result.summary,
        "findings": [f.as_dict() for f in result.findings],
        "recommendations": result.recommendations,
        "open_violations": [
            {
                "violation_id": v.violation_id,
                "worker_id": v.worker_id,
                "violation_type": v.violation_type,
                "zone": v.zone,
                "confidence": v.confidence,
                "timestamp": v.timestamp,
            }
            for v in violations
        ],
    }


@router.get("/compliance/{project_id}")
def compliance_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _project(db, project_id)
    compliance = compliance_agent.run(db, project, persist=False)
    insurance = insurance_agent.run(db, project, persist=False)
    return {
        "project": project.project_name,
        "compliance": {
            "metrics": compliance.metrics,
            "summary": compliance.summary,
            "findings": [f.as_dict() for f in compliance.findings],
            "recommendations": compliance.recommendations,
        },
        "insurance": {
            "metrics": insurance.metrics,
            "summary": insurance.summary,
            "findings": [f.as_dict() for f in insurance.findings],
            "recommendations": insurance.recommendations,
        },
    }


@router.get("/insurance/{project_id}")
def insurance_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _project(db, project_id)
    result = insurance_agent.run(db, project, persist=False)
    return {
        "project": project.project_name,
        "metrics": result.metrics,
        "summary": result.summary,
        "findings": [f.as_dict() for f in result.findings],
        "recommendations": result.recommendations,
    }


@router.get("/executive/{project_id}")
def executive_dashboard(project_id: int, db: Session = Depends(get_db)):
    project = _project(db, project_id)
    results = {
        "site_risk_agent": site_agent.run(db, project, persist=False),
        "safety_agent": safety_agent.run(db, project, persist=False),
        "compliance_agent": compliance_agent.run(db, project, persist=False),
        "insurance_agent": insurance_agent.run(db, project, persist=False),
    }
    engine = intelligence.consolidate(results)
    alerts = (
        db.query(Alert)
        .filter(Alert.project_id == project_id)
        .order_by(Alert.created_at.desc())
        .limit(8)
        .all()
    )
    incidents_prevented = sum(
        1 for r in db.query(SiteRisk).filter(SiteRisk.project_id == project_id, SiteRisk.status == "closed").all()
    )
    return {
        "project": {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "location": project.location,
            "contractor": project.contractor,
            "workers_on_site": project.workers_on_site,
            "status": project.status,
        },
        "engine": engine,
        "agent_summaries": {name: r.summary for name, r in results.items()},
        "agent_metrics": {name: r.metrics for name, r in results.items()},
        "incidents_prevented": incidents_prevented,
        "estimated_cost_avoided": round(incidents_prevented * 36_000, 2),
        "escalation_path": ESCALATION_ORDER,
        "alerts": [
            {
                "alert_id": a.alert_id,
                "severity": a.severity,
                "alert_type": a.alert_type,
                "message": a.message,
                "source_agent": a.source_agent,
                "created_at": a.created_at,
            }
            for a in alerts
        ],
    }


@router.get("/portfolio")
def portfolio(db: Session = Depends(get_db)):
    """Cross-project roll-up for the executive command centre."""
    projects = db.query(Project).all()
    rows = []
    for project in projects:
        results = {
            "site_risk_agent": site_agent.run(db, project, persist=False),
            "safety_agent": safety_agent.run(db, project, persist=False),
            "compliance_agent": compliance_agent.run(db, project, persist=False),
            "insurance_agent": insurance_agent.run(db, project, persist=False),
        }
        engine = intelligence.consolidate(results)
        rows.append(
            {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "location": project.location,
                "workers_on_site": project.workers_on_site,
                "project_risk_score": engine["project_risk_score"],
                "risk_band": engine["risk_band"],
                "critical_findings": engine["critical_findings"],
                "predicted_incidents": engine["predicted_incidents"],
                "ppe_compliance": results["safety_agent"].metrics.get("ppe_compliance_rate", 0),
                "compliance_score": results["compliance_agent"].metrics.get("compliance_score", 0),
                "exposure": results["insurance_agent"].metrics.get("total_exposure", 0),
            }
        )
    return {
        "projects": rows,
        "portfolio_risk_score": round(sum(r["project_risk_score"] for r in rows) / max(len(rows), 1)),
        "total_exposure": round(sum(r["exposure"] for r in rows), 2),
        "total_workers": sum(r["workers_on_site"] for r in rows),
    }
