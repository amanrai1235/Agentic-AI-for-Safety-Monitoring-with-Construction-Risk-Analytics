from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectIn(BaseModel):
    project_name: str
    location: str
    contractor: str = ""
    status: str = "active"
    workers_on_site: int = 0
    start_date: datetime | None = None


class ProjectOut(ORMModel):
    project_id: int
    project_name: str
    location: str
    contractor: str
    status: str
    workers_on_site: int
    start_date: datetime
    risk_score: float
    safety_score: float
    compliance_score: float
    insurance_exposure: float


class SiteRiskIn(BaseModel):
    project_id: int
    risk_type: str
    zone: str = ""
    description: str = ""
    probability: int = Field(3, ge=1, le=5)
    impact: int = Field(3, ge=1, le=5)
    status: str = "open"
    mitigation: str = ""
    source: str = "cctv"


class SiteRiskOut(ORMModel):
    risk_id: int
    project_id: int
    risk_type: str
    zone: str
    description: str
    probability: int
    impact: int
    severity: str
    status: str
    mitigation: str
    source: str
    detected_at: datetime


class PPEViolationIn(BaseModel):
    project_id: int
    worker_id: str
    violation_type: str
    zone: str = ""
    confidence: float = 0.9


class PPEViolationOut(ORMModel):
    violation_id: int
    project_id: int
    worker_id: str
    violation_type: str
    zone: str
    confidence: float
    resolved: bool
    timestamp: datetime


class IncidentIn(BaseModel):
    project_id: int
    incident_type: str
    zone: str = ""
    severity: str = "minor"
    description: str = ""
    lost_days: int = 0


class IncidentOut(ORMModel):
    incident_id: int
    project_id: int
    incident_type: str
    zone: str
    severity: str
    description: str
    lost_days: int
    incident_date: datetime


class ComplianceCheckIn(BaseModel):
    project_id: int
    regulation_name: str
    category: str = "general"
    compliance_status: str = "compliant"
    finding: str = ""
    due_date: datetime | None = None


class ComplianceCheckOut(ORMModel):
    compliance_id: int
    project_id: int
    regulation_name: str
    category: str
    compliance_status: str
    finding: str
    due_date: datetime | None
    checked_at: datetime


class InsuranceCaseIn(BaseModel):
    project_id: int
    claim_type: str
    description: str = ""
    estimated_cost: float = 0.0
    status: str = "open"
    documentation_status: str = "incomplete"


class InsuranceCaseOut(ORMModel):
    case_id: int
    project_id: int
    claim_type: str
    description: str
    estimated_cost: float
    risk_score: float
    status: str
    documentation_status: str
    created_at: datetime


class ReportOut(ORMModel):
    report_id: int
    project_id: int
    report_type: str
    title: str
    body: str
    generated_by: str
    generated_at: datetime


class AlertOut(ORMModel):
    alert_id: int
    project_id: int
    alert_type: str
    severity: str
    message: str
    source_agent: str
    channel: str
    acknowledged: bool
    created_at: datetime


class AgentRunOut(ORMModel):
    run_id: int
    project_id: int
    agent: str
    status: str
    findings: int
    score: float
    summary: str
    duration_ms: int
    created_at: datetime
