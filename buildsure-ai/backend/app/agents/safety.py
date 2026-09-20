"""Safety Agent — PPE compliance, worker safety monitoring, accident-prone zones."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import PPEViolation, Project, SafetyIncident
from .base import AgentResult, BaseAgent, Finding
from ..utils import utcnow

PPE_TYPES = ["hard hat", "safety vest", "safety boots", "protective gloves", "fall harness"]


class SafetyAgent(BaseAgent):
    name = "safety_agent"
    label = "Safety Agent"

    def analyse(self, db: Session, project: Project) -> AgentResult:
        window = utcnow() - timedelta(days=30)
        violations = (
            db.query(PPEViolation)
            .filter(PPEViolation.project_id == project.project_id, PPEViolation.timestamp >= window)
            .all()
        )
        incidents = (
            db.query(SafetyIncident)
            .filter(SafetyIncident.project_id == project.project_id, SafetyIncident.incident_date >= window)
            .all()
        )
        today = [v for v in violations if v.timestamp.date() == utcnow().date()]
        open_violations = [v for v in violations if not v.resolved]

        workers = max(project.workers_on_site, 1)
        checks = workers * len(PPE_TYPES)
        compliance_rate = max(0.0, 100.0 - (len(violations) / max(checks, 1)) * 100)

        findings: list[Finding] = []
        by_type = Counter(v.violation_type for v in open_violations)
        for ptype, count in by_type.items():
            if count >= 3:
                findings.append(
                    Finding(
                        title=f"Repeat {ptype} violations",
                        detail=f"{count} unresolved {ptype} detections in the last 30 days.",
                        severity="high" if count >= 5 else "medium",
                        category="ppe",
                        score=count * 2,
                        recommendation=f"Run a toolbox talk on {ptype} use and issue replacement stock at the gate.",
                        raise_alert=count >= 5,
                    )
                )

        zones = Counter(i.zone for i in incidents if i.zone)
        for zone, count in zones.items():
            if count >= 2:
                findings.append(
                    Finding(
                        title=f"Accident-prone zone: {zone}",
                        detail=f"{count} recorded incidents in 30 days.",
                        severity="high",
                        category="unsafe_zone",
                        score=count * 5,
                        recommendation=f"Re-sequence work in {zone} and add a dedicated safety watch.",
                        raise_alert=count >= 3,
                    )
                )

        lost_days = sum(i.lost_days for i in incidents)
        if lost_days > 5:
            findings.append(
                Finding(
                    title="Lost-time injuries rising",
                    detail=f"{lost_days} lost worker-days recorded this month.",
                    severity="critical" if lost_days > 15 else "high",
                    category="lost_time",
                    score=lost_days,
                    recommendation="Escalate to the project safety board and review the last three incident reports.",
                    raise_alert=lost_days > 15,
                )
            )

        safety_score = max(
            0.0,
            compliance_rate - len(incidents) * 2.5 - lost_days * 0.8,
        )

        return AgentResult(
            agent=self.name,
            score=min(safety_score, 100.0),
            summary=(
                f"PPE compliance {compliance_rate:.0f}%, {len(open_violations)} open violations, "
                f"{len(incidents)} incidents in 30 days."
            ),
            findings=findings,
            metrics={
                "ppe_compliance_rate": round(compliance_rate, 1),
                "safety_violations": len(open_violations),
                "violations_today": len(today),
                "workers_monitored": project.workers_on_site,
                "safety_score": round(min(safety_score, 100.0)),
                "incidents_30d": len(incidents),
                "lost_days": lost_days,
                "compliance_by_ppe": [
                    {
                        "type": ptype,
                        "rate": round(max(0.0, 100 - (by_type.get(ptype, 0) / max(workers, 1)) * 100), 1),
                        "violations": by_type.get(ptype, 0),
                    }
                    for ptype in PPE_TYPES
                ],
                "incident_trend": self._trend(incidents),
            },
            recommendations=[f.recommendation for f in findings if f.recommendation][:5],
        )

    @staticmethod
    def _trend(incidents: list[SafetyIncident]) -> list[dict]:
        buckets: Counter[str] = Counter()
        for i in incidents:
            buckets[i.incident_date.strftime("%d %b")] += 1
        return [{"day": k, "incidents": v} for k, v in sorted(buckets.items())]
