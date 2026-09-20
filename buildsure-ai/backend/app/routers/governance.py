"""Compliance checks and insurance cases."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ComplianceCheck, InsuranceCase
from ..schemas import ComplianceCheckIn, ComplianceCheckOut, InsuranceCaseIn, InsuranceCaseOut

router = APIRouter(prefix="/api", tags=["compliance & insurance"])


@router.get("/compliance-checks", response_model=list[ComplianceCheckOut])
def list_checks(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ComplianceCheck)
    if project_id:
        query = query.filter(ComplianceCheck.project_id == project_id)
    return query.order_by(ComplianceCheck.checked_at.desc()).all()


@router.post("/compliance-checks", response_model=ComplianceCheckOut, status_code=201)
def create_check(payload: ComplianceCheckIn, db: Session = Depends(get_db)):
    check = ComplianceCheck(**payload.model_dump())
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.patch("/compliance-checks/{compliance_id}", response_model=ComplianceCheckOut)
def update_check(compliance_id: int, compliance_status: str, db: Session = Depends(get_db)):
    check = db.get(ComplianceCheck, compliance_id)
    if not check:
        raise HTTPException(404, "Check not found")
    check.compliance_status = compliance_status
    db.commit()
    db.refresh(check)
    return check


@router.get("/insurance-cases", response_model=list[InsuranceCaseOut])
def list_cases(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(InsuranceCase)
    if project_id:
        query = query.filter(InsuranceCase.project_id == project_id)
    return query.order_by(InsuranceCase.created_at.desc()).all()


@router.post("/insurance-cases", response_model=InsuranceCaseOut, status_code=201)
def create_case(payload: InsuranceCaseIn, db: Session = Depends(get_db)):
    case = InsuranceCase(**payload.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case
