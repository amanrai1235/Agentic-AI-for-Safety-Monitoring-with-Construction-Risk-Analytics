import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="BuildSure AI — Construction Risk Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).parent / "data"
site = pd.read_csv(BASE / "site_risk_data.csv")
safety = pd.read_csv(BASE / "worker_safety_data.csv")
compliance = pd.read_csv(BASE / "compliance_data.csv")

# ------------------ Styling ------------------
st.markdown("""
<style>
.stApp { background: #f5f7fb; }
.block-container { padding-top: 1.1rem; padding-bottom: 2rem; }
.hero {
    padding: 1.25rem 1.4rem;
    border-radius: 16px;
    background: linear-gradient(135deg,#172033 0%,#294a78 100%);
    color: white;
    margin-bottom: 1rem;
}
.hero h1 { margin: 0; font-size: 2rem; }
.hero p { margin: .35rem 0 0; color: #dbe7f7; }
.kpi {
    background: white;
    border: 1px solid #e3e8ef;
    border-radius: 14px;
    padding: 1rem;
    min-height: 110px;
}
.kpi-label { color:#667085; font-size:.82rem; }
.kpi-value { font-size:1.7rem; font-weight:750; margin-top:.2rem; }
.kpi-note { color:#667085; font-size:.74rem; margin-top:.15rem; }
.module-pill {
    display:inline-block; padding:.28rem .65rem; border-radius:999px;
    background:#eaf2ff; color:#245b9e; font-size:.78rem; font-weight:650;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar navigation ------------------
st.sidebar.title("BuildSure AI")
st.sidebar.caption("Construction Risk Intelligence Platform")

page = st.sidebar.radio(
    "Navigate",
    ["Executive Overview", "Module 1 — Site Risk", "Module 2 — Safety Intelligence", "Module 3 — Compliance Intelligence"]
)

st.sidebar.divider()
st.sidebar.caption("Current implementation: Modules 1–3")

# ------------------ Executive Overview ------------------
if page == "Executive Overview":
    st.markdown("""
    <div class="hero">
        <h1>🏗️ BuildSure AI</h1>
        <p>Agentic Construction Risk Intelligence Platform • Modules 1–3</p>
    </div>
    """, unsafe_allow_html=True)

    site_score = round(site["risk_score"].mean())
    safety_score = round(safety["safety_score"].mean())
    safety_violations = int((safety["compliance_status"] == "Violation").sum())
    ppe_compliance = round((1 - safety_violations / len(safety)) * 100) if len(safety) else 0
    compliance_ok = int((compliance["compliance_status"] == "Compliant").sum())
    compliance_rate = round((compliance_ok / len(compliance)) * 100) if len(compliance) else 0
    compliance_violations = int((compliance["compliance_status"] == "Violation").sum())
    pending_reviews = int((compliance["compliance_status"] == "Pending Review").sum())

    k1,k2,k3,k4,k5 = st.columns(5)
    for c,l,v,n in [
        (k1,"Site Risk Score",f"{site_score}/100","Module 1"),
        (k2,"Active Site Risks",len(site),"Module 1"),
        (k3,"Safety Violations",safety_violations,"Module 2"),
        (k4,"PPE Compliance",f"{ppe_compliance}%","Module 2"),
        (k5,"Compliance Score",f"{compliance_rate}%","Module 3"),
    ]:
        c.markdown(f'<div class="kpi"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-note">{n}</div></div>', unsafe_allow_html=True)

    st.subheader("Platform Modules")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.info("### Module 1 — Site Risk Agent\n\nSite-condition monitoring, environmental risk assessment, equipment hazard detection and site risk scoring.")
    with c2:
        st.info("### Module 2 — Safety Agent\n\nWorker safety compliance, PPE violation detection, unsafe behavior analysis, accident-prone zone analysis and safety recommendations.")
    with c3:
        st.info("### Module 3 — Compliance Agent\n\nRegulatory compliance validation, construction-standard monitoring, policy-violation detection, inspection tracking and compliance reporting.")

    st.subheader("Integrated Risk & Compliance View")
    combined = pd.DataFrame({
        "Metric": ["Site Risk Score","Safety Score","PPE Compliance","Compliance Score"],
        "Value": [site_score, safety_score, ppe_compliance, compliance_rate]
    }).set_index("Metric")
    st.bar_chart(combined)

# ------------------ Module 1 ------------------
elif page == "Module 1 — Site Risk":
    st.markdown("""
    <div class="hero">
        <span class="module-pill">MODULE 1</span>
        <h1>🏗️ Site Risk Monitoring</h1>
        <p>Site Risk Agent • Hazard Detection & Risk Scoring</p>
    </div>
    """, unsafe_allow_html=True)

    zones = ["All Zones"] + sorted(site.zone.unique())
    types = ["All Types"] + sorted(site.risk_type.unique())
    zone = st.sidebar.selectbox("Site Zone", zones)
    rtype = st.sidebar.selectbox("Risk Type", types)
    severity = st.sidebar.multiselect("Severity", ["High","Medium","Low"], ["High","Medium","Low"])

    f = site.copy()
    if zone != "All Zones": f = f[f.zone == zone]
    if rtype != "All Types": f = f[f.risk_type == rtype]
    f = f[f.severity.isin(severity)]

    avg = round(f.risk_score.mean()) if len(f) else 0
    high_zones = f.loc[f.risk_score >= 75, "zone"].nunique()

    k1,k2,k3,k4 = st.columns(4)
    for c,l,v,n in [
        (k1,"Active Risks",len(f),"Detected site hazards"),
        (k2,"High-Risk Zones",high_zones,"Score ≥ 75"),
        (k3,"Hazards Detected",f.hazard.nunique(),"Unique hazard events"),
        (k4,"Site Risk Score",f"{avg}/100","Higher = more risk"),
    ]:
        c.markdown(f'<div class="kpi"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-note">{n}</div></div>', unsafe_allow_html=True)

    a,b=st.columns([1.35,1])
    with a:
        st.subheader("Risk Monitoring by Zone")
        st.bar_chart(f.groupby("zone").risk_score.mean())
    with b:
        st.subheader("Risk Distribution by Type")
        st.bar_chart(f.risk_type.value_counts())

    st.subheader("Site Risk Heatmap")
    heat = f.pivot_table(index="zone", columns="risk_type", values="risk_score", aggfunc="mean").round(0)
    if not heat.empty:
        st.dataframe(heat.style.background_gradient(axis=None), use_container_width=True)
    else:
        st.info("No data for the selected filters.")

    st.subheader("Latest Detected Hazards")
    st.dataframe(f.sort_values("risk_score", ascending=False), use_container_width=True, hide_index=True)

    if len(f):
        top=f.sort_values("risk_score", ascending=False).iloc[0]
        st.warning(f"Priority hazard: **{top.hazard}** in **{top.zone}** — risk score **{top.risk_score}/100**.")

# ------------------ Module 2 ------------------
elif page == "Module 2 — Safety Intelligence":
    st.markdown("""
    <div class="hero">
        <span class="module-pill">MODULE 2</span>
        <h1>🦺 Safety Intelligence</h1>
        <p>Safety Agent • Worker Protection & PPE Compliance</p>
    </div>
    """, unsafe_allow_html=True)

    zones = ["All Zones"] + sorted(safety.zone.unique())
    ppes = ["All PPE Types"] + sorted(safety.ppe_type.unique())
    zone = st.sidebar.selectbox("Safety Zone", zones)
    ppe = st.sidebar.selectbox("PPE Type", ppes)
    status = st.sidebar.multiselect("Compliance Status", ["Compliant","Violation"], ["Compliant","Violation"])

    f=safety.copy()
    if zone != "All Zones": f=f[f.zone==zone]
    if ppe != "All PPE Types": f=f[f.ppe_type==ppe]
    f=f[f.compliance_status.isin(status)]

    violations=int((f.compliance_status=="Violation").sum())
    compliance=round((1-violations/len(f))*100) if len(f) else 0
    score=round(f.safety_score.mean()) if len(f) else 0

    k1,k2,k3,k4=st.columns(4)
    for c,l,v,n in [
        (k1,"Workers Monitored",f.worker_id.nunique(),"Workers in selected view"),
        (k2,"Safety Violations",violations,"PPE / behavior violations"),
        (k3,"PPE Compliance Rate",f"{compliance}%","Higher = better"),
        (k4,"Safety Score",f"{score}/100","Higher = safer"),
    ]:
        c.markdown(f'<div class="kpi"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-note">{n}</div></div>', unsafe_allow_html=True)

    a,b=st.columns([1.25,1])
    with a:
        st.subheader("PPE Compliance by Type")
        st.bar_chart(f.groupby(["ppe_type","compliance_status"]).size().unstack(fill_value=0))
    with b:
        st.subheader("Safety Violations by Zone")
        st.bar_chart(f[f.compliance_status=="Violation"].groupby("zone").size())

    st.subheader("Worker Safety Monitoring")
    m=f.copy()
    m["Risk Level"]=m.safety_score.apply(lambda x:"HIGH" if x<60 else ("MEDIUM" if x<80 else "LOW"))
    st.dataframe(m, use_container_width=True, hide_index=True)

    st.subheader("Safety Agent Assessment")
    v=f[f.compliance_status=="Violation"]
    if len(v):
        x=v.sort_values("safety_score").iloc[0]
        st.warning(f"Priority safety issue: **{x.violation_type}** for **{x.worker_id}** in **{x.zone}**. Safety score: **{x.safety_score}/100**.")
        st.info("Recommendation: verify required PPE, reinforce the relevant safety procedure, and review the zone for recurring unsafe behavior.")
    else:
        st.success("No safety violations found for the selected filters.")

# ------------------ Module 3 ------------------
else:
    st.markdown("""
    <div class="hero">
        <span class="module-pill">MODULE 3</span>
        <h1>📋 Compliance Intelligence</h1>
        <p>Compliance Agent • Regulatory Validation, Inspections & Policy Monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Demo mode: the compliance records below are structured demonstration data created for the Module 3 prototype. Replace them later with verified project/regulatory data.")

    regulations = ["All Regulations"] + sorted(compliance.regulation.unique())
    categories = ["All Categories"] + sorted(compliance.category.unique())
    statuses = ["Compliant", "Violation", "Pending Review"]
    zones = ["All Zones"] + sorted(compliance.zone.unique())

    c1, c2, c3, c4 = st.columns(4)
    with c1: reg = st.selectbox("Regulation", regulations)
    with c2: cat = st.selectbox("Compliance Category", categories)
    with c3: zone = st.selectbox("Site Zone", zones)
    with c4: status_filter = st.multiselect("Status", statuses, statuses)

    f = compliance.copy()
    if reg != "All Regulations": f = f[f.regulation == reg]
    if cat != "All Categories": f = f[f.category == cat]
    if zone != "All Zones": f = f[f.zone == zone]
    f = f[f.compliance_status.isin(status_filter)]

    total = len(f)
    compliant = int((f.compliance_status == "Compliant").sum())
    violations = int((f.compliance_status == "Violation").sum())
    pending = int((f.compliance_status == "Pending Review").sum())
    compliance_rate = round((compliant / total) * 100) if total else 0
    open_actions = int(f[f.action_required == "Yes"].shape[0]) if total else 0

    k1,k2,k3,k4,k5=st.columns(5)
    for c,l,v,n in [
        (k1,"Compliance Score",f"{compliance_rate}%","Higher = better"),
        (k2,"Open Violations",violations,"Policy / standard violations"),
        (k3,"Pending Reviews",pending,"Items awaiting validation"),
        (k4,"Inspections Tracked",int(f.inspection_required.sum()) if total else 0,"Inspection requirements"),
        (k5,"Open Actions",open_actions,"Items requiring action"),
    ]:
        c.markdown(f'<div class="kpi"><div class="kpi-label">{l}</div><div class="kpi-value">{v}</div><div class="kpi-note">{n}</div></div>', unsafe_allow_html=True)

    st.divider()
    a,b=st.columns([1.15,1])
    with a:
        st.subheader("Compliance Status by Category")
        status_chart = f.groupby(["category","compliance_status"]).size().unstack(fill_value=0) if total else pd.DataFrame()
        if not status_chart.empty:
            st.bar_chart(status_chart)
        else:
            st.info("No records match the selected filters.")
    with b:
        st.subheader("Inspection Tracking")
        inspection = f.groupby("inspection_status").size() if total else pd.Series(dtype=int)
        if not inspection.empty:
            st.bar_chart(inspection)
        else:
            st.info("No inspection records match the selected filters.")

    st.subheader("Compliance Overview")
    overview = f.groupby("category").agg(
        Requirements=("requirement","count"),
        Compliant=("compliance_status", lambda x: (x=="Compliant").sum()),
        Violations=("compliance_status", lambda x: (x=="Violation").sum()),
        Pending=("compliance_status", lambda x: (x=="Pending Review").sum()),
    ).reset_index()
    if not overview.empty:
        overview["Compliance %"] = (overview["Compliant"] / overview["Requirements"] * 100).round(0).astype(int)
        st.dataframe(overview, use_container_width=True, hide_index=True)

    st.subheader("Policy Violations & Required Actions")
    issues = f[f.compliance_status != "Compliant"].copy()
    if not issues.empty:
        issues = issues.sort_values(["priority","due_date"], ascending=[True, True])
        st.dataframe(issues[["requirement","regulation","category","zone","compliance_status","inspection_status","priority","action_required","due_date"]], use_container_width=True, hide_index=True)
    else:
        st.success("No violations or pending reviews found for the selected filters.")

    st.subheader("Inspection Requirements")
    inspection_df = f[f.inspection_required].copy()
    if not inspection_df.empty:
        st.dataframe(inspection_df[["requirement","zone","inspection_status","last_inspection","next_inspection","inspection_owner"]], use_container_width=True, hide_index=True)
    else:
        st.info("No inspection requirements found for the selected filters.")

    st.subheader("Compliance Agent Assessment")
    if not issues.empty:
        critical = issues.sort_values("priority").iloc[0]
        if critical["compliance_status"] == "Violation":
            st.error(f"Priority violation: **{critical.requirement}** in **{critical.zone}**. Action required: **{critical.action_required}** by **{critical.due_date}**.")
        else:
            st.warning(f"Priority review: **{critical.requirement}** in **{critical.zone}** is **Pending Review**. Validate the requirement and close the inspection workflow.")
        st.info("Compliance Agent workflow: validate the requirement → identify the status → track inspection → flag violations → record the corrective action → generate the compliance report.")
    else:
        st.success("All selected compliance requirements are currently marked compliant.")

    st.subheader("Generate Compliance Report")
    report = f.copy()
    if not report.empty:
        report_cols=["requirement","regulation","category","zone","compliance_status","inspection_status","priority","action_required","due_date"]
        st.download_button("⬇️ Download Filtered Compliance Report (CSV)", report[report_cols].to_csv(index=False), "buildsure_compliance_report.csv", "text/csv")
    else:
        st.button("⬇️ Download Filtered Compliance Report (CSV)", disabled=True)

st.caption("BuildSure AI • Unified dashboard for Modules 1, 2 and 3. Data shown is structured demonstration data.")
