"""Seed the database with realistic multi-project construction site data."""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from .database import Base, SessionLocal, engine
from .models import (
    Alert,
    ComplianceCheck,
    InsuranceCase,
    PPEViolation,
    Project,
    SafetyIncident,
    SiteRisk,
)
from .utils import utcnow

random.seed(11)

PROJECTS = [
    {
        "project_name": "Meridian Tower — Phase 2",
        "location": "Sector 62, Noida",
        "contractor": "Larsen Infra Works",
        "workers_on_site": 342,
        "status": "active",
    },
    {
        "project_name": "Yamuna Expressway Interchange",
        "location": "Jewar, Uttar Pradesh",
        "contractor": "Bharat Highways Ltd",
        "workers_on_site": 218,
        "status": "active",
    },
    {
        "project_name": "Prayagraj Metro Depot",
        "location": "Naini, Prayagraj",
        "contractor": "Ganga Rail Constructions",
        "workers_on_site": 156,
        "status": "active",
    },
]

RISKS = [
    ("fall hazard", "Level 14 slab edge", "Edge protection missing on the east slab edge during shuttering.", 4, 5, "cctv"),
    ("equipment risk", "Crane bay A", "Tower crane load chart exceeded twice during the morning lift.", 3, 5, "site inspection"),
    ("electrical hazard", "Basement B2", "Temporary distribution board left open next to standing water.", 4, 4, "inspection report"),
    ("environmental risk", "South stockyard", "Dust levels above permissible limits on three consecutive readings.", 3, 2, "sensor"),
    ("structural risk", "Core wall grid C4", "Formwork deflection observed beyond tolerance after the pour.", 2, 5, "engineer review"),
    ("excavation risk", "North trench", "Trench face unshored beyond 1.5 m depth.", 4, 5, "cctv"),
    ("fall hazard", "Scaffold tower 3", "Two missing guardrails on the fourth lift.", 3, 4, "cctv"),
    ("equipment risk", "Batching plant", "Conveyor guard removed for maintenance and not refitted.", 3, 3, "site inspection"),
    ("environmental risk", "Access road", "Surface water pooling near the site entry after overnight rain.", 2, 2, "sensor"),
    ("fall hazard", "Lift shaft 2", "Shaft opening cover displaced by material movement.", 4, 5, "cctv"),
    ("electrical hazard", "Tower A riser", "Cable joints taped rather than terminated in an enclosure.", 3, 4, "inspection report"),
    ("equipment risk", "Hoist 1", "Overload alarm bypassed by the operator.", 3, 4, "site inspection"),
]

PPE_TYPES = ["hard hat", "safety vest", "safety boots", "protective gloves", "fall harness"]
ZONES = ["Level 14 slab edge", "Crane bay A", "Basement B2", "North trench", "Scaffold tower 3", "Batching plant"]

REGULATIONS = [
    ("Fall protection above 1.8 m", "OSHA standards"),
    ("Scaffold inspection register", "OSHA standards"),
    ("Hot work permit system", "OSHA standards"),
    ("Structural load test certificate", "Building codes"),
    ("Fire egress and stair pressurisation", "Building codes"),
    ("Occupancy load documentation", "Building codes"),
    ("Dust suppression compliance", "Environmental regulations"),
    ("Construction debris disposal log", "Environmental regulations"),
    ("Noise limit adherence (day works)", "Environmental regulations"),
    ("Workmen compensation policy validity", "Insurance requirements"),
    ("Contractor all-risk policy endorsement", "Insurance requirements"),
    ("Third-party liability certificate", "Insurance requirements"),
]

CLAIMS = [
    ("Worker injury — fall from height", 285_000, "open", "incomplete"),
    ("Equipment damage — crane boom", 142_000, "under review", "complete"),
    ("Third-party property damage", 68_500, "open", "incomplete"),
    ("Material theft", 24_000, "settled", "complete"),
    ("Water ingress — basement", 96_000, "under review", "complete"),
]

