"""Reporting Agent — aggregates every agent finding into readable documentation."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Project, Report
from .base import AgentResult, BaseAgent, Finding
from ..utils import utcnow


class ReportingAgent(BaseAgent):
    name = "reporting_agent"
    label = "Reporting Agent"

    def analyse(self, db: Session, project: Project) -> AgentResult:
        return AgentResult(
            agent=self.name,
            score=100.0,
            summary="Reporting agent runs after the specialist agents; call compose() with their results.",
        )

    def compose(
        self,
        db: Session,
        project: Project,
        agent_results: dict[str, AgentResult],
        engine_output: dict,
        report_type: str = "daily",
    ) -> Report:
        lines: list[str] = []
        lines.append(f"# {project.project_name} — {report_type.replace('-', ' ').title()} Report")
        lines.append(f"Generated {utcnow():%d %b %Y %H:%M} UTC · {project.location}")
        lines.append("")
        lines.append("## Project health")
        lines.append(f"- Project risk score: {engine_output['project_risk_score']}/100 ({engine_output['risk_band']})")
        lines.append(f"- Incidents predicted next 30 days: {engine_output['predicted_incidents']}")
        lines.append(f"- Workers on site: {project.workers_on_site}")
        lines.append("")

        for key, result in agent_results.items():
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append(result.summary)
            for finding in result.findings[:5]:
                lines.append(f"- [{finding.severity.upper()}] {finding.title} — {finding.detail}")
            lines.append("")

        if engine_output.get("recommendations"):
            lines.append("## Recommended actions")
            for i, rec in enumerate(engine_output["recommendations"], 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        if engine_output.get("patterns"):
            lines.append("## Recurring patterns")
            for pattern in engine_output["patterns"]:
                lines.append(f"- {pattern}")

        report = Report(
            project_id=project.project_id,
            report_type=report_type,
            title=f"{project.project_name} {report_type} report — {utcnow():%d %b %Y}",
            body="\n".join(lines),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def summarise(self, agent_results: dict[str, AgentResult]) -> AgentResult:
        findings = [
            Finding(
                title=f"{name.replace('_', ' ').title()} summary",
                detail=result.summary,
                severity="low",
                category="report",
            )
            for name, result in agent_results.items()
        ]
        return AgentResult(
            agent=self.name,
            score=100.0,
            summary=f"Aggregated {len(agent_results)} agent reports into audit-ready documentation.",
            findings=findings,
        )
