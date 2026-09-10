# BuildSure AI — Construction Risk Intelligence Platform

Integrated Streamlit website containing the current project modules.

## Implemented
- Module 1 — Site Risk Agent
- Module 2 — Safety Agent
- Module 3 — Compliance Agent

## Run
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

The sidebar provides one website with:
- Executive Overview
- Module 1 — Site Risk
- Module 2 — Safety Intelligence
- Module 3 — Compliance Intelligence

The current data files are structured demonstration data. They can later be replaced with the selected real/Kaggle datasets while keeping the same dashboard architecture.


### Module 3 — Compliance Intelligence
The Compliance Agent prototype validates structured compliance requirements, monitors construction standards, flags policy violations, tracks inspection requirements, and supports filtered compliance-report export. The included `data/compliance_data.csv` is demonstration data and should be replaced with verified project/regulatory records for production use.
