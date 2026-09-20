"""Site data ingestion: hazards, PPE detections and safety incidents."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PPEViolation, Project, SafetyIncident, SiteRisk
from ..schemas import (
    IncidentIn,
    IncidentOut,
    PPEViolationIn,
    PPEViolationOut,
    SiteRiskIn,
    SiteRiskOut,
)

router = APIRouter(prefix="/api", tags=["site data"])


def _severity(probability: int, impact: int) -> str:
    exposure = probability * impact
    if exposure >= 17:
        return "critical"
    if exposure >= 11:
        return "high"
    if exposure >= 6:
        return "medium"
    return "low"


@router.get("/risks", response_model=list[SiteRiskOut])
def list_risks(project_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(SiteRisk)
    if project_id:
        query = query.filter(SiteRisk.project_id == project_id)
    if status:
        query = query.filter(SiteRisk.status == status)
    return query.order_by(SiteRisk.detected_at.desc()).all()


@router.post("/risks", response_model=SiteRiskOut, status_code=201)
def create_risk(payload: SiteRiskIn, db: Session = Depends(get_db)):
    if not db.get(Project, payload.project_id):
        raise HTTPException(404, "Project not found")
    risk = SiteRisk(**payload.model_dump())
    risk.severity = _severity(risk.probability, risk.impact)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


@router.patch("/risks/{risk_id}", response_model=SiteRiskOut)
def update_risk(risk_id: int, status: str | None = None, mitigation: str | None = None, db: Session = Depends(get_db)):
    risk = db.get(SiteRisk, risk_id)
    if not risk:
        raise HTTPException(404, "Risk not found")
    if status:
        risk.status = status
    if mitigation is not None:
        risk.mitigation = mitigation
    db.commit()
    db.refresh(risk)
    return risk


@router.get("/ppe-violations", response_model=list[PPEViolationOut])
def list_violations(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(PPEViolation)
    if project_id:
        query = query.filter(PPEViolation.project_id == project_id)
    return query.order_by(PPEViolation.timestamp.desc()).limit(200).all()


@router.post("/ppe-violations", response_model=PPEViolationOut, status_code=201)
def create_violation(payload: PPEViolationIn, db: Session = Depends(get_db)):
    violation = PPEViolation(**payload.model_dump())
    db.add(violation)
    db.commit()
    db.refresh(violation)
    return violation


@router.patch("/ppe-violations/{violation_id}", response_model=PPEViolationOut)
def resolve_violation(violation_id: int, resolved: bool = True, db: Session = Depends(get_db)):
    violation = db.get(PPEViolation, violation_id)
    if not violation:
        raise HTTPException(404, "Violation not found")
    violation.resolved = resolved
    db.commit()
    db.refresh(violation)
    return violation


@router.get("/incidents", response_model=list[IncidentOut])
def list_incidents(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(SafetyIncident)
    if project_id:
        query = query.filter(SafetyIncident.project_id == project_id)
    return query.order_by(SafetyIncident.incident_date.desc()).all()


@router.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentIn, db: Session = Depends(get_db)):
    incident = SafetyIncident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
