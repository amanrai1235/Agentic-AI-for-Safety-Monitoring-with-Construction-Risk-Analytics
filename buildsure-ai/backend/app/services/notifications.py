"""Notification & workflow module.

Channels are configured through the environment. With no credentials set the
service runs in log-only mode so the platform is demo-safe out of the box.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Alert, Project

logger = logging.getLogger("buildsure.notifications")
settings = get_settings()

ESCALATION_ORDER = ["site engineer", "safety officer", "project manager", "HSE director"]


def dispatch_alerts(db: Session, project: Project, engine_output: dict) -> list[dict]:
    """Route unsent alerts to the right channel and escalate critical ones."""
    pending = (
        db.query(Alert)
        .filter(Alert.project_id == project.project_id, Alert.acknowledged.is_(False))
        .order_by(Alert.created_at.desc())
        .limit(25)
        .all()
    )

    sent: list[dict] = []
    for alert in pending:
        channels = _channels_for(alert.severity)
        alert.channel = ", ".join(channels)
        sent.append(
            {
                "alert_id": alert.alert_id,
                "severity": alert.severity,
                "message": alert.message,
                "channels": channels,
                "escalated_to": _escalation_path(alert.severity),
            }
        )
        logger.info("[%s] %s -> %s", alert.severity.upper(), alert.message, channels)

    if engine_output["project_risk_score"] < settings.critical_risk_score:
        escalation = Alert(
            project_id=project.project_id,
            alert_type="project_risk",
            severity="critical",
            message=(
                f"Project risk score dropped to {engine_output['project_risk_score']}/100 "
                f"({engine_output['risk_band']}). Mitigation workflow opened."
            ),
            source_agent="risk_intelligence_engine",
            channel="email, teams, sms",
        )
        db.add(escalation)
        sent.append(
            {
                "alert_id": None,
                "severity": "critical",
                "message": escalation.message,
                "channels": ["email", "teams", "sms"],
                "escalated_to": ESCALATION_ORDER,
            }
        )

    db.commit()
    return sent


def _channels_for(severity: str) -> list[str]:
    if severity == "critical":
        return ["email", "sms", "teams", "dashboard"]
    if severity == "high":
        return ["email", "teams", "dashboard"]
    return ["dashboard"]


def _escalation_path(severity: str) -> list[str]:
    if severity == "critical":
        return ESCALATION_ORDER
    if severity == "high":
        return ESCALATION_ORDER[:3]
    return ESCALATION_ORDER[:2]
