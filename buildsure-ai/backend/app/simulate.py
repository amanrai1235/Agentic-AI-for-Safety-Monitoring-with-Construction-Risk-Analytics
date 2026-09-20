"""Live site simulator.

Feeds new hazards, PPE detections and incidents into the platform on a timer, so
the dashboards move while you are presenting. Run it in a third terminal:

    python -m app.simulate                 # every 6 seconds, all projects
    python -m app.simulate --interval 3 --project 1
"""
from __future__ import annotations

import argparse
import random
import time

from .database import SessionLocal
from .models import Alert, PPEViolation, Project, SafetyIncident, SiteRisk
from .utils import utcnow

HAZARDS = [
    ("fall hazard", "Guardrail removed for a material lift and not reinstated.", 4, 5),
    ("equipment risk", "Excavator operating inside the pedestrian walkway.", 3, 4),
    ("electrical hazard", "Extension lead running through standing water.", 4, 4),
    ("environmental risk", "Dust reading above the permitted limit at the boundary.", 3, 2),
    ("excavation risk", "Spoil stacked at the trench edge.", 3, 5),
    ("structural risk", "Props removed early from the slab soffit.", 2, 5),
]
PPE = ["hard hat", "safety vest", "safety boots", "protective gloves", "fall harness"]
ZONES = ["Level 14 slab edge", "Crane bay A", "Basement B2", "North trench", "Scaffold tower 3", "Gate 2"]
INCIDENTS = [("slip and fall", "minor", 1), ("struck by object", "moderate", 3), ("manual handling injury", "minor", 2)]


def emit(project_id: int) -> str:
    db = SessionLocal()
    try:
        roll = random.random()
        if roll < 0.45:
            risk_type, description, probability, impact = random.choice(HAZARDS)
            exposure = probability * impact
            severity = "critical" if exposure >= 17 else "high" if exposure >= 11 else "medium" if exposure >= 6 else "low"
            db.add(
                SiteRisk(
                    project_id=project_id,
                    risk_type=risk_type,
                    zone=random.choice(ZONES),
                    description=description,
                    probability=probability,
                    impact=impact,
                    severity=severity,
                    source=random.choice(["cctv", "sensor", "site inspection"]),
                    detected_at=utcnow(),
                )
            )
            message = f"hazard · {risk_type} ({severity})"
        elif roll < 0.85:
            ptype = random.choice(PPE)
            db.add(
                PPEViolation(
                    project_id=project_id,
                    worker_id=f"W-{project_id}{random.randint(100, 999)}",
                    violation_type=ptype,
                    zone=random.choice(ZONES),
                    confidence=round(random.uniform(0.72, 0.99), 2),
                    timestamp=utcnow(),
                )
            )
            message = f"PPE · missing {ptype}"
        else:
            itype, severity, lost = random.choice(INCIDENTS)
            db.add(
                SafetyIncident(
                    project_id=project_id,
                    incident_type=itype,
                    zone=random.choice(ZONES),
                    severity=severity,
                    description=f"{itype.title()} reported to the supervisor.",
                    lost_days=lost,
                    incident_date=utcnow(),
                )
            )
            db.add(
                Alert(
                    project_id=project_id,
                    alert_type="incident",
                    severity="high" if severity != "minor" else "medium",
                    message=f"{itype.title()} reported on site.",
                    source_agent="safety_agent",
                )
            )
            message = f"incident · {itype} ({severity})"
        db.commit()
        return message
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream live site events into BuildSure AI")
    parser.add_argument("--interval", type=float, default=6.0, help="seconds between events")
    parser.add_argument("--project", type=int, default=0, help="project id, 0 = random across all projects")
    args = parser.parse_args()

    db = SessionLocal()
    project_ids = [p.project_id for p in db.query(Project).all()]
    db.close()
    if not project_ids:
        raise SystemExit("No projects found. Run: python -m app.seed")

    print(f"Streaming site events every {args.interval}s. Ctrl+C to stop.")
    try:
        while True:
            pid = args.project or random.choice(project_ids)
            print(f"[{utcnow():%H:%M:%S}] project {pid} · {emit(pid)}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()
