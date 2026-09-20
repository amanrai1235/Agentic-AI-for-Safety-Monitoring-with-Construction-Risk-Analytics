"""Reports and alerts."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..agents.reporting import ReportingAgent
from ..agents.compliance import ComplianceAgent
from ..agents.insurance import InsuranceAgent
from ..agents.safety import SafetyAgent
from ..agents.site_risk import SiteRiskAgent
from ..database import get_db
from ..engine import intelligence
from ..models import Alert, Project, Report
from ..schemas import AlertOut, ReportOut

router = APIRouter(prefix="/api", tags=["reports & alerts"])
reporter = ReportingAgent()


@router.get("/reports", response_model=list[ReportOut])
def list_reports(project_id: int | None = None, report_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    if project_id:
        query = query.filter(Report.project_id == project_id)
    if report_type:
        query = query.filter(Report.report_type == report_type)
    return query.order_by(Report.generated_at.desc()).limit(50).all()


@router.post("/reports/generate/{project_id}", response_model=ReportOut, status_code=201)
def generate_report(project_id: int, report_type: str = "daily", db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    results = {
        "site_risk_agent": SiteRiskAgent().run(db, project, persist=False),
        "safety_agent": SafetyAgent().run(db, project, persist=False),
        "compliance_agent": ComplianceAgent().run(db, project, persist=False),
        "insurance_agent": InsuranceAgent().run(db, project, persist=False),
    }
    engine = intelligence.consolidate(results)
    return reporter.compose(db, project, results, engine, report_type=report_type)


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(project_id: int | None = None, severity: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if project_id:
        query = query.filter(Alert.project_id == project_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    return query.order_by(Alert.created_at.desc()).limit(100).all()


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert
