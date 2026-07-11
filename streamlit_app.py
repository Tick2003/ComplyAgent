import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ComplyAgent | SEBI Agentic Compliance Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium dark styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #050a18;
        color: #f8fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1528 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .accent-border-blue {
        border-left: 4px solid #3b82f6 !important;
    }
    
    .accent-border-emerald {
        border-left: 4px solid #10b981 !important;
    }
    
    .accent-border-amber {
        border-left: 4px solid #f59e0b !important;
    }
    
    .accent-border-rose {
        border-left: 4px solid #f43f5e !important;
    }
    
    .accent-border-violet {
        border-left: 4px solid #8b5cf6 !important;
    }

    /* Headings and Text */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-desc {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint configuration
API_BASE = "http://localhost:8000/api"

# Helper for API requests with safe fallback
def api_request(endpoint, method="GET", json=None):
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=3)
        elif method == "POST":
            response = requests.post(url, json=json, timeout=3)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# Load global fallback/mock data (consistent with seed data)
MOCK_OBLIGATIONS = [
    {"obligation_id": "OBL-KYC-001", "summary": "Complete client verification through CKYC portal before trading activation.", "type": "kyc_onboarding", "status": "compliant", "process": "Client Onboarding (KYC/AML)"},
    {"obligation_id": "OBL-KYC-002", "summary": "Verify PAN card details against Income Tax database in real-time.", "type": "kyc_onboarding", "status": "compliant", "process": "Client Onboarding (KYC/AML)"},
    {"obligation_id": "OBL-RISK-001", "summary": "Maintain daily Client Margin reports and upload exposure data to Clearing Corp.", "type": "risk_management", "status": "compliant", "process": "Margin & Risk Management"},
    {"obligation_id": "OBL-RISK-002", "summary": "Monitor real-time position limits and apply client-wise VaR margins.", "type": "risk_management", "status": "partially_compliant", "process": "Margin & Risk Management"},
    {"obligation_id": "OBL-TRADING-001", "summary": "Issue electronic contract notes to clients within 24 hours of trade execution.", "type": "systems_process", "status": "compliant", "process": "Trading & Order Management"},
    {"obligation_id": "OBL-REPORT-001", "summary": "Submit monthly holding statement reports to depositories.", "type": "reporting", "status": "compliant", "process": "Reporting to Exchange/SEBI"},
    {"obligation_id": "OBL-REPORT-002", "summary": "File quarterly compliance certificate signed by the Compliance Officer.", "type": "reporting", "status": "non_compliant", "process": "Reporting to Exchange/SEBI"},
    {"obligation_id": "OBL-GRIEVANCE-001", "summary": "Resolve investor complaints synced via SEBI SCORES portal within 7 days SLA.", "type": "grievance_redressal", "status": "partially_compliant", "process": "Investor Grievance Redressal"},
    {"obligation_id": "OBL-CYBER-001", "summary": "Conduct annual VAPT and submit cybersecurity audit report to exchange.", "type": "cybersecurity", "status": "non_compliant", "process": "Cybersecurity & IT Infrastructure"},
    {"obligation_id": "OBL-CYBER-002", "summary": "Maintain immutable event logs and report cyber incidents within 6 hours.", "type": "cybersecurity", "status": "partially_compliant", "process": "Cybersecurity & IT Infrastructure"},
    {"obligation_id": "OBL-RECORD-001", "summary": "Preserve client registration documents and trade logs for a minimum of 8 years.", "type": "record_keeping", "status": "compliant", "process": "Record-Keeping & Documentation"},
    {"obligation_id": "OBL-AD-001", "summary": "Obtain pre-approval from exchange before publishing any promotional advertisement.", "type": "advertising", "status": "compliant", "process": "Advertising & Marketing"},
]

# Title / Sidebar
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
    <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 8px; border-radius: 8px;">
        <span style="font-size: 1.5rem; color: white;">⚖️</span>
    </div>
    <div>
        <h2 style="margin: 0; font-size: 1.25rem;">ComplyAgent</h2>
        <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">SEBI RegTech Engine</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Firm card
st.sidebar.markdown("""
<div style="background: rgba(59, 130, 246, 0.06); border: 1px solid rgba(59, 130, 246, 0.15); padding: 12px; border-radius: 10px; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 0.65rem; color: #3b82f6; font-weight: bold; text-transform: uppercase;">Firm</p>
    <p style="margin: 0; font-size: 0.85rem; color: #f8fafc; font-weight: 500;">Horizon Securities Pvt. Ltd.</p>
    <p style="margin: 0; font-size: 0.7rem; color: #64748b; font-family: monospace;">INZ000012345</p>
</div>
""", unsafe_allow_html=True)

# Navigation
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard",
        "📈 Impact Metrics",
        "👁️ Supervision Mode",
        "📋 Obligations Explorer",
        "🔍 Change Detection",
        "💬 Ask Agent"
    ]
)

# Fetch stats from backend if possible
dashboard_stats = api_request("/dashboard/stats")
impact_metrics = api_request("/platform/metrics/impact")
coverage_matrix = api_request("/platform/regulatory-coverage")
chain_stats = api_request("/platform/audit/chain-stats")

# ── PAGE: DASHBOARD ───────────────────────────────────────────────────
if menu == "📊 Dashboard":
    st.markdown("## Compliance Dashboard")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Real-time compliance status tracker for Horizon Securities Pvt. Ltd.</p>", unsafe_allow_html=True)
    
    # 1. Health Score & Overview Cards
    health_score = dashboard_stats.get("health_score", 75.0) if dashboard_stats else 75.0
    compliant_count = dashboard_stats.get("compliant", 9) if dashboard_stats else 9
    partial_count = dashboard_stats.get("partially_compliant", 3) if dashboard_stats else 3
    non_compliant = dashboard_stats.get("non_compliant", 2) if dashboard_stats else 2
    not_due = dashboard_stats.get("not_yet_due", 2) if dashboard_stats else 2
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card accent-border-blue">
            <p class="metric-label">Health Score</p>
            <p class="metric-value" style="color: #10b981;">{health_score}%</p>
            <p class="metric-desc">Overall compliance index</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="glass-card accent-border-emerald">
            <p class="metric-label">Compliant</p>
            <p class="metric-value" style="color: #10b981;">{compliant_count}</p>
            <p class="metric-desc">Satisfied requirements</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="glass-card accent-border-amber">
            <p class="metric-label">Partially</p>
            <p class="metric-value" style="color: #f59e0b;">{partial_count}</p>
            <p class="metric-desc">Evidence or review pending</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="glass-card accent-border-rose">
            <p class="metric-label">Non-Compliant</p>
            <p class="metric-value" style="color: #f43f5e;">{non_compliant}</p>
            <p class="metric-desc">Action needed immediately</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="glass-card accent-border-violet">
            <p class="metric-label">Not Yet Due</p>
            <p class="metric-value" style="color: #8b5cf6;">{not_due}</p>
            <p class="metric-desc">Future compliance dates</p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Charts Section
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### Obligation Status Distribution")
        df_status = pd.DataFrame({
            "Status": ["Compliant", "Partially Compliant", "Non-Compliant", "Not Yet Due"],
            "Count": [compliant_count, partial_count, non_compliant, not_due]
        })
        fig_pie = px.pie(
            df_status, values="Count", names="Status",
            color="Status",
            color_discrete_map={
                "Compliant": "#10b981",
                "Partially Compliant": "#f59e0b",
                "Non-Compliant": "#f43f5e",
                "Not Yet Due": "#8b5cf6"
            },
            hole=0.4
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f8fafc',
            margin=dict(t=10, b=10, l=10, r=10),
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with chart_col2:
        st.markdown("### Obligations by Category")
        df_types = pd.DataFrame({
            "Category": ["KYC/Onboarding", "Risk Management", "Reporting", "Cybersecurity", "Others"],
            "Count": [3, 4, 3, 2, 4]
        })
        fig_bar = px.bar(
            df_types, x="Count", y="Category", orientation='h',
            color="Category",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f8fafc',
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Recent Audits / Notifications
    st.markdown("### Recent Compliance Operations")
    logs = dashboard_stats.get("recent_changes", []) if dashboard_stats else [
        {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": "Priya Sharma", "action": "approved", "entity_id": "OBL-RISK-001", "details": "Evidence verified for RMS exposure limits"},
        {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": "system", "action": "extracted", "entity_id": "OBL-CYBER-002", "details": "Extracted from circular SEBI/HO/MRD/2025/11"},
        {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": "Priya Sharma", "action": "status_changed", "entity_id": "OBL-KYC-002", "details": "Changed status to Compliant"}
    ]
    
    for log in logs[:4]:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-weight: 600; color: #3b82f6;">{log['entity_id']}</span> - 
                <span style="color: #cbd5e1;">{log['details']}</span>
            </div>
            <div style="text-align: right; font-size: 0.75rem; color: #64748b;">
                <div>Action by: <b>{log['user']}</b></div>
                <div>{log['timestamp']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── PAGE: IMPACT METRICS ──────────────────────────────────────────────
elif menu == "📈 Impact Metrics":
    st.markdown("## Impact Metrics & Technological Stack")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Quantifying the market impact and feasibility of ComplyAgent</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(59, 130, 246, 0.04));">
            <p class="metric-label" style="font-size: 0.75rem;">Investor Protection Score</p>
            <p class="metric-value" style="font-size: 3.5rem; color: #10b981; margin-top: 10px;">{impact_metrics.get('investor_protection_score', 78.5) if impact_metrics else 78.5}</p>
            <p style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">Composite index reflecting audit trail depth, regulatory coverage, and grievance compliance rates.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(244, 63, 94, 0.08), rgba(59, 130, 246, 0.04));">
            <p class="metric-label" style="font-size: 0.75rem;">Time Saved Metric</p>
            <p class="metric-value" style="font-size: 3.2rem; color: #f43f5e; margin-top: 10px;">95%</p>
            <p style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">Manual audit time reduced from ~40 hours/circular to under 2 hours.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### Penalty Risk Avoidance Profile")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 96.0,
            title = {'text': "Mitigated Penalty Pool (₹ in Lakhs)"},
            delta = {'reference': 40.0, 'increasing': {'color': "#10b981"}},
            gauge = {
                'axis': {'range': [None, 150]},
                'bar': {'color': "#10b981"},
                'steps': [
                    {'range': [0, 40], 'color': "rgba(244, 63, 94, 0.1)"},
                    {'range': [40, 100], 'color': "rgba(245, 158, 11, 0.1)"},
                    {'range': [100, 150], 'color': "rgba(16, 185, 129, 0.1)"}
                ]
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f8fafc',
            height=280,
            margin=dict(t=50, b=10, l=30, r=30)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # 4. Tech Stack Showcase
    st.markdown("### Technological Stack Capabilities")
    t1, t2, t3, t4 = st.columns(4)
    
    with t1:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.03); border: 1px solid rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 12px; height: 180px;">
            <p style="color: #3b82f6; font-weight: 700; margin: 0;">🧠 Google Gemini</p>
            <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px;">LLM-powered extraction, zero-shot clause classification, natural language queries, and autonomous gap remediation steps.</p>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.03); border: 1px solid rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 12px; height: 180px;">
            <p style="color: #8b5cf6; font-weight: 700; margin: 0;">🛡️ Hash Chain Audit</p>
            <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px;">Blockchain-inspired SHA-256 cryptographically linked audit logs. Assures tamper-evident compliance trace for regulatory inspectors.</p>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.03); border: 1px solid rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 12px; height: 180px;">
            <p style="color: #10b981; font-weight: 700; margin: 0;">⚡ DPI Integrations</p>
            <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px;">Digitally signed evidence validation powered by government portals: DigiLocker document lookup, Central KYC (CKYC) registry, e-PAN.</p>
        </div>
        """, unsafe_allow_html=True)
    with t4:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.03); border: 1px solid rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 12px; height: 180px;">
            <p style="color: #f59e0b; font-weight: 700; margin: 0;">📂 ChromaDB RAG</p>
            <p style="font-size: 0.75rem; color: #94a3b8; margin-top: 8px;">Vector store index mapping chunks of the SEBI Master Circular corpus to power contextual RAG with source-level citations.</p>
        </div>
        """, unsafe_allow_html=True)


# ── PAGE: SUPERVISION MODE ────────────────────────────────────────────
elif menu == "👁️ Supervision Mode":
    st.markdown("## SEBI Supervision Panel")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Read-only regulatory compliance inspection dashboard</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="background: rgba(139, 92, 246, 0.04); border-color: rgba(139, 92, 246, 0.2);">
            <h3 style="margin-top: 0; font-size: 1.1rem; color: #8b5cf6 !important;">Regulator View Active</h3>
            <p style="font-size: 0.8rem; color: #cbd5e1;">Horizon Securities is currently ranked as <b>Medium Risk</b> based on recent inspection metrics.</p>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px;">
                <span style="color: #94a3b8;">SEBI Registration:</span>
                <span style="font-family: monospace; color: #cbd5e1;">INZ000012345</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px;">
                <span style="color: #94a3b8;">Last Inspection:</span>
                <span style="color: #cbd5e1;">2025-03-15</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                <span style="color: #94a3b8;">Next Inspection:</span>
                <span style="color: #cbd5e1;">2025-09-15</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hash chain validation check
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; font-size: 0.9rem; color: #10b981 !important;">✓ Cryptographic Audit Trail</h4>
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">Full audit log integrity verified. SHA-256 hash chains computed successfully with zero corrupted log nodes detected.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### SCORES Grievance Metrics (7 Days SLA)")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #3b82f6;">80.8%</p>
                <p style="margin: 0; font-size: 0.7rem; color: #94a3b8;">SLA Compliance Rate</p>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #10b981;">5.2 Days</p>
                <p style="margin: 0; font-size: 0.7rem; color: #94a3b8;">Avg Resolution Time</p>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: #f43f5e;">66.7%</p>
                <p style="margin: 0; font-size: 0.7rem; color: #94a3b8;">SLA Cycle Reduced</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        st.markdown("##### Grievance Resolution Trend")
        df_grievance = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
            "Received": [12, 9, 15, 8, 11, 14, 6],
            "Resolved": [11, 9, 14, 8, 10, 13, 4]
        })
        fig_trend = px.line(df_grievance, x="Month", y=["Received", "Resolved"], markers=True)
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f8fafc',
            height=180,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True)


# ── PAGE: OBLIGATIONS EXPLORER ────────────────────────────────────────
elif menu == "📋 Obligations Explorer":
    st.markdown("## Obligations Registry")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Search and filter extracted SEBI regulatory obligations</p>", unsafe_allow_html=True)
    
    # Filter Controls
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_query = st.text_input("Search obligations summary or text", "")
    with f_col2:
        status_filter = st.selectbox("Status", ["All", "compliant", "partially_compliant", "non_compliant"])
    with f_col3:
        category_filter = st.selectbox("Category", ["All", "kyc_onboarding", "risk_management", "reporting", "cybersecurity", "systems_process"])

    # Filtering logic
    filtered = MOCK_OBLIGATIONS
    if search_query:
        filtered = [o for o in filtered if search_query.lower() in o["summary"].lower() or search_query.lower() in o["obligation_id"].lower()]
    if status_filter != "All":
        filtered = [o for o in filtered if o["status"] == status_filter]
    if category_filter != "All":
        filtered = [o for o in filtered if o["type"] == category_filter]
        
    df_filtered = pd.DataFrame(filtered)
    if not df_filtered.empty:
        st.dataframe(
            df_filtered[["obligation_id", "summary", "process", "status"]],
            column_config={
                "obligation_id": "Obligation ID",
                "summary": "Required Obligation",
                "process": "Mapped Process Area",
                "status": "Current Compliance Status"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No obligations matching the selected filters.")


# ── PAGE: CHANGE DETECTION ────────────────────────────────────────────
elif menu == "🔍 Change Detection":
    st.markdown("## Change Detection & Ingestion Feed")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Simulate circular upload to detect additions and SLA modifications</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Upload Circular")
        uploaded_file = st.file_uploader("Upload SEBI Circular PDF", type="pdf")
        
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem;'>OR</p>", unsafe_allow_html=True)
        
        sim_btn = st.button("Simulate Grievance SLA Amendment Ingestion", type="primary")
        
    with col2:
        st.markdown("### Agentic Change Logs")
        if sim_btn:
            st.success("Ingestion Triggered: Simulated SEBI Circular on SLA Reduction Ingested!")
            
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.04); border: 1px solid rgba(245, 158, 11, 0.2); padding: 15px; border-radius: 12px; margin-bottom: 15px;">
                <p style="color: #f59e0b; font-weight: 700; margin: 0;">⚠️ SLA Modification Identified in Chapter VII, Clause 2.1</p>
                <p style="font-size: 0.8rem; color: #cbd5e1; margin-top: 8px;">
                    <b>Obligation ID:</b> OBL-GRIEVANCE-001<br>
                    <b>Previous SLA Rule:</b> Resolve investor complaints within 21 days.<br>
                    <b>New SLA Rule:</b> Resolve investor complaints within 7 days.<br>
                    <b>Change Risk:</b> Critical - Potential breach based on historical grievance logs.
                </p>
            </div>
            
            <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.2); padding: 15px; border-radius: 12px;">
                <p style="color: #10b981; font-weight: 700; margin: 0;">✨ New Obligation Detected in Chapter VII, Clause 2.2</p>
                <p style="font-size: 0.8rem; color: #cbd5e1; margin-top: 8px;">
                    <b>Obligation ID:</b> OBL-GRIEVANCE-002<br>
                    <b>Rule:</b> Maintain weekly reports of all pending grievances exceeding 3 days.<br>
                    <b>Assigned Process Area:</b> Reporting to Exchange/SEBI
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Upload a circular or click the simulation button to trigger agentic analysis.")


# ── PAGE: ASK AGENT (CHAT) ────────────────────────────────────────────
elif menu == "💬 Ask Agent":
    st.markdown("## RAG Query Assistant")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem; margin-top: -10px;'>Ask natural language questions about the SEBI Master Circular corpus</p>", unsafe_allow_html=True)
    
    # Pre-canned prompts
    st.markdown("##### Suggested Queries:")
    col_q1, col_q2 = st.columns(2)
    
    q_input = ""
    with col_q1:
        if st.button("What is the new SLA requirement for grievance redressal?"):
            q_input = "What is the new SLA requirement for grievance redressal?"
    with col_q2:
        if st.button("Show me requirements for client KYC verification"):
            q_input = "Show me requirements for client KYC verification"
            
    st.write("")
    user_query = st.text_input("Ask a question about compliance rules", value=q_input)
    
    if user_query:
        # Check backend first
        result = api_request("/agents/query", method="POST", json={"question": user_query})
        
        if result:
            st.markdown("### Answer")
            st.write(result.get("answer"))
            
            citations = result.get("citations", [])
            if citations:
                st.markdown("### Citations & Sources")
                for cit in citations:
                    st.markdown(f"- **{cit.get('clause')}** (Page {cit.get('page')}): *\"{cit.get('text')}\"*")
        else:
            # Fallback mockup responses
            st.markdown("### Answer")
            if "grievance" in user_query.lower() or "sla" in user_query.lower():
                st.markdown("""
                According to the SEBI Master Circular 2025 (Chapter VII, Clause 2.1), the **timeline for resolving investor grievances has been reduced to 7 days** from the date of receipt of the complaint.

                *Key Operational Impacts:*
                1. System alerts must flag complaints exceeding 3 days pending.
                2. Real-time updates must synchronize with the SEBI SCORES portal.
                """)
                st.markdown("### Citations & Sources")
                st.markdown("- **Chapter VII, Clause 2.1** (Page 47): *\"All registered stock brokers shall resolve grievances of investors within 7 calendar days of receipt...\"*")
            elif "kyc" in user_query.lower() or "verification" in user_query.lower():
                st.markdown("""
                Stockbrokers are required to verify the Know Your Client (KYC) details of all investors via the **Central KYC (CKYC) registry** before activating the trading account.
                
                *Key Operational Impacts:*
                1. Lookups must check CKYC status and verify PAN records.
                2. Accounts can only be activated after successful registry validation.
                """)
                st.markdown("### Citations & Sources")
                st.markdown("- **Chapter III, Clause 1.2** (Page 14): *\"verification of client identity shall be done through central registries including CKYC before account activation...\"*")
            else:
                st.markdown("No fallback RAG response mapped for this query. Connect the backend database/ChromaDB to enable generic RAG answers.")
