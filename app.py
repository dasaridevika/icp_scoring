"""
Enterprise ICP Revenue Intelligence Studio
Powered by Cloudflare Worker AI Edge Engine.
Worker AI performs full end-to-end qualification: Fit, Intent, Readiness, Value,
Disqualification, Confidence, Next Best Action, and Sales Discovery Prompts.
"""

import streamlit as st
import json
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from engine.models import ComprehensiveAIWorkerResponse
from workers.base_worker import WorkerAIClient

# Page Configuration
st.set_page_config(
    page_title="Enterprise ICP Revenue Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Luxury Dark & Neon RevOps Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div, span, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .title-gradient {
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(167, 139, 250, 0.5);
    }

    .metric-label {
        color: #94A3B8;
        font-size: 0.80rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 4px 0;
        letter-spacing: -0.5px;
    }

    .badge-a1 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;
    }
    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;
    }
    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;
    }
    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;
    }

    .action-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #311042 100%);
        border: 1px solid #A855F7;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Worker AI Client (exclusively reads CLOUDFLARE_WORKER_URL from secrets/env)
worker_client = WorkerAIClient()

# Header
st.markdown('<div class="title-gradient">⚡ Enterprise ICP Revenue Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Cloudflare Worker AI Edge Engine • Fit, Intent, Readiness & Value Qualification</div>', unsafe_allow_html=True)

# Main Input Section
col_in1, col_in2 = st.columns([3, 1])

with col_in1:
    prospect_text = st.text_area(
        "Paste Inbound Lead:",
        height=180,
        placeholder="Paste prospect notes, inbound form data, or account details to qualify...",
        key="live_prospect_input"
    )

with col_in2:
    st.markdown("#### Parameters")
    deal_size = st.number_input("Target Contract Size ($)", min_value=5000, max_value=2000000, value=75000, step=5000)
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    eval_btn = st.button("🚀 Qualify on Worker AI", type="primary", use_container_width=True)

if eval_btn:
    if not prospect_text.strip():
        st.error("Please paste account details to qualify.")
    else:
        with st.spinner("Executing Worker AI Analysis on Edge..."):
            res: ComprehensiveAIWorkerResponse = worker_client.evaluate_account(prospect_text, float(deal_size))
            st.session_state["live_worker_res"] = res

if "live_worker_res" in st.session_state:
    res: ComprehensiveAIWorkerResponse = st.session_state["live_worker_res"]
    
    st.markdown("---")
    
    if not res.success:
        st.error(f"""
        ### ❌ Unable to score this account.
        **AI evaluation failed:** {res.error_message or 'Workers AI inference failed or returned an invalid response.'}
        
        **Request ID:** `{res.request_id}`
        """)
    else:
        # Account Header
        c_head1, c_head2 = st.columns([3, 1])
        company_disp = res.company_name or "Unspecified Account"
        domain_disp = f"({res.domain})" if res.domain else ""
        contact_disp = res.contact_name or "Unspecified Contact"
        title_disp = res.job_title or "Unspecified Role"
        industry_disp = res.industry or "Unspecified Industry"
        scale_disp = res.scale or "Unspecified Scale"
        loc_disp = f" | Location: **{res.location}**" if res.location else ""

        with c_head1:
            st.markdown(f"## **{company_disp}** `{domain_disp}`")
            st.caption(f"Contact: **{contact_disp}** — *{title_disp}* | Industry: **{industry_disp}**{loc_disp} | Scale: **{scale_disp}** | Confidence: **{res.data_confidence_pct}%** | Trace: `{res.request_id}`")
        with c_head2:
            badge_class = "badge-disq" if res.is_disqualified else ("badge-a1" if "A1" in res.priority_tier or "Dream" in res.priority_tier else ("badge-a2" if "A2" in res.priority_tier or "Strong" in res.priority_tier else "badge-b1"))
            st.markdown(f'<div style="text-align:right;"><span class="{badge_class}">{res.priority_tier}</span></div>', unsafe_allow_html=True)
            if res.is_disqualified:
                st.error(f"Disqualification: {res.disqualification_reason}")

        # 4 Core Engine KPI Cards Evaluated Deterministically from Worker AI Evidence
        st.markdown("#### ⚡ 4-Dimensional AI Intelligence Engines")
        k1, k2, k3, k4 = st.columns(4)
        
        def format_snippet(text: str, max_len: int = 120) -> str:
            if not text:
                return "Evidence evaluated."
            t = text.strip()
            if len(t) <= max_len:
                return t
            return t[:max_len].rsplit(" ", 1)[0] + "..."

        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">1. ICP FIT SCORE</div>
                <div class="metric-value" style="color: #A78BFA;">{res.icp_fit_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem; line-height:1.3;">{format_snippet(res.icp_fit_rationale)}</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">2. INTENT & TIMING</div>
                <div class="metric-value" style="color: #34D399;">{res.intent_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem; line-height:1.3;">{format_snippet(res.intent_rationale)}</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">3. READINESS & AUTHORITY</div>
                <div class="metric-value" style="color: #60A5FA;">{res.readiness_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem; line-height:1.3;">{format_snippet(res.readiness_rationale)}</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">4. ACCOUNT VALUE SCALE</div>
                <div class="metric-value" style="color: #F472B6;">{res.value_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem; line-height:1.3;">Expansion: <b>{res.expansion_potential}</b></div>
            </div>
            """, unsafe_allow_html=True)

        # Why (Strengths) vs Risks
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        col_why, col_risk = st.columns(2)
        
        with col_why:
            st.markdown("##### 🟢 Key Drivers & Evidence")
            if res.key_strengths:
                for s in res.key_strengths:
                    st.success(f"✓ {s}")
            else:
                st.info(f"ICP Fit: {res.icp_fit_rationale}")

        with col_risk:
            st.markdown("##### ⚠️ Risks & Missing Information")
            if res.key_risks:
                for r in res.key_risks:
                    st.warning(f"⚠ {r}")
            else:
                st.success("No critical risks identified.")

        # Format Target
        target_display = f"{contact_disp} — {title_disp}" if (title_disp and title_disp != "Unspecified Role" and title_disp not in contact_disp) else contact_disp

        # Next Best Action Card
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="action-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.1rem; font-weight:700; color:#E9D5FF;">🎯 Deterministic Next Best Action:</span>
                <span style="background:rgba(255,255,255,0.15); padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;">SLA: {res.urgency_sla}</span>
            </div>
            <div style="font-size:1.05rem; font-weight:600; color:#FFFFFF; margin-top:8px;">{res.sales_action}</div>
            <div style="font-size:0.85rem; color:#D8B4FE; margin-top:6px;"><b>Channel:</b> {res.recommended_channel} | <b>Target:</b> {target_display}</div>
            <div style="font-size:0.85rem; color:#E2E8F0; margin-top:10px;"><b>Strategic Value Wedge:</b> {res.value_wedge or 'Accelerate strategic operational outcomes.'}</div>
            <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:12px; margin-top:12px;">
                <div style="font-size:0.8rem; font-weight:700; color:#38BDF8;">🔥 1-SENTENCE COLD OUTREACH OPENER:</div>
                <div style="font-size:0.85rem; color:#F1F5F9; font-style:italic; margin-top:4px;">"{res.outreach_hook or 'Reaching out regarding your strategic initiatives.'}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Discovery Gap Prompts
        if res.discovery_questions:
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            with st.expander("❓ Sales Discovery Questions (Targeted for Missing Evidence)", expanded=True):
                for q in res.discovery_questions:
                    st.markdown(f"• **Discovery Question:** *{q}*")

