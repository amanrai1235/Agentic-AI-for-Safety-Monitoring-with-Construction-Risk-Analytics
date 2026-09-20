"""Compliance Agent — regulatory validation, inspection tracking, audit readiness."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import ComplianceCheck, Project
from .base import AgentResult, BaseAgent, Finding
from ..utils import utcnow

CATEGORIES = ["OSHA standards", "Building codes", "Environmental regulations", "Insurance requirements"]


class ComplianceAgent(BaseAgent):
    name = "compliance_agent"
    label = "Compliance Agent"

    def analyse(self, db: Session, project: Project) -> AgentResult:
        checks = db.query(ComplianceCheck).filter(ComplianceCheck.project_id == project.project_id).all()
        if not checks:
            return AgentResult(
                agent=self.name,
                score=0.0,
                summary="No compliance checks recorded yet. Run an inspection to establish a baseline.",
                metrics={"compliance_score": 0, "open_violations": 0, "audit_readiness": 0, "by_category": []},
            )

        violations = [c for c in checks if c.compliance_status == "violation"]
        pending = [c for c in checks if c.compliance_status == "pending"]
        compliant = [c for c in checks if c.compliance_status == "compliant"]

        findings: list[Finding] = []
        for check in violations:
            overdue = check.due_date and check.due_date < utcnow()
            findings.append(
                Finding(
                    title=f"Violation: {check.regulation_name}",
                    detail=check.finding or "Requirement not met at last inspection.",
                    severity="critical" if overdue else "high",
                    category="compliance",
                    score=10 if overdue else 6,
                    recommendation=(
                        f"Close out {check.regulation_name} and re-submit evidence"
                        + (" — the corrective deadline has passed." if overdue else " before the due date.")
                    ),
                    raise_alert=bool(overdue),
                )
            )

        soon = [
            c for c in pending
            if c.due_date and c.due_date <= utcnow() + timedelta(days=7)
        ]
        for check in soon:
            findings.append(
                Finding(
                    title=f"Inspection due: {check.regulation_name}",
                    detail=f"Due {check.due_date:%d %b %Y}.",
                    severity="medium",
                    category="inspection",
                    score=3,
                    recommendation="Book the inspector and attach the supporting documentation pack.",
                )
            )

        compliance_score = len(compliant) / len(checks) * 100
        audit_readiness = max(0.0, compliance_score - len(pending) * 2)

        grouped: dict[str, list[ComplianceCheck]] = defaultdict(list)
        for check in checks:
            grouped[check.category].append(check)

        return AgentResult(
            agent=self.name,
            score=compliance_score,
            summary=(
                f"{compliance_score:.1f}% of {len(checks)} requirements met, "
                f"{len(violations)} open violations, audit readiness {audit_readiness:.0f}%."
            ),
            findings=findings,
            metrics={
                "compliance_score": round(compliance_score, 1),
                "open_violations": len(violations),
                "pending_inspections": len(pending),
                "audit_readiness": round(audit_readiness),
                "documentation_status": "complete" if not pending else "action needed",
                "by_category": [
                    {
                        "category": cat,
                        "rate": round(
                            len([c for c in items if c.compliance_status == "compliant"]) / len(items) * 100
                        ),
                        "checks": len(items),
                    }
                    for cat, items in sorted(grouped.items())
                ],
            },
            recommendations=[f.recommendation for f in findings if f.recommendation][:5],
        )
