# Agentic AI for Safety Monitoring with Construction Risk Analytics

## Project Overview

This project aims to develop an Agentic AI-powered Construction Risk Intelligence Platform for monitoring construction-site activities, identifying safety and operational risks, and providing actionable risk insights.

The platform follows a multi-agent approach where specialized AI agents handle different aspects of construction risk management.

## Project Modules

### 1. Site Risk Agent

The Site Risk Agent focuses on construction-site risk monitoring.

- Monitor construction site activities.
- Detect unsafe site conditions.
- Assess environmental risks.
- Identify equipment-related hazards.
- Generate site risk scores.

### 2. Safety Agent

The Safety Agent focuses on worker safety and protection.

- Monitor worker safety compliance.
- Detect PPE violations.
- Identify unsafe worker behavior.
- Analyze accident-prone zones.
- Generate safety recommendations.

### 3. Compliance Agent

The Compliance Agent will focus on regulatory and construction-standard compliance.

- Validate regulatory compliance.
- Monitor construction standards.
- Detect policy violations.
- Track inspection requirements.
- Generate compliance reports.

### 4. Insurance Agent

The Insurance Agent will focus on insurance-related construction risks.

- Assess insurance exposure.
- Evaluate incident severity.
- Analyze claim risks.
- Generate insurance risk scores.
- Support claim documentation.

### 5. Reporting Agent

The Reporting Agent will consolidate information from the different agents.

- Aggregate findings from all agents.
- Generate daily site reports.
- Produce executive risk summaries.
- Create audit-ready documentation.
- Generate project health reports.

### 6. Construction Risk Intelligence Engine

This will act as the central intelligence layer of the platform.

- Consolidate findings from all agents.
- Calculate project risk scores.
- Predict potential incidents.
- Identify recurring risk patterns.
- Generate operational recommendations.

### 7. Dashboard & Reporting Module

The platform will provide dashboards for:

- Construction Risk
- Safety
- Compliance
- Insurance
- Executive Project Monitoring

All dashboards are intended to be part of one integrated web application.

### 8. Notification & Workflow Module

The future notification and workflow system will support:

- Email notifications.
- SMS alerts.
- Teams/Slack notifications.
- Incident escalation.
- Risk mitigation workflows.

## Current Development Status

### Milestone 1 — Site Risk Monitoring & Hazard Detection

**Status: Completed**

Implemented features include:

- Site risk monitoring.
- Hazard detection and analysis.
- Risk scoring.
- Risk monitoring dashboard.
- Risk analysis by construction zone.
- Risk distribution by hazard type.
- Site risk heatmap.
- Risk filtering by zone, type, and severity.

### Milestone 2 — Safety Intelligence & Worker Protection

**Status: Integrated**

Implemented/planned capabilities include:

- Safety Agent.
- Worker safety monitoring.
- PPE compliance analysis.
- Worker safety risk analysis.
- Safety alerts.
- Safety analytics dashboard.

## Unified Application

Module 1 and Module 2 are integrated into a **single Streamlit web application**.

```text
                    BuildSure AI
                        │
              Unified Web Application
                        │
             ┌──────────┴──────────┐
             │                     │
       Site Risk Agent        Safety Agent
             │                     │
             └──────────┬──────────┘
                        │
              Future AI Agents
                        │
                        ▼
          Construction Risk Intelligence
                     Engine