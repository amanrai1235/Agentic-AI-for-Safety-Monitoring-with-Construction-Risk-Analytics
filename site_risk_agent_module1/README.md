# BuildSure AI — Site Risk Agent (Module 1)

A Streamlit prototype for Milestone 1 of the Agentic Construction Risk Intelligence Platform.

## Module 1 scope
- Monitor construction site activities
- Detect unsafe site conditions
- Assess environmental risks
- Identify equipment-related hazards
- Generate site risk scores
- Provide a site risk monitoring dashboard

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Data
`data/site_risk_data.csv` contains demonstration construction-site observations. Replace it later with the selected Kaggle/site-monitoring dataset.

## Important
This is a Module 1 prototype. The current risk score is demonstration logic; later it can be replaced with a trained ML model and/or an agentic workflow.
