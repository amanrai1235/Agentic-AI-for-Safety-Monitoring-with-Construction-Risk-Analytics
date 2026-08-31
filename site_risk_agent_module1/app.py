
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="BuildSure AI — Site Risk Monitoring",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = Path(__file__).parent / "data" / "site_risk_data.csv"
df = pd.read_csv(DATA_PATH)

# ---------- Styling ----------
st.markdown("""
<style>
    .main { background: #f6f8fb; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    .hero {
        padding: 1.1rem 1.3rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #172033 0%, #263b5b 100%);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .35rem 0 0; color: #dce5f3; }
    .kpi {
        background: white;
        border: 1px solid #e7ebf1;
        border-radius: 12px;
        padding: 1rem;
        min-height: 112px;
        box-shadow: 0 2px 8px rgba(20,30,50,.04);
    }
    .kpi-label { color: #6b7280; font-size: .82rem; }
    .kpi-value { font-size: 1.75rem; font-weight: 700; margin-top: .2rem; }
    .kpi-note { color: #6b7280; font-size: .75rem; margin-top: .15rem; }
    .section-title { font-size: 1.15rem; font-weight: 700; margin: .4rem 0 .6rem; }
    .risk-high { color: #b42318; font-weight: 700; }
    .risk-medium { color: #b54708; font-weight: 700; }
    .risk-low { color: #027a48; font-weight: 700; }
    .footer { color: #7a8494; font-size: .75rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>🏗️ BuildSure AI — Site Risk Monitoring</h1>
    <p>Module 1 • Site Risk Agent • Construction Risk Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("Site Risk Agent")
st.sidebar.caption("Monitoring controls")

zones = ["All Zones"] + sorted(df["zone"].unique().tolist())
selected_zone = st.sidebar.selectbox("Site Zone", zones)

risk_types = ["All Types"] + sorted(df["risk_type"].unique().tolist())
selected_type = st.sidebar.selectbox("Risk Type", risk_types)

severity_filter = st.sidebar.multiselect(
    "Severity",
    ["High", "Medium", "Low"],
    default=["High", "Medium", "Low"]
)

filtered = df.copy()
if selected_zone != "All Zones":
    filtered = filtered[filtered["zone"] == selected_zone]
if selected_type != "All Types":
    filtered = filtered[filtered["risk_type"] == selected_type]
filtered = filtered[filtered["severity"].isin(severity_filter)]

# ---------- KPIs ----------
avg_score = round(filtered["risk_score"].mean()) if not filtered.empty else 0
active_risks = len(filtered)
high_risk_zones = filtered.loc[filtered["risk_score"] >= 75, "zone"].nunique()
hazards_detected = filtered["hazard"].nunique()

k1, k2, k3, k4 = st.columns(4)
for col, label, value, note in [
    (k1, "Active Risks", active_risks, "Detected site hazards"),
    (k2, "High-Risk Zones", high_risk_zones, "Score ≥ 75"),
    (k3, "Hazards Detected", hazards_detected, "Unique hazard events"),
    (k4, "Site Risk Score", f"{avg_score}/100", "Higher = more risk"),
]:
    col.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True
    )

st.write("")

# ---------- Charts ----------
left, right = st.columns([1.45, 1])

with left:
    st.markdown('<div class="section-title">Risk Monitoring by Zone</div>', unsafe_allow_html=True)
    zone_scores = (
        filtered.groupby("zone", as_index=False)["risk_score"]
        .mean()
        .sort_values("risk_score", ascending=False)
        .set_index("zone")
    )
    st.bar_chart(zone_scores, y="risk_score", use_container_width=True)

with right:
    st.markdown('<div class="section-title">Risk Distribution by Type</div>', unsafe_allow_html=True)
    type_counts = filtered["risk_type"].value_counts()
    st.bar_chart(type_counts, use_container_width=True)

# ---------- Heatmap-style matrix ----------
st.markdown('<div class="section-title">Site Risk Heatmap</div>', unsafe_allow_html=True)

if not filtered.empty:
    heat = filtered.pivot_table(
        index="zone",
        columns="risk_type",
        values="risk_score",
        aggfunc="mean"
    ).round(0)
    st.dataframe(
        heat.style.background_gradient(axis=None),
        use_container_width=True
    )
else:
    st.info("No risks match the selected filters.")

# ---------- Risk table ----------
st.markdown('<div class="section-title">Latest Detected Hazards</div>', unsafe_allow_html=True)

display_df = filtered.sort_values("risk_score", ascending=False).copy()
display_df["Risk Level"] = display_df["risk_score"].apply(
    lambda x: "HIGH" if x >= 75 else ("MEDIUM" if x >= 50 else "LOW")
)
display_df = display_df[
    ["risk_id", "zone", "activity", "hazard", "risk_type", "risk_score", "Risk Level", "detected_at"]
].rename(columns={
    "risk_id": "ID",
    "zone": "Zone",
    "activity": "Activity",
    "hazard": "Detected Hazard",
    "risk_type": "Risk Type",
    "risk_score": "Score",
    "detected_at": "Detected At"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

# ---------- Agent explanation ----------
st.markdown('<div class="section-title">Site Risk Agent Assessment</div>', unsafe_allow_html=True)

if not filtered.empty:
    top = filtered.sort_values("risk_score", ascending=False).iloc[0]
    level = "HIGH" if top["risk_score"] >= 75 else ("MEDIUM" if top["risk_score"] >= 50 else "LOW")
    st.warning(
        f"Priority hazard: **{top['hazard']}** in **{top['zone']}** "
        f"(risk score **{top['risk_score']}/100**, {level}). "
        f"Activity context: {top['activity']}."
    )
else:
    st.success("No hazards found for the selected filters.")

st.markdown(
    '<div class="footer">Prototype data for Module 1 demonstration • '
    'Site Risk Agent covers site conditions, environmental risks, equipment hazards, '
    'and site risk scoring.</div>',
    unsafe_allow_html=True
)