INCIDENT_TYPES = [
    ("slip and fall", "minor", 1),
    ("struck by object", "moderate", 4),
    ("electrical shock", "major", 9),
    ("manual handling injury", "minor", 2),
    ("scaffold collapse (near miss)", "moderate", 0),
    ("vehicle reversing incident", "moderate", 3),
]


def seed(reset: bool = True) -> None:
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    if db.query(Project).count():
        db.close()
        print("Database already seeded — skipping.")
        return

    now = utcnow()
    for index, spec in enumerate(PROJECTS):
        project = Project(**spec, start_date=now - timedelta(days=120 + index * 45))
        db.add(project)
        db.flush()

        risk_sample = RISKS if index == 0 else random.sample(RISKS, 7 - index)
        for risk_type, zone, description, prob, impact, source in risk_sample:
            exposure = prob * impact
            severity = "critical" if exposure >= 17 else "high" if exposure >= 11 else "medium" if exposure >= 6 else "low"
            db.add(
                SiteRisk(
                    project_id=project.project_id,
                    risk_type=risk_type,
                    zone=zone,
                    description=description,
                    probability=prob,
                    impact=impact,
                    severity=severity,
                    status=random.choice(["open", "open", "open", "mitigating", "closed"]),
                    mitigation="Mitigation assigned to zone supervisor." if random.random() > 0.5 else "",
                    source=source,
                    detected_at=now - timedelta(days=random.randint(0, 9), hours=random.randint(0, 20)),
                )
            )

        violation_count = [46, 28, 19][index]
        for n in range(violation_count):
            db.add(
                PPEViolation(
                    project_id=project.project_id,
                    worker_id=f"W-{project.project_id}{n:03d}",
                    violation_type=random.choices(PPE_TYPES, weights=[4, 5, 3, 6, 2])[0],
                    zone=random.choice(ZONES),
                    confidence=round(random.uniform(0.74, 0.99), 2),
                    resolved=random.random() > 0.45,
                    timestamp=now - timedelta(days=random.randint(0, 29), hours=random.randint(0, 23)),
                )
            )

        for n in range([9, 6, 4][index]):
            itype, severity, lost = random.choice(INCIDENT_TYPES)
            db.add(
                SafetyIncident(
                    project_id=project.project_id,
                    incident_type=itype,
                    zone=random.choice(ZONES),
                    severity=severity,
                    description=f"{itype.title()} reported by the zone supervisor and logged for investigation.",
                    lost_days=lost,
                    incident_date=now - timedelta(days=random.randint(0, 28)),
                )
            )

        for name, category in REGULATIONS:
            status = random.choices(
                ["compliant", "compliant", "compliant", "compliant", "pending", "violation"],
                weights=[5, 5, 5, 5, 2, 1],
            )[0]
            db.add(
                ComplianceCheck(
                    project_id=project.project_id,
                    regulation_name=name,
                    category=category,
                    compliance_status=status,
                    finding="" if status == "compliant" else f"{name} could not be verified at the last inspection.",
                    due_date=now + timedelta(days=random.randint(-6, 21)) if status != "compliant" else None,
                    checked_at=now - timedelta(days=random.randint(1, 20)),
                )
            )

        for claim_type, cost, status, doc in random.sample(CLAIMS, 4 - index if index < 3 else 2):
            db.add(
                InsuranceCase(
                    project_id=project.project_id,
                    claim_type=claim_type,
                    description=f"{claim_type} reported on site and forwarded to the broker.",
                    estimated_cost=cost,
                    status=status,
                    documentation_status=doc,
                    created_at=now - timedelta(days=random.randint(3, 80)),
                )
            )

        db.add(
            Alert(
                project_id=project.project_id,
                alert_type="site_risk",
                severity="high",
                message=f"Open hazard backlog reviewed for {project.project_name}.",
                source_agent="site_risk_agent",
            )
        )

    db.commit()
    db.close()
    print(f"Seeded {len(PROJECTS)} projects with site, safety, compliance and insurance data.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the BuildSure AI database")
    parser.add_argument("--reset", action="store_true", help="wipe existing data first")
    seed(reset=parser.parse_args().reset)
