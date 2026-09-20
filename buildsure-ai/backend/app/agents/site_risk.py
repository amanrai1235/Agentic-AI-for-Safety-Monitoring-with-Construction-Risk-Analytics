"""Site Risk Agent — monitors site activity, detects hazards, scores site risk."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import Project, SiteRisk
from .base import SEVERITY_WEIGHT, AgentResult, BaseAgent, Finding
from ..utils import utcnow

HAZARD_PLAYBOOK = {
    "fall": "Install edge protection and re-inspect scaffold tie-ins before the next shift.",
    "equipment": "Lock out the unit, run the pre-use checklist and log the operator certificate.",
    "electrical": "De-energise the circuit, mark the panel and schedule a licensed re-test.",
    "environmental": "Suppress dust, cover open excavations and re-check weather hold limits.",
    "structural": "Stop work in the zone until the structural engineer signs the load check.",
    "excavation": "Re-shore the trench face and restrict access to the 2 m exclusion line.",
}


class SiteRiskAgent(BaseAgent):
    name = "site_risk_agent"
    label = "Site Risk Agent"

    def analyse(self, db: Session, project: Project) -> AgentResult:
        risks = (
            db.query(SiteRisk)
            .filter(SiteRisk.project_id == project.project_id)
            .order_by(SiteRisk.detected_at.desc())
            .all()
        )
        open_risks = [r for r in risks if r.status != "closed"]
        recent = [r for r in open_risks if r.detected_at >= utcnow() - timedelta(days=7)]

        findings: list[Finding] = []
        for risk in open_risks:
            exposure = risk.probability * risk.impact          # 1-25 matrix cell
            severity = self._severity(exposure)
            if severity in ("high", "critical"):
                findings.append(
                    Finding(
                        title=f"{risk.risk_type.title()} hazard in {risk.zone or 'unzoned area'}",
                        detail=f"{risk.description} (probability {risk.probability}/5, impact {risk.impact}/5).",
                        severity=severity,
                        category="site_risk",
                        score=exposure,
                        recommendation=self._playbook(risk.risk_type),
                        raise_alert=severity == "critical",
                    )
                )

        zones = Counter(r.zone for r in open_risks if r.zone)
        hot_zones = [z for z, c in zones.items() if c >= 2]
        for zone in hot_zones:
            findings.append(
                Finding(
                    title=f"Risk clustering in {zone}",
                    detail=f"{zones[zone]} open hazards recorded in the same zone this cycle.",
                    severity="high",
                    category="hot_zone",
                    score=zones[zone] * 4,
                    recommendation=f"Run a targeted walk-down of {zone} and brief the crew before shift start.",
                )
            )

        risk_score = self._score(open_risks)
        distribution = Counter(r.risk_type for r in open_risks)

        return AgentResult(
            agent=self.name,
            score=risk_score,
            summary=(
                f"{len(open_risks)} open hazards, {len(hot_zones)} high-risk zones, "
                f"site risk score {risk_score:.0f}/100."
            ),
            findings=findings,
            metrics={
                "active_risks": len(open_risks),
                "high_risk_zones": len(hot_zones),
                "hazards_detected_7d": len(recent),
                "site_risk_score": round(risk_score),
                "distribution": [
                    {"type": k, "count": v, "share": round(v / max(len(open_risks), 1) * 100)}
                    for k, v in distribution.most_common()
                ],
                "heatmap": self._heatmap(open_risks),
                "residual_heatmap": self._heatmap(open_risks, mitigated=True),
            },
            recommendations=[f.recommendation for f in findings if f.recommendation][:5],
        )

    @staticmethod
    def _severity(exposure: int) -> str:
        if exposure >= 17:
            return "critical"
        if exposure >= 11:
            return "high"
        if exposure >= 6:
            return "medium"
        return "low"

    @staticmethod
    def _playbook(risk_type: str) -> str:
        for key, action in HAZARD_PLAYBOOK.items():
            if key in risk_type.lower():
                return action
        return "Assign an owner, set a 24-hour mitigation deadline and re-inspect."

    def _score(self, risks: list[SiteRisk]) -> float:
        """0-100 where 100 is a clean site."""
        if not risks:
            return 100.0
        penalty = sum(SEVERITY_WEIGHT[self._severity(r.probability * r.impact)] for r in risks)
        return max(0.0, 100.0 - min(penalty, 100.0))

    @staticmethod
    def _heatmap(risks: list[SiteRisk], mitigated: bool = False) -> list[list[int]]:
        """5x5 probability x impact matrix. Residual view drops one band after mitigation."""
        grid = [[0] * 5 for _ in range(5)]
        for r in risks:
            p, i = r.probability, r.impact
            if mitigated and r.mitigation:
                p = max(1, p - 1)
                i = max(1, i - 1)
            grid[5 - p][i - 1] += 1
        return grid
