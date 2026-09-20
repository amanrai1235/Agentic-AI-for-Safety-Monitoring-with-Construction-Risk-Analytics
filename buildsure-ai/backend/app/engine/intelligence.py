"""Construction Risk Intelligence Engine.

Consolidates every agent's findings into one project risk score, predicts
incident likelihood, surfaces recurring patterns and ranks the actions that
will move the score the most.
"""
from __future__ import annotations

from collections import Counter

from ..agents.base import SEVERITY_WEIGHT, AgentResult

# How much each agent contributes to the consolidated project risk score.
AGENT_WEIGHTS = {
    "site_risk_agent": 0.35,
    "safety_agent": 0.30,
    "compliance_agent": 0.20,
    "insurance_agent": 0.15,
}


def band(score: float) -> str:
    if score >= 80:
        return "Low risk"
    if score >= 65:
        return "Moderate risk"
    if score >= 45:
        return "Elevated risk"
    return "Critical risk"


def consolidate(results: dict[str, AgentResult]) -> dict:
    weighted = 0.0
    total_weight = 0.0
    for agent, weight in AGENT_WEIGHTS.items():
        if agent in results:
            weighted += results[agent].score * weight
            total_weight += weight
    project_score = weighted / total_weight if total_weight else 0.0

    all_findings = [f for r in results.values() for f in r.findings]
    severity_counts = Counter(f.severity for f in all_findings)
    pressure = sum(SEVERITY_WEIGHT.get(f.severity, 1) for f in all_findings)

    # Simple incident forecast: severity pressure scaled against the health score.
    predicted = round(pressure / 12 * (1 + (100 - project_score) / 100), 1)

    patterns = _patterns(results)
    recommendations = _rank_recommendations(results)

    return {
        "project_risk_score": round(project_score),
        "risk_band": band(project_score),
        "agent_scores": {name: round(r.score, 1) for name, r in results.items()},
        "critical_findings": severity_counts.get("critical", 0),
        "high_findings": severity_counts.get("high", 0),
        "total_findings": len(all_findings),
        "predicted_incidents": predicted,
        "patterns": patterns,
        "recommendations": recommendations,
    }


def _patterns(results: dict[str, AgentResult]) -> list[str]:
    patterns: list[str] = []
    categories = Counter(f.category for r in results.values() for f in r.findings)
    for category, count in categories.most_common(3):
        if count >= 2:
            patterns.append(
                f"{count} findings share the '{category.replace('_', ' ')}' pattern — treat it as a systemic issue, not isolated events."
            )

    site = results.get("site_risk_agent")
    safety = results.get("safety_agent")
    if site and safety and site.score < 70 and safety.score < 80:
        patterns.append(
            "Site hazards and PPE non-compliance are rising together, which historically precedes a lost-time injury."
        )

    compliance = results.get("compliance_agent")
    insurance = results.get("insurance_agent")
    if compliance and insurance and compliance.score < 90 and insurance.score < 70:
        patterns.append(
            "Open compliance violations overlap with active claims — expect underwriter scrutiny at renewal."
        )
    return patterns


def _rank_recommendations(results: dict[str, AgentResult]) -> list[str]:
    ranked: list[tuple[float, str]] = []
    for result in results.values():
        for finding in result.findings:
            if finding.recommendation:
                weight = SEVERITY_WEIGHT.get(finding.severity, 1) + finding.score / 10
                ranked.append((weight, finding.recommendation))
    ranked.sort(key=lambda item: item[0], reverse=True)

    seen: set[str] = set()
    ordered: list[str] = []
    for _, rec in ranked:
        if rec not in seen:
            seen.add(rec)
            ordered.append(rec)
    return ordered[:6]
