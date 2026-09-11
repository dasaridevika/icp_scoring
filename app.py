"""
Enterprise ICP Revenue Intelligence Studio (v3.0)
High-Velocity AI Lead Qualifier & Dynamic Company Standards Studio.
100% Pure Python • Deterministic {-5 to +5} Scoring • AI Text Field Intelligence.
"""

import streamlit as st
import json
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from engine.gtm_engine import (
    MASTER_INDUSTRY_SECTORS,
    CompanyStandardsConfig,
    StreamlinedLeadForm,
    GTMScoringEngine,
    StreamlinedScoringResult
)
from engine.ai_analyzer import AITextAnalyzer

# Page Configuration
st.set_page_config(
    page_title="Enterprise ICP Revenue Intelligence Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional RevOps High-Contrast Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1380px;
    }

    /* Hero Header */
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        background: linear-gradient(135deg, #0F172A 0%, #4338CA 60%, #6D28D9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }

    .hero-subtitle {
        color: #475569 !important;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 0.8rem;
    }

    /* Form Section Headers */
    .form-panel-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A !important;
        border-left: 4px solid #4F46E5;
        padding-left: 10px;
        margin-bottom: 14px;
        margin-top: 4px;
    }

    /* Top Bar Status Card */
    .top-status-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    /* Sleek Output Cards */
    .master-score-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #311042 100%);
        border: 1px solid rgba(167, 139, 250, 0.35);
        border-radius: 16px;
        padding: 24px 28px;
        color: #FFFFFF !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), 0 8px 10px -6px rgba(15, 23, 42, 0.4);
        margin-bottom: 20px;
    }

    .ai-feature-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 14px;
        padding: 18px;
        color: #F8FAFC !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .ai-feature-card:hover {
        border-color: rgba(167, 139, 250, 0.6);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.25);
    }

    .metric-pillar-card {
        background: linear-gradient(145deg, #0F172A 0%, #1A2238 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 18px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
    }

    .action-routing-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #2E1065 50%, #4C0519 100%);
        border: 1px solid rgba(244, 114, 182, 0.4);
        border-radius: 16px;
        padding: 22px 26px;
        color: #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(236, 72, 153, 0.18);
        margin-top: 15px;
        margin-bottom: 20px;
    }

    /* Badges */
    .badge-a1 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
    }

    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
    }

    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.35);
    }

    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
    }

    .tag-chip {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    .tag-purple {
        background: rgba(167, 139, 250, 0.2);
        color: #C4B5FD !important;
        border: 1px solid rgba(167, 139, 250, 0.4);
    }

    .tag-cyan {
        background: rgba(56, 189, 248, 0.2);
        color: #7DD3FC !important;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }

    .tag-emerald {
        background: rgba(52, 211, 153, 0.2);
        color: #6EE7B7 !important;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }

    .tag-amber {
        background: rgba(251, 191, 36, 0.2);
        color: #FDE68A !important;
        border: 1px solid rgba(251, 191, 36, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_config" not in st.session_state:
    st.session_state["company_config"] = CompanyStandardsConfig()

cfg: CompanyStandardsConfig = st.session_state["company_config"]


# ==============================================================================
# SETTINGS MODAL DIALOG
# ==============================================================================
@st.dialog("⚙️ Company ICP Standards & Thresholds", width="large")
def show_settings_dialog():
    st.caption("Configure dynamic commercial floors, focus industries, territory parameters, and 4-pillar percentage weights:")

    with st.form("modal_company_standards_form"):
        col_s1, col_s2 = st.columns(2, gap="medium")

        with col_s1:
            st.markdown("##### 🏢 Commercial & Scale Margins")
            s_name = st.text_input("Company / Organization Name", value=cfg.company_name)

            c_s1, c_s2 = st.columns(2)
            with c_s1:
                s_min_deal = st.number_input("Minimum Deal Size ($ USD)", min_value=1000.0, max_value=500000.0, value=cfg.min_deal_size_usd, step=5000.0)
            with c_s2:
                s_target_deal = st.number_input("Target Deal Size ($ USD)", min_value=5000.0, max_value=2000000.0, value=cfg.target_deal_size_usd, step=10000.0)

            c_s3, c_s4 = st.columns(2)
            with c_s3:
                s_min_rev = st.number_input("Minimum Revenue ($ USD)", min_value=0.0, max_value=50000000.0, value=cfg.min_company_revenue_usd, step=500000.0)
            with c_s4:
                s_ideal_rev = st.number_input("Ideal Revenue Target ($ USD)", min_value=1000000.0, max_value=500000000.0, value=cfg.ideal_revenue_usd, step=5000000.0)

            c_s5, c_s6 = st.columns(2)
            with c_s5:
                s_min_hc = st.number_input("Minimum Employee Count", min_value=1, max_value=1000, value=cfg.min_headcount, step=10)
            with c_s6:
                s_ideal_hc = st.number_input("Ideal Employee Count", min_value=20, max_value=10000, value=cfg.ideal_headcount, step=50)

            st.markdown("##### 🎯 Target Focus Industries")
            s_focus_ind = st.multiselect(
                "Primary Focus Verticals (+5 pts)",
                options=MASTER_INDUSTRY_SECTORS,
                default=[i for i in cfg.target_focus_industries if i in MASTER_INDUSTRY_SECTORS]
            )

        with col_s2:
            st.markdown("##### 🌍 Geographic Parameters")
            s_t1_geo = st.text_area(
                "Tier 1 Supported Territories (Comma-separated)",
                value=", ".join(cfg.tier1_territories),
                height=68
            )
            s_proh_geo = st.text_input(
                "Prohibited / Sanctioned Territories (Hard Disqualification)",
                value=", ".join(cfg.prohibited_countries)
            )

            st.markdown("##### ⚖️ Pillar Percentage Weights (Must Sum to 100%)")
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                s_w_firmo = st.slider("Firmographics Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_firmographics * 100), step=5)
                s_w_auth = st.slider("Decision Authority Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_authority * 100), step=5)
            with c_w2:
                s_w_intent = st.slider("Buying Intent Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_intent * 100), step=5)
                s_w_val = st.slider("Contract Value Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_value * 100), step=5)

            total_w = s_w_firmo + s_w_auth + s_w_intent + s_w_val
            if total_w != 100:
                st.warning(f"⚠️ Total weight sum is {total_w}%. Must equal 100%.")
            else:
                st.success("✓ Total weights sum to 100%.")

            st.markdown("##### 🏷️ Priority Tier Cutoffs")
            c_t_a1, c_t_a2, c_t_b1 = st.columns(3)
            with c_t_a1:
                s_tier_a1 = st.number_input("Tier A1 Cutoff", min_value=70.0, max_value=95.0, value=cfg.tier_a1_threshold, step=5.0)
            with c_t_a2:
                s_tier_a2 = st.number_input("Tier A2 Cutoff", min_value=55.0, max_value=85.0, value=cfg.tier_a2_threshold, step=5.0)
            with c_t_b1:
                s_tier_b1 = st.number_input("Tier B1 Cutoff", min_value=40.0, max_value=70.0, value=cfg.tier_b1_threshold, step=5.0)

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("💾 Save ICP Standards & Recalibrate", type="primary", use_container_width=True)

    if save_btn:
        new_cfg = CompanyStandardsConfig(
            company_name=s_name,
            min_deal_size_usd=s_min_deal,
            target_deal_size_usd=s_target_deal,
            min_company_revenue_usd=s_min_rev,
            ideal_revenue_usd=s_ideal_rev,
            min_headcount=s_min_hc,
            ideal_headcount=s_ideal_hc,
            target_focus_industries=s_focus_ind,
            tier1_territories=[t.strip() for t in s_t1_geo.split(",") if t.strip()],
            prohibited_countries=[p.strip() for p in s_proh_geo.split(",") if p.strip()],
            weight_firmographics=s_w_firmo / 100.0,
            weight_authority=s_w_auth / 100.0,
            weight_intent=s_w_intent / 100.0,
            weight_value=s_w_val / 100.0,
            tier_a1_threshold=s_tier_a1,
            tier_a2_threshold=s_tier_a2,
            tier_b1_threshold=s_tier_b1
        )
        st.session_state["company_config"] = new_cfg
        st.rerun()


# ==============================================================================
# HEADER BAR & CONTROLS
# ==============================================================================
head_col1, head_col2 = st.columns([5, 2])

with head_col1:
    st.markdown('<div class="hero-title">⚡ Enterprise ICP Revenue Intelligence Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI Semantic Text Field Analysis • Dynamic ICP Thresholds • Deterministic GTM Scoring</div>', unsafe_allow_html=True)

with head_col2:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    btn_c1, btn_c2 = st.columns([1, 1])
    with btn_c2:
        if st.button("⚙️ ICP Settings", use_container_width=True, help="Configure company standards, margins, and weights"):
            show_settings_dialog()

# Clean Status Indicator Bar
with st.container(border=True):
    bar_c1, bar_c2, bar_c3, bar_c4 = st.columns([3, 2, 2, 3])
    with bar_c1:
        st.markdown(f"🏢 **Standards Org**: `{cfg.company_name}`")
    with bar_c2:
        st.markdown(f"🎯 **Min ACV Floor**: `${cfg.min_deal_size_usd:,.0f}`")
    with bar_c3:
        st.markdown(f"📈 **Target ARR**: `${cfg.ideal_revenue_usd:,.0f}`")
    with bar_c4:
        st.markdown("🤖 **AI Semantics**: `Classifiers Active`")


# ==============================================================================
# MAIN LEAD QUALIFICATION FORM (CLEAN & UNIFORMLY ALIGNED)
# ==============================================================================
with st.form("lead_qualification_form"):
    col_f1, col_f2 = st.columns(2, gap="large")

    with col_f1:
        st.markdown('<div class="form-panel-header">🏢 1. Account Scale & Firmographics</div>', unsafe_allow_html=True)
        f_company = st.text_input("Company Name", value=st.session_state.get("f_company", ""), placeholder="e.g. Acme Corporation")
        f_loc = st.text_input("Geographic Location / Territory", value=st.session_state.get("f_loc", ""), placeholder="e.g. United States, United Kingdom, UAE")

        c_ind1, c_ind2 = st.columns(2)
        with c_ind1:
            cur_ind = st.session_state.get("f_ind", MASTER_INDUSTRY_SECTORS[0])
            ind_idx = MASTER_INDUSTRY_SECTORS.index(cur_ind) if cur_ind in MASTER_INDUSTRY_SECTORS else 0
            f_ind = st.selectbox("Industry Sector", options=MASTER_INDUSTRY_SECTORS, index=ind_idx)
        with c_ind2:
            f_subv = st.text_input("Sub-Vertical / Niche (AI Analyzed)", value=st.session_state.get("f_subv", ""), placeholder="e.g. Solar Energy Farm Infrastructure")

        c_sc1, c_sc2 = st.columns(2)
        with c_sc1:
            f_rev = st.number_input("Annual Revenue ($ USD)", min_value=0.0, max_value=1000000000.0, value=float(st.session_state.get("f_rev", 0.0)), step=500000.0)
        with c_sc2:
            f_hc = st.number_input("Employee Headcount", min_value=1, max_value=500000, value=int(st.session_state.get("f_hc", 50)), step=25)

    with col_f2:
        st.markdown('<div class="form-panel-header">👤 2. Decision Authority, Intent & Ecosystem</div>', unsafe_allow_html=True)
        c_ct1, c_ct2 = st.columns(2)
        with c_ct1:
            f_name = st.text_input("Contact Full Name", value=st.session_state.get("f_name", ""), placeholder="e.g. Jane Doe")
        with c_ct2:
            f_email = st.text_input("Work Email Address", value=st.session_state.get("f_email", ""), placeholder="e.g. jane@company.com")

        f_role = st.text_input("Role Title (AI Analyzes Seniority & Persona)", value=st.session_state.get("f_role", ""), placeholder="e.g. VP of Global Supply Chain, Principal DevOps Architect, Intern")

        c_in1, c_in2 = st.columns(2)
        with c_in1:
            f_intent = st.text_input("Buying Intent & Notes (AI Urgency Signal)", value=st.session_state.get("f_intent", ""), placeholder="e.g. Need pricing for 50 seats before Q4 renewal")
        with c_in2:
            f_deal = st.number_input("Target Contract Value ($ USD)", min_value=0.0, max_value=5000000.0, value=float(st.session_state.get("f_deal", 0.0)), step=5000.0)

        f_tech = st.text_input("Current Tech Stack & Tools (AI Synergy Analysis)", value=st.session_state.get("f_tech", ""), placeholder="e.g. SAP S/4HANA, AWS, Snowflake, Salesforce")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2, _ = st.columns([2, 1, 3])
    with c_btn1:
        calc_btn = st.form_submit_button("🚀 Run AI Analysis & Qualify Lead", type="primary", use_container_width=True)
    with c_btn2:
        clear_btn = st.form_submit_button("🔄 Reset Form", use_container_width=True)

if clear_btn:
    st.session_state["f_company"] = ""
    st.session_state["f_loc"] = ""
    st.session_state["f_ind"] = MASTER_INDUSTRY_SECTORS[0]
    st.session_state["f_subv"] = ""
    st.session_state["f_rev"] = 0.0
    st.session_state["f_hc"] = 50
    st.session_state["f_name"] = ""
    st.session_state["f_email"] = ""
    st.session_state["f_role"] = ""
    st.session_state["f_intent"] = ""
    st.session_state["f_deal"] = 0.0
    st.session_state["f_tech"] = ""
    if "streamlined_res" in st.session_state:
        del st.session_state["streamlined_res"]
    st.rerun()

# Process Form Evaluation
if calc_btn:
    if not f_company.strip():
        st.warning("⚠️ Please provide a Company Name to qualify the account.")
    else:
        st.session_state["f_company"] = f_company
        st.session_state["f_loc"] = f_loc
        st.session_state["f_ind"] = f_ind
        st.session_state["f_subv"] = f_subv
        st.session_state["f_rev"] = f_rev
        st.session_state["f_hc"] = f_hc
        st.session_state["f_name"] = f_name
        st.session_state["f_email"] = f_email
        st.session_state["f_role"] = f_role
        st.session_state["f_intent"] = f_intent
        st.session_state["f_deal"] = f_deal
        st.session_state["f_tech"] = f_tech

        submission = StreamlinedLeadForm(
            company_name=f_company.strip(),
            industry_sector=f_ind,
            sub_vertical=f_subv.strip(),
            annual_revenue_usd=f_rev,
            employee_count=f_hc,
            location=f_loc.strip(),
            contact_name=f_name.strip(),
            contact_email=f_email.strip(),
            contact_role_title=f_role.strip(),
            buying_intent=f_intent.strip(),
            target_deal_size_usd=f_deal,
            tech_stack_notes=f_tech.strip()
        )
        res: StreamlinedScoringResult = GTMScoringEngine.evaluate(submission, cfg)
        st.session_state["streamlined_res"] = res
        st.rerun()


# ==============================================================================
# OUTPUT: SLEEK CARD INTELLIGENCE SUITE
# ==============================================================================
if "streamlined_res" in st.session_state:
    st.markdown("---")
    res: StreamlinedScoringResult = st.session_state["streamlined_res"]

    badge_class = "badge-disq" if res.is_disqualified else ("badge-a1" if "A1" in res.priority_tier else ("badge-a2" if "A2" in res.priority_tier else "badge-b1"))
    fit_color = "#EF4444" if res.is_disqualified else ("#10B981" if res.master_icp_score >= 70 else ("#3B82F6" if res.master_icp_score >= 55 else "#F59E0B"))

    # 1. Master Score Obsidian Banner
    st.markdown(f"""
    <div class="master-score-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div>
                <div style="font-size:0.80rem; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
                    GTM Revenue Intelligence Report &bull; {cfg.company_name}
                </div>
                <div style="font-size:1.9rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; margin-bottom:6px;">
                    {res.company_name or 'Unspecified Account'}
                </div>
                <div style="display:flex; align-items:center; gap:18px; font-size:0.92rem; color:#CBD5E1;">
                    <span>Industry: <strong style="color:#FFFFFF;">{res.lead_summary.get('industry', 'N/A')}</strong></span>
                    <span>&bull;</span>
                    <span>Location: <strong style="color:#FFFFFF;">{res.lead_summary.get('location', 'Global')}</strong></span>
                    <span>&bull;</span>
                    <span>SLA: <strong style="color:#38BDF8;">{res.urgency_sla}</strong></span>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.78rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">
                    Master ICP Score
                </div>
                <div style="font-size:2.8rem; font-weight:800; color:{fit_color}; line-height:1; letter-spacing:-1px; margin-bottom:8px;">
                    {res.master_icp_score:.1f}<span style="font-size:1.2rem; color:#94A3B8; font-weight:500;">/100</span>
                </div>
                <div>
                    <span class="{badge_class}">{res.priority_tier}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if res.is_disqualified:
        st.error(f"❌ **Hard Disqualification Detected**: {res.disqualification_reason}")

    # 2. 🤖 AI Semantic Text Intelligence Grid
    st.markdown("<h4 style='color:#0F172A; font-weight:700; margin-bottom:12px;'>🤖 AI Semantic Text Field Intelligence</h4>", unsafe_allow_html=True)
    ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)

    with ai_col1:
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:0.8px;">
                    👤 Role & Authority
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-top:4px; line-height:1.3;">
                    {res.ai_role.raw_title if res.ai_role else 'Unspecified Role'}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-purple">{res.ai_role.seniority_level if res.ai_role else 'Standard'}</span>
                    <span class="tag-chip tag-cyan">{res.ai_role.persona_type if res.ai_role else 'End User'}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.80rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="color:#94A3B8; font-size:0.75rem;">Dept: <strong style="color:#E2E8F0;">{res.ai_role.department if res.ai_role else 'General'}</strong></div>
                <div style="font-style:italic; margin-top:4px; color:#A78BFA;">"{res.ai_role.rationale if res.ai_role else ''}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col2:
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px;">
                    🏢 Vertical & Niche
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-top:4px; line-height:1.3;">
                    {res.ai_niche.raw_niche if res.ai_niche else 'Standard Market'}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-cyan">{res.ai_niche.market_complexity if res.ai_niche else 'Established'}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.80rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="font-style:italic; color:#7DD3FC;">"{res.ai_niche.rationale if res.ai_niche else ''}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col3:
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#FBBF24; text-transform:uppercase; letter-spacing:0.8px;">
                    ⚡ Intent & Timeline
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-top:4px; line-height:1.3;">
                    {res.ai_intent.raw_intent if res.ai_intent else 'Standard Lead'}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-amber">{res.ai_intent.urgency_tier if res.ai_intent else 'Moderate'}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.80rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="color:#94A3B8; font-size:0.75rem;">Timeline: <strong style="color:#FDE68A;">{res.ai_intent.timeline_detected or 'Unspecified'}</strong></div>
                <div style="font-style:italic; margin-top:4px; color:#FBBF24;">"{res.ai_intent.rationale if res.ai_intent else ''}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col4:
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#34D399; text-transform:uppercase; letter-spacing:0.8px;">
                    💻 Tech Stack Synergy
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-top:4px; line-height:1.3;">
                    {res.ai_tech.raw_stack if res.ai_tech else 'Standard Stack'}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-emerald">{res.ai_tech.ecosystem_fit if res.ai_tech else 'Standard'}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.80rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="font-style:italic; color:#6EE7B7;">"{res.ai_tech.rationale if res.ai_tech else ''}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. ⚡ 4-Dimensional Revenue Intelligence Score Cards
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#0F172A; font-weight:700; margin-bottom:12px;'>⚡ 4-Dimensional Revenue Intelligence Scores</h4>", unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)

    pillars = [
        (p1, "1. FIRMOGRAPHIC SCALE", res.pillar_firmographics, cfg.weight_firmographics, "#38BDF8"),
        (p2, "2. DECISION AUTHORITY", res.pillar_authority, cfg.weight_authority, "#A78BFA"),
        (p3, "3. BUYING INTENT", res.pillar_intent, cfg.weight_intent, "#FBBF24"),
        (p4, "4. CONTRACT VALUE", res.pillar_value, cfg.weight_value, "#34D399")
    ]

    for col, title, p_res, weight, col_accent in pillars:
        with col:
            diff = p_res.score - 50.0
            diff_str = f"+{diff:.0f} pts" if diff >= 0 else f"{diff:.0f} pts"
            st.markdown(f"""
            <div class="metric-pillar-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:0.72rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.6px;">
                        {title}
                    </div>
                    <div style="font-size:0.72rem; font-weight:700; color:{col_accent};">
                        {weight*100:.0f}% Weight
                    </div>
                </div>
                <div style="font-size:2.1rem; font-weight:800; color:#FFFFFF; margin:8px 0; letter-spacing:-0.5px;">
                    {p_res.score:.0f} <span style="font-size:1.0rem; font-weight:500; color:#94A3B8;">/100</span>
                </div>
                <div style="font-size:0.80rem; font-weight:600; color:{col_accent};">
                    {diff_str} vs baseline
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 4. 🎯 Next Best Action & Routing Card
    st.markdown(f"""
    <div class="action-routing-card">
        <div style="font-size:0.78rem; font-weight:700; color:#F472B6; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
            🎯 Strategic Next Best Action & Routing &bull; SLA: {res.urgency_sla}
        </div>
        <div style="font-size:1.25rem; font-weight:700; color:#FFFFFF; margin-bottom:10px;">
            Channel: <span style="color:#FDE68A;">{res.recommended_channel}</span>
        </div>
        <div style="font-size:0.92rem; color:#F1F5F9; line-height:1.5; margin-bottom:12px;">
            <strong>Strategic Value Wedge:</strong> {res.value_wedge}
        </div>
        <div style="background:rgba(0,0,0,0.3); border-left:4px solid #F472B6; padding:12px 16px; border-radius:8px;">
            <div style="font-size:0.76rem; font-weight:700; color:#F472B6; text-transform:uppercase; letter-spacing:0.5px;">🔥 Recommended 1-Sentence Outreach Hook:</div>
            <div style="font-size:0.92rem; color:#FFFFFF; font-style:italic; margin-top:4px;">"{res.outreach_hook}"</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Strengths vs Risks
    c_why, c_risk = st.columns(2)
    with c_why:
        with st.container(border=True):
            st.markdown("#### 🟢 Key Strengths & Value Drivers")
            if res.key_strengths:
                for s in res.key_strengths:
                    st.success(f"✓ {s}")
            else:
                st.info("Standard baseline profile.")
    with c_risk:
        with st.container(border=True):
            st.markdown("#### ⚠️ Risks & Missing Evidence")
            if res.key_risks:
                for r in res.key_risks:
                    st.warning(f"⚠ {r}")
            else:
                st.success("Zero critical risks detected.")

    # 6. Explainable Point Audit Receipt
    with st.expander("🧾 View Full Score Audit Receipt (Explainable Point Breakdown)", expanded=False):
        all_summaries = [
            res.pillar_firmographics,
            res.pillar_authority,
            res.pillar_intent,
            res.pillar_value
        ]
        for p_sum in all_summaries:
            st.markdown(f"**{p_sum.pillar_name} (Score: {p_sum.score:.0f}/100)**")
            receipt_data = []
            for rec in p_sum.field_receipts:
                pts_str = f"+{rec.gtm_points}" if rec.gtm_points > 0 else str(rec.gtm_points)
                receipt_data.append({
                    "Field": rec.field_name,
                    "Submitted Value": str(rec.raw_value),
                    "Impact Points": pts_str,
                    "Business Rationale": rec.rationale
                })
            st.table(receipt_data)

    # 7. Discovery Prompts
    if res.discovery_questions:
        with st.expander("❓ Sales Discovery Prompts (Targeted Questions for SDRs)", expanded=False):
            for q in res.discovery_questions:
                st.markdown(f"• **Discovery Prompt:** *{q}*")
