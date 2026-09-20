"""Shared agent contract.

Every specialist agent takes a project + its site data, reasons over it with
deterministic risk rules, and returns a normalised AgentResult. The orchestrator
never needs to know how an individual agent reaches its conclusion.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from ..models import Alert, AgentRun, Project


@dataclass
class Finding:
    title: str
    detail: str
    severity: str = "medium"          # low | medium | high | critical
    category: str = "general"
    score: float = 0.0
    recommendation: str = ""
    raise_alert: bool = False

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AgentResult:
    agent: str
    score: float                       # 0-100, higher = healthier, except risk agents (see each agent)
    summary: str
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    duration_ms: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "score": round(self.score, 1),
            "summary": self.summary,
            "findings": [f.as_dict() for f in self.findings],
            "metrics": self.metrics,
            "recommendations": self.recommendations,
            "duration_ms": self.duration_ms,
        }


SEVERITY_WEIGHT = {"low": 1, "medium": 3, "high": 7, "critical": 12}


class BaseAgent:
    name: str = "base_agent"
    label: str = "Base Agent"

    def run(self, db: Session, project: Project, persist: bool = True) -> AgentResult:
        """Analyse a project. Dashboard reads pass persist=False so that simply
        viewing a screen does not create duplicate alerts or audit rows."""
        started = time.perf_counter()
        result = self.analyse(db, project)
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        if persist:
            self._persist(db, project, result)
        return result

    def analyse(self, db: Session, project: Project) -> AgentResult:  # pragma: no cover - interface
        raise NotImplementedError

    def _persist(self, db: Session, project: Project, result: AgentResult) -> None:
        db.add(
            AgentRun(
                project_id=project.project_id,
                agent=self.name,
                findings=len(result.findings),
                score=result.score,
                summary=result.summary,
                duration_ms=result.duration_ms,
            )
        )
        for finding in result.findings:
            if finding.raise_alert:
                db.add(
                    Alert(
                        project_id=project.project_id,
                        alert_type=finding.category,
                        severity=finding.severity,
                        message=f"{finding.title}: {finding.detail}",
                        source_agent=self.name,
                    )
                )
        db.commit()
