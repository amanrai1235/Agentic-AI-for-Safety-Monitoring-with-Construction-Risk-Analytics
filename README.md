# Agentic AI for Safety Monitoring with Construction Risk Analytics

## Project Overview

This project aims to develop an Agentic AI-powered Construction Risk Intelligence Platform for monitoring construction-site activities, identifying safety and operational risks, and providing actionable risk insights.

The platform is designed as a multi-agent system where specialized AI agents handle different aspects of construction risk management.

## Project Modules

The platform is planned to include the following modules:

1. **Site Risk Agent**
   - Monitor construction site activities
   - Detect unsafe site conditions
   - Assess environmental risks
   - Identify equipment-related hazards
   - Generate site risk scores

2. **Safety Agent**
   - Monitor worker safety compliance
   - Detect PPE violations
   - Identify unsafe worker behavior
   - Analyze accident-prone zones
   - Generate safety recommendations

3. **Compliance Agent**
   - Validate regulatory compliance
   - Monitor construction standards
   - Detect policy violations
   - Track inspection requirements
   - Generate compliance reports

4. **Insurance Agent**
   - Assess insurance exposure
   - Evaluate incident severity
   - Analyze claim risks
   - Generate insurance risk scores

5. **Reporting Agent**
   - Aggregate findings from different agents
   - Generate site reports
   - Produce risk summaries
   - Create audit-ready documentation

6. **Construction Risk Intelligence Engine**
   - Consolidate agent findings
   - Calculate project risk scores
   - Identify recurring risk patterns
   - Generate operational recommendations

## Current Progress

### Milestone 1 — Site Risk Monitoring & Hazard Detection

The first module focuses on the **Site Risk Agent**.

Current implementation includes:

- Construction site risk monitoring
- Hazard identification
- Site-condition risk analysis
- Environmental risk analysis
- Equipment-related hazard identification
- Risk scoring
- Zone-wise risk analysis
- Risk distribution analysis
- Site risk heatmap
- Interactive monitoring dashboard

## Technology Stack

- **Python** — Application and risk-analysis logic
- **Pandas** — Data processing and analysis
- **Streamlit** — Interactive dashboard
- **Matplotlib** — Data visualization and heatmap support
- **CSV** — Current structured site-risk data source

## Project Structure

```text
Agentic-AI-for-Safety-Monitoring-with-Construction-Risk-Analytics/
│
├── site_risk_agent_module1/
│   ├── app.py
│   ├── README.md
│   ├── requirements.txt
│   │
│   └── data/
│       └── site_risk_data.csv
│
└── README.md
