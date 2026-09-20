"""Insurance Agent — exposure assessment, claim risk analysis, claim documentation."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import InsuranceCase, Project, SafetyIncident, SiteRisk
from .base import AgentResult, BaseAgent, Finding
from ..utils import utcnow

SEVERITY_MULTIPLIER = {"minor": 1.0, "moderate": 2.0, "major": 4.0, "critical": 6.5}


class InsuranceAgent(BaseAgent):
    name = "insurance_agent"
    label = "Insurance Agent"

    def analyse(self, db: Session, project: Project) -> AgentResult:
        cases = db.query(InsuranceCase).filter(InsuranceCase.project_id == project.project_id).all()
        incidents = (
            db.query(SafetyIncident)
            .filter(
                SafetyIncident.project_id == project.project_id,
                SafetyIncident.incident_date >= utcnow() - timedelta(days=90),
            )
            .all()
        )
        open_risks = (
            db.query(SiteRisk)
            .filter(SiteRisk.project_id == project.project_id, SiteRisk.status != "closed")
            .all()
        )

        open_cases = [c for c in cases if c.status != "settled"]
        exposure = sum(c.estimated_cost for c in open_cases)
        incident_load = sum(SEVERITY_MULTIPLIER.get(i.severity, 1.0) for i in incidents)
        hazard_load = sum(r.probability * r.impact for r in open_risks) / 25

        # 0-100 exposure index; higher means more insurance risk.
        risk_index = min(100.0, incident_load * 1.8 + hazard_load * 2.0 + len(open_cases) * 4.0)

        findings: list[Finding] = []
        for case in open_cases:
            case.risk_score = round(
                min(100.0, case.estimated_cost / 50000 * 20 + SEVERITY_MULTIPLIER.get("moderate", 2) * 5), 1
            )
            if case.documentation_status != "complete":
                findings.append(
                    Finding(
                        title=f"Incomplete claim file: {case.claim_type}",
                        detail=f"Case #{case.case_id} is missing supporting documentation.",
                        severity="high",
                        category="claim_documentation",
                        score=8,
                        recommendation="Attach incident report, photos, witness statements and the site log extract.",
                    )
                )
            if case.estimated_cost >= 250_000:
                findings.append(
                    Finding(
                        title=f"High-value exposure: {case.claim_type}",
                        detail=f"Estimated cost ${case.estimated_cost:,.0f}.",
                        severity="critical",
                        category="exposure",
                        score=15,
                        recommendation="Notify the broker within 24 hours and open a reserve review.",
                        raise_alert=True,
                    )
                )

        if incident_load > 12:
            findings.append(
                Finding(
                    title="Claim frequency trending up",
                    detail=f"Weighted incident load {incident_load:.1f} over 90 days.",
                    severity="high",
                    category="claim_risk",
                    score=12,
                    recommendation="Expect a premium loading at renewal; prepare a mitigation dossier for the underwriter.",
                )
            )

        db.commit()
        band = "Low" if risk_index < 34 else "Medium" if risk_index < 67 else "High"

        return AgentResult(
            agent=self.name,
            score=max(0.0, 100.0 - risk_index),
            summary=(
                f"{len(open_cases)} open cases, ${exposure:,.0f} exposure, insurance risk band {band}."
            ),
            findings=findings,
            metrics={
                "open_cases": len(open_cases),
                "total_exposure": round(exposure, 2),
                "insurance_risk_index": round(risk_index, 1),
                "insurance_risk_band": band,
                "claims_90d": len(incidents),
                "avg_claim_value": round(exposure / max(len(open_cases), 1), 2),
                "cases": [
                    {
                        "case_id": c.case_id,
                        "claim_type": c.claim_type,
                        "estimated_cost": c.estimated_cost,
                        "risk_score": c.risk_score,
                        "status": c.status,
                        "documentation_status": c.documentation_status,
                    }
                    for c in cases
                ],
            },
            recommendations=[f.recommendation for f in findings if f.recommendation][:5],
        )
