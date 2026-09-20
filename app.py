import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(
    page_title="US HR Operations & Workforce Compliance Suite",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Styling
st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .metric-card {
        background-color: #151b28;
        border: 1px solid #232d42;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.25);
    }
    .metric-title { color: #8fa0bd; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-val { color: #ffffff; font-size: 26px; font-weight: 700; margin: 4px 0; }
    .metric-sub { font-size: 12px; font-weight: 500; }
    .status-positive { color: #10b981; }
    .status-negative { color: #ef4444; }
    .header-box {
        padding: 8px 0 18px 0;
        border-bottom: 1px solid #232d42;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Synthetic US HR Operations Data Generator
@st.cache_data
def generate_hr_ops_data():
    np.random.seed(42)
    categories = [
        "Time & Attendance (Punch/Shift Audit)",
        "Onboarding & Employee Records Verification",
        "US Leave Administration (FMLA/Disability)",
        "Case Lifecycle & Referral Triage",
        "HR Policy & Workplace Compliance"
    ]
    tiers = ["Tier 1 (Core Resolution)", "Tier 2 (Specialist Review)", "Tier 3 (Lead Escalation)"]
    channels = ["MHLS Portal / Ticket Ingestion", "Shared Operations Inbox", "Urgent Escalation Queue"]
    teams = ["US HR Shared Services", "Workforce Triage Team", "HR Leave & Attendance Ops"]
    states = ["California", "New York", "Texas", "Washington", "Florida", "Illinois"]
    audit_verdicts = ["Verified & Compliant", "Exception Resolved", "Pending Documentation", "Escalated for Audit"]

    data = []
    base_date = datetime.now() - timedelta(days=45)

    for i in range(1, 451):
        created_at = base_date + timedelta(
            days=np.random.randint(0, 45),
            hours=np.random.randint(8, 20),
            minutes=np.random.randint(0, 59)
        )
        cat = np.random.choice(categories, p=[0.30, 0.25, 0.20, 0.15, 0.10])
        tier = np.random.choice(tiers, p=[0.55, 0.35, 0.10])
        
        # Turnaround modeling based on category complexity
        base_time = 8.0 if "Attendance" in cat else (14.0 if "Onboarding" in cat else 22.0)
        turnaround = max(1.2, np.random.normal(loc=base_time, scale=base_time * 0.4))
        sla_target = 24.0  # Standard 24h SLA target
        
        is_breached = turnaround > sla_target
        sla_status = "Breached" if is_breached else "Met"
        status = np.random.choice(audit_verdicts, p=[0.65, 0.20, 0.10, 0.05])
        
        data.append({
            "Case_ID": f"HROPS-{30200 + i}",
            "Date": created_at.date(),
            "Category": cat,
            "US_State": np.random.choice(states),
            "Support_Tier": tier,
            "Intake_Channel": np.random.choice(channels),
            "Assigned_Queue": np.random.choice(teams),
            "Turnaround_Hours": round(turnaround, 1),
            "SLA_Target": sla_target,
            "SLA_Performance": sla_status,
            "Audit_Status": status,
            "Aging_Bracket": "0-12 hrs" if turnaround <= 12 else ("13-24 hrs" if turnaround <= 24 else ("25-48 hrs" if turnaround <= 48 else "48+ hrs"))
        })
    return pd.DataFrame(data)

df_raw = generate_hr_ops_data()

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown("### 🗂️ **US HR Queue Filters**")
    st.caption("Filter live operational cases and audit trails")

    min_date = df_raw["Date"].min()
    max_date = df_raw["Date"].max()
    date_selection = st.date_input("Date Horizon", (min_date, max_date), min_value=min_date, max_value=max_date)

    selected_categories = st.multiselect("Operational Workstream", options=df_raw["Category"].unique(), default=df_raw["Category"].unique())
    selected_queues = st.multiselect("Assigned Queue", options=df_raw["Assigned_Queue"].unique(), default=df_raw["Assigned_Queue"].unique())
    selected_sla = st.multiselect("SLA Status", options=["Met", "Breached"], default=["Met", "Breached"])

    st.markdown("---")
    st.caption("Engineered for US Workforce Compliance, Timecard Audits & Case Lifecycle.")

# Apply Filters
if isinstance(date_selection, tuple) and len(date_selection) == 2:
    start_d, end_d = date_selection
else:
    start_d, end_d = min_date, max_date

filtered_df = df_raw[
    (df_raw["Date"] >= start_d) &
    (df_raw["Date"] <= end_d) &
    (df_raw["Category"].isin(selected_categories)) &
    (df_raw["Assigned_Queue"].isin(selected_queues)) &
    (df_raw["SLA_Performance"].isin(selected_sla))
]

# ----------------- HEADER -----------------
st.markdown("""
<div class="header-box">
    <h2 style="margin: 0; font-weight: 700; color: #f8fafc;">💼 US HR Operations & Workforce Compliance Suite</h2>
    <p style="margin: 4px 0 0 0; color: #8fa0bd; font-size: 14px;">Time & Attendance Ingestion | Employee Records & Onboarding Verification | US Leave (FMLA) | SLA Triage</p>
</div>
""", unsafe_allow_html=True)

# ----------------- TOP METRICS -----------------
total_cases = len(filtered_df)
met_cases = len(filtered_df[filtered_df["SLA_Performance"] == "Met"])
sla_rate = round((met_cases / total_cases * 100), 1) if total_cases > 0 else 0.0
avg_tat = round(filtered_df["Turnaround_Hours"].mean(), 1) if total_cases > 0 else 0.0
pending_audits = len(filtered_df[filtered_df["Audit_Status"].isin(["Pending Documentation", "Escalated for Audit"])])

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Cases Audited</div>
        <div class="metric-val">{total_cases:,}</div>
        <div class="metric-sub status-positive">Active Queue Records</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    sla_color = "status-positive" if sla_rate >= 92.0 else "status-negative"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">24-Hr SLA Adherence</div>
        <div class="metric-val">{sla_rate}%</div>
        <div class="metric-sub {sla_color}">Enterprise Target: 92.0%</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Mean Turnaround Time</div>
        <div class="metric-val">{avg_tat} hrs</div>
        <div class="metric-sub status-positive">Benchmark: &lt; 24.0 hrs</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Pending Exceptions / Audits</div>
        <div class="metric-val">{pending_audits}</div>
        <div class="metric-sub status-negative">Documentation / Escalations</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- TABS -----------------
tab1, tab2, tab3 = st.tabs(["📊 Operational Workstreams", "⏱️ SLA Aging & Turnaround Analysis", "📋 Compliance Records & Export"])

with tab1:
    col_left, col_right = st.columns((3, 2))
    
    with col_left:
        fig_cat = px.histogram(
            filtered_df,
            y="Category",
            color="SLA_Performance",
            orientation="h",
            barmode="stack",
            title="<b>Volume & SLA Compliance by HR Workstream</b>",
            color_discrete_map={"Met": "#10b981", "Breached": "#ef4444"},
            template="plotly_dark"
        )
        fig_cat.update_layout(margin=dict(l=10, r=10, t=40, b=10), yaxis_title=None, xaxis_title="Total Case Records")
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        status_data = filtered_df["Audit_Status"].value_counts().reset_index()
        status_data.columns = ["Audit_Status", "Count"]
        fig_pie = px.pie(
            status_data,
            values="Count",
            names="Audit_Status",
            hole=0.55,
            title="<b>Audit Verification Status</b>",
            color_discrete_sequence=["#2563eb", "#10b981", "#f59e0b", "#ef4444"],
            template="plotly_dark"
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    c_a, c_b = st.columns(2)
    
    with c_a:
        fig_box = px.box(
            filtered_df,
            x="Support_Tier",
            y="Turnaround_Hours",
            color="Support_Tier",
            title="<b>Turnaround Time Variance by Support Complexity Tier</b>",
            color_discrete_sequence=["#38bdf8", "#818cf8", "#f472b6"],
            template="plotly_dark"
        )
        fig_box.add_hline(y=24.0, line_dash="dash", line_color="#ef4444", annotation_text="24h SLA Target")
        fig_box.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    with c_b:
        aging_order = ["0-12 hrs", "13-24 hrs", "25-48 hrs", "48+ hrs"]
        fig_aging = px.histogram(
            filtered_df,
            x="Aging_Bracket",
            category_orders={"Aging_Bracket": aging_order},
            color="SLA_Performance",
            title="<b>Queue Aging Distribution & Backlog Exposure</b>",
            color_discrete_map={"Met": "#10b981", "Breached": "#ef4444"},
            template="plotly_dark"
        )
        fig_aging.update_layout(margin=dict(l=10, r=10, t=40, b=10), xaxis_title="Resolution Bracket", yaxis_title="Cases")
        st.plotly_chart(fig_aging, use_container_width=True)

with tab3:
    st.markdown("#### **Audit Log & Records Inspection**")
    display_columns = ["Case_ID", "Date", "Category", "US_State", "Support_Tier", "Turnaround_Hours", "SLA_Performance", "Audit_Status"]
    st.dataframe(filtered_df[display_columns].sort_values(by="Date", ascending=False), use_container_width=True, height=340)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export HR Operations Audit Trail (CSV)",
        data=csv_data,
        file_name=f"us_hr_ops_audit_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
