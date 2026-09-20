"""Database models — mirrors the BuildSure AI schema (section 9 of the spec)."""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .utils import utcnow


def now() -> datetime:
    return utcnow()


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_name: Mapped[str] = mapped_column(String(160))
    location: Mapped[str] = mapped_column(String(160))
    contractor: Mapped[str] = mapped_column(String(160), default="")
    start_date: Mapped[datetime] = mapped_column(DateTime, default=now)
    status: Mapped[str] = mapped_column(String(40), default="active")
    workers_on_site: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    safety_score: Mapped[float] = mapped_column(Float, default=0.0)
    compliance_score: Mapped[float] = mapped_column(Float, default=0.0)
    insurance_exposure: Mapped[float] = mapped_column(Float, default=0.0)

    site_risks: Mapped[list["SiteRisk"]] = relationship(back_populates="project", cascade="all, delete")
    safety_incidents: Mapped[list["SafetyIncident"]] = relationship(back_populates="project", cascade="all, delete")
    ppe_violations: Mapped[list["PPEViolation"]] = relationship(back_populates="project", cascade="all, delete")
    compliance_checks: Mapped[list["ComplianceCheck"]] = relationship(back_populates="project", cascade="all, delete")
    insurance_cases: Mapped[list["InsuranceCase"]] = relationship(back_populates="project", cascade="all, delete")
    reports: Mapped[list["Report"]] = relationship(back_populates="project", cascade="all, delete")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="project", cascade="all, delete")


class SiteRisk(Base):
    __tablename__ = "site_risks"

    risk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    risk_type: Mapped[str] = mapped_column(String(80))
    zone: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    probability: Mapped[int] = mapped_column(Integer, default=3)   # 1-5
    impact: Mapped[int] = mapped_column(Integer, default=3)        # 1-5
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open")
    mitigation: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(40), default="cctv")
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="site_risks")

    @property
    def score(self) -> int:
        return self.probability * self.impact


class SafetyIncident(Base):
    __tablename__ = "safety_incidents"

    incident_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    incident_type: Mapped[str] = mapped_column(String(80))
    zone: Mapped[str] = mapped_column(String(80), default="")
    severity: Mapped[str] = mapped_column(String(20), default="minor")
    description: Mapped[str] = mapped_column(Text, default="")
    lost_days: Mapped[int] = mapped_column(Integer, default=0)
    incident_date: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="safety_incidents")


class PPEViolation(Base):
    __tablename__ = "ppe_violations"

    violation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    worker_id: Mapped[str] = mapped_column(String(40))
    violation_type: Mapped[str] = mapped_column(String(60))   # hard hat, vest, boots, gloves, harness
    zone: Mapped[str] = mapped_column(String(80), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    resolved: Mapped[bool] = mapped_column(default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="ppe_violations")


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    compliance_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    regulation_name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), default="general")
    compliance_status: Mapped[str] = mapped_column(String(30), default="compliant")
    finding: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="compliance_checks")


class InsuranceCase(Base):
    __tablename__ = "insurance_cases"

    case_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    claim_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text, default="")
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="open")
    documentation_status: Mapped[str] = mapped_column(String(30), default="incomplete")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="insurance_cases")


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    report_type: Mapped[str] = mapped_column(String(60))   # daily, executive, audit, project-health
    title: Mapped[str] = mapped_column(String(200), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    generated_by: Mapped[str] = mapped_column(String(60), default="reporting_agent")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="reports")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    alert_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    message: Mapped[str] = mapped_column(Text)
    source_agent: Mapped[str] = mapped_column(String(60), default="site_risk_agent")
    channel: Mapped[str] = mapped_column(String(40), default="dashboard")
    acknowledged: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    project: Mapped[Project] = relationship(back_populates="alerts")


class AgentRun(Base):
    """Audit log of every agent execution — feeds the agent performance panel."""
    __tablename__ = "agent_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.project_id"))
    agent: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(20), default="success")
    findings: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[str] = mapped_column(Text, default="")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
