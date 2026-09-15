"""
Enterprise ICP Revenue Intelligence Studio (v3.4)
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

# Professional RevOps UI Styling with High Visual Hierarchy
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
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
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        background: linear-gradient(135deg, #0F172A 0%, #4338CA 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.15rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .hero-subtitle {
        color: #475569 !important;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }

    .pill-badge-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 4px;
    }

    .hero-pill {
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .hero-pill-ai {
        background: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
    }

    /* Field Labels */
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        letter-spacing: 0.2px;
        margin-bottom: 3px !important;
    }

    /* Form Container Card Headers */
    .form-card-header {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A !important;
        background: #F8FAFC;
        padding: 10px 14px;
        border-radius: 8px;
        border-left: 4px solid #4F46E5;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .form-card-header span.tag {
        font-size: 0.72rem;
        font-weight: 700;
        background: #EEF2FF;
        color: #4F46E5;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #C7D2FE;
        text-transform: uppercase;
    }

    /* Section Card Header in Settings Dialog */
    .settings-section-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: #1E293B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 6px;
        margin-top: 2px;
        margin-bottom: 12px;
    }

    /* Sleek Output Cards */
    .master-score-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #311042 100%);
        border: 1px solid rgba(167, 139, 250, 0.35);
        border-radius: 16px;
        padding: 26px 30px;
        color: #FFFFFF !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), 0 8px 10px -6px rgba(15, 23, 42, 0.4);
        margin-bottom: 22px;
    }

    .ai-feature-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 14px;
        padding: 20px;
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
        padding: 20px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
    }

    .action-routing-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #2E1065 50%, #4C0519 100%);
        border: 1px solid rgba(244, 114, 182, 0.4);
        border-radius: 16px;
        padding: 24px 28px;
        color: #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(236, 72, 153, 0.18);
        margin-top: 18px;
        margin-bottom: 22px;
    }

    /* Badges */
    .badge-a1 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.35);
    }

    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
    }

    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.35);
    }

    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: #FFFFFF !important;
        padding: 8px 20px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
    }

    .tag-chip {
        display: inline-block;
        padding: 4px 10px;
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
# SETTINGS MODAL DIALOG (UNIFORMLY ALIGNED & PROFESSIONAL)
# ==============================================================================
@st.dialog("⚙️ Company ICP Standards & Thresholds", width="large")
def show_settings_dialog():
    st.caption("Configure dynamic commercial revenue thresholds, focus industries, territory whitelists, and 4-pillar percentage weights:")

    with st.form("modal_company_standards_form"):
        col_s1, col_s2 = st.columns(2, gap="large")

        with col_s1:
            with st.container(border=True):
                st.markdown('<div class="settings-section-title">🏢 Commercial Margins & Scale Sweet-Spots</div>', unsafe_allow_html=True)
                s_name = st.text_input("Company / Org Identifier", value=cfg.company_name)

                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    s_min_deal = st.number_input("Minimum Viable Deal ($)", min_value=1000, max_value=500000, value=int(cfg.min_deal_size_usd), step=5000, format="%d")
                with c_s2:
                    s_target_deal = st.number_input("Target Ideal Deal ($)", min_value=5000, max_value=2000000, value=int(cfg.target_deal_size_usd), step=10000, format="%d")

                c_s3, c_s4 = st.columns(2)
                with c_s3:
                    s_min_rev = st.number_input("Minimum Prospect Revenue ($)", min_value=0, max_value=50000000, value=int(cfg.min_company_revenue_usd), step=500000, format="%d")
                with c_s4:
                    s_ideal_rev = st.number_input("Ideal Prospect Target ARR ($)", min_value=1000000, max_value=500000000, value=int(cfg.ideal_revenue_usd), step=5000000, format="%d")

                c_s5, c_s6 = st.columns(2)
                with c_s5:
                    s_min_hc = st.number_input("Min Headcount Floor", min_value=1, max_value=1000, value=int(cfg.min_headcount), step=10, format="%d")
                with c_s6:
                    s_ideal_hc = st.number_input("Ideal Headcount Target", min_value=20, max_value=10000, value=int(cfg.ideal_headcount), step=50, format="%d")

            with st.container(border=True):
                st.markdown('<div class="settings-section-title">🎯 Primary Focus Verticals (+5 Pts)</div>', unsafe_allow_html=True)
                s_focus_ind = st.multiselect(
                    "Select Sweet-Spot Verticals",
                    options=MASTER_INDUSTRY_SECTORS,
                    default=[i for i in cfg.target_focus_industries if i in MASTER_INDUSTRY_SECTORS]
                )

        with col_s2:
            with st.container(border=True):
                st.markdown('<div class="settings-section-title">🌍 Geographic Parameters</div>', unsafe_allow_html=True)
                s_t1_geo = st.text_area(
                    "Tier 1 Supported Territories (Comma-separated)",
                    value=", ".join(cfg.tier1_territories),
                    height=65
                )
                s_proh_geo = st.text_input(
                    "Sanctioned / Prohibited Territories (Hard Disqualification)",
                    value=", ".join(cfg.prohibited_countries)
                )

            with st.container(border=True):
                st.markdown('<div class="settings-section-title">⚖️ Pillar Weights & Margins (Must = 100%)</div>', unsafe_allow_html=True)
                c_w1, c_w2 = st.columns(2)
                with c_w1:
                    s_w_firmo = st.slider("Firmographics Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_firmographics * 100), step=5)
                    s_w_auth = st.slider("Decision Authority Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_authority * 100), step=5)
                with c_w2:
                    s_w_intent = st.slider("Buying Intent Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_intent * 100), step=5)
                    s_w_val = st.slider("Contract Value Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_value * 100), step=5)

                total_w = s_w_firmo + s_w_auth + s_w_intent + s_w_val
                if total_w != 100:
                    st.warning(f"⚠️ Current weight sum is {total_w}%. Must equal 100%.")
                else:
                    st.success("✓ Total weights sum to 100%.")

                st.markdown('<div style="margin-top: 8px; font-weight:700; font-size:0.84rem; color:#1E293B;">Priority Tier Cutoff Margins:</div>', unsafe_allow_html=True)
                c_t_a1, c_t_a2, c_t_b1 = st.columns(3)
                with c_t_a1:
                    s_tier_a1 = st.number_input("Tier A1 Cutoff", min_value=70.0, max_value=95.0, value=float(cfg.tier_a1_threshold), step=5.0, format="%.0f")
                with c_t_a2:
                    s_tier_a2 = st.number_input("Tier A2 Cutoff", min_value=55.0, max_value=85.0, value=float(cfg.tier_a2_threshold), step=5.0, format="%.0f")
                with c_t_b1:
                    s_tier_b1 = st.number_input("Tier B1 Cutoff", min_value=40.0, max_value=70.0, value=float(cfg.tier_b1_threshold), step=5.0, format="%.0f")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("💾 Save ICP Standards & Recalibrate", type="primary", use_container_width=True)

    if save_btn:
        new_cfg = CompanyStandardsConfig(
            company_name=s_name,
            min_deal_size_usd=float(s_min_deal),
            target_deal_size_usd=float(s_target_deal),
            min_company_revenue_usd=float(s_min_rev),
            ideal_revenue_usd=float(s_ideal_rev),
            min_headcount=int(s_min_hc),
            ideal_headcount=int(s_ideal_hc),
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
# HERO HEADER BAR & CONTROLS
# ==============================================================================
head_col1, head_col2 = st.columns([5, 2])

with head_col1:
    st.markdown("""
    <div>
        <div class="hero-title">⚡ Enterprise ICP Revenue Intelligence Studio</div>
        <div class="hero-subtitle">High-Velocity Lead Qualification • AI Semantic Text Field Analysis • Deterministic GTM Scoring Engine</div>
        <div class="pill-badge-row">
            <span class="hero-pill hero-pill-ai">🤖 AI Role & Persona Classifier</span>
            <span class="hero-pill hero-pill-ai">⚡ AI Timeline & Urgency Signal</span>
            <span class="hero-pill">⚖️ 4-Pillar Weighted Score</span>
            <span class="hero-pill">🎯 Dynamic Org Thresholds</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
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
# MAIN LEAD QUALIFICATION FORM (CLEAN, BOLD HEADINGS, NO PLACEHOLDER DATA)
# ==============================================================================
with st.form("lead_qualification_form"):
    col_f1, col_f2 = st.columns(2, gap="large")

    with col_f1:
        with st.container(border=True):
            st.markdown("""
            <div class="form-card-header">
                <span>🏢 1. Account Scale & Firmographics</span>
                <span class="tag">Firmographic Pillar</span>
            </div>
            """, unsafe_allow_html=True)
            
            f_company = st.text_input("Company Name", value=st.session_state.get("f_company", ""))
            
            c_loc1, c_loc2 = st.columns(2)
            with c_loc1:
                f_loc = st.text_input("Primary Headquarters Location", value=st.session_state.get("f_loc", ""))
            with c_loc2:
                f_branches = st.text_input("Branch Locations / Hubs (Comma-separated)", value=st.session_state.get("f_branches", ""))

            c_ind1, c_ind2 = st.columns(2)
            with c_ind1:
                cur_ind = st.session_state.get("f_ind", MASTER_INDUSTRY_SECTORS[0])
                ind_idx = MASTER_INDUSTRY_SECTORS.index(cur_ind) if cur_ind in MASTER_INDUSTRY_SECTORS else 0
                f_ind = st.selectbox("Industry Macro Sector", options=MASTER_INDUSTRY_SECTORS, index=ind_idx)
            with c_ind2:
                f_subv = st.text_input("Sub-Vertical / Niche (AI Analyzed)", value=st.session_state.get("f_subv", ""))

            c_sc1, c_sc2 = st.columns(2)
            with c_sc1:
                f_rev = st.number_input("Annual Revenue ($ USD)", min_value=0, max_value=1000000000, value=int(st.session_state.get("f_rev", 0)), step=500000, format="%d")
            with c_sc2:
                f_hc = st.number_input("Employee Headcount", min_value=1, max_value=500000, value=int(st.session_state.get("f_hc", 50)), step=25, format="%d")

    with col_f2:
        with st.container(border=True):
            st.markdown("""
            <div class="form-card-header">
                <span>👤 2. Decision Authority, Intent & Ecosystem</span>
                <span class="tag">AI Signal Engine</span>
            </div>
            """, unsafe_allow_html=True)

            c_ct1, c_ct2 = st.columns(2)
            with c_ct1:
                f_name = st.text_input("Contact Full Name", value=st.session_state.get("f_name", ""))
            with c_ct2:
                f_email = st.text_input("Work Email Address", value=st.session_state.get("f_email", ""))

            f_role = st.text_input("Role Title (AI Analyzes Seniority & Persona)", value=st.session_state.get("f_role", ""))

            c_in1, c_in2 = st.columns(2)
            with c_in1:
                f_intent = st.text_input("Buying Intent & Notes (AI Urgency Signal)", value=st.session_state.get("f_intent", ""))
            with c_in2:
                f_deal = st.number_input("Target Contract Value ($ USD)", min_value=0, max_value=5000000, value=int(st.session_state.get("f_deal", 0)), step=5000, format="%d")

            f_tech = st.text_input("Current Tech Stack & Tools (AI Synergy Analysis)", value=st.session_state.get("f_tech", ""))

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2, _ = st.columns([2, 1, 3])
    with c_btn1:
        calc_btn = st.form_submit_button("🚀 Run AI Analysis & Qualify Lead", type="primary", use_container_width=True)
    with c_btn2:
        clear_btn = st.form_submit_button("🔄 Reset Form", use_container_width=True)

if clear_btn:
    st.session_state["f_company"] = ""
    st.session_state["f_loc"] = ""
    st.session_state["f_branches"] = ""
    st.session_state["f_ind"] = MASTER_INDUSTRY_SECTORS[0]
    st.session_state["f_subv"] = ""
    st.session_state["f_rev"] = 0
    st.session_state["f_hc"] = 50
    st.session_state["f_name"] = ""
    st.session_state["f_email"] = ""
    st.session_state["f_role"] = ""
    st.session_state["f_intent"] = ""
    st.session_state["f_deal"] = 0
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
        st.session_state["f_branches"] = f_branches
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

        branches_list = [b.strip() for b in f_branches.split(",") if b.strip()]

        submission = StreamlinedLeadForm(
            company_name=f_company.strip(),
            industry_sector=f_ind,
            sub_vertical=f_subv.strip(),
            annual_revenue_usd=float(f_rev),
            employee_count=int(f_hc),
            location=f_loc.strip(),
            branch_locations=branches_list,
            contact_name=f_name.strip(),
            contact_email=f_email.strip(),
            contact_role_title=f_role.strip(),
            buying_intent=f_intent.strip(),
            target_deal_size_usd=float(f_deal),
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
                <div style="display:flex; align-items:center; gap:18px; font-size:0.92rem; color:#CBD5E1; flex-wrap:wrap;">
                    <span>Industry: <strong style="color:#FFFFFF;">{res.lead_summary.get('industry', 'N/A')}</strong></span>
                    <span>&bull;</span>
                    <span>HQ: <strong style="color:#FFFFFF;">{res.lead_summary.get('location') or 'Global'}</strong></span>
                    {f"<span>&bull;</span><span>Branches: <strong style='color:#38BDF8;'>{len(res.lead_summary.get('branches', []))} Locations</strong></span>" if res.lead_summary.get('branches') else ""}
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
    st.markdown("<h4 style='color:#0F172A; font-weight:700; margin-bottom:12px;'>🤖 AI Semantic Strategic Intelligence</h4>", unsafe_allow_html=True)
    ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)

    with ai_col1:
        persona_str = res.ai_role.persona_type if res.ai_role else "End User"
        sen_str = res.ai_role.seniority_level if res.ai_role else "Standard"
        dept_str = res.ai_role.department if res.ai_role else "General"
        rat_str = res.ai_role.rationale if res.ai_role else ""
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:0.8px;">
                    👤 Authority & Persona
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
                    {persona_str}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-purple">{sen_str}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="color:#94A3B8; font-size:0.76rem;">Dept: <strong style="color:#E2E8F0;">{dept_str}</strong></div>
                <div style="font-style:italic; margin-top:4px; color:#A78BFA;">"{rat_str}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col2:
        market_str = res.ai_niche.market_complexity if res.ai_niche else "Established Market"
        niche_rat = res.ai_niche.rationale if res.ai_niche else ""
        reach_str = res.ai_footprint.geographic_reach if res.ai_footprint else "Single Market"
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.8px;">
                    🏢 Vertical & Market Footprint
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
                    {market_str}
                </div>
                <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
                    <span class="tag-chip tag-cyan">{res.lead_summary.get('industry', 'General')}</span>
                    <span class="tag-chip tag-emerald">{reach_str}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="font-style:italic; color:#7DD3FC;">"{niche_rat}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col3:
        urgency_str = res.ai_intent.urgency_tier if res.ai_intent else "Moderate Urgency"
        timeline_str = res.ai_intent.timeline_detected or "Standard Inbound"
        intent_rat = res.ai_intent.rationale if res.ai_intent else ""
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#FBBF24; text-transform:uppercase; letter-spacing:0.8px;">
                    ⚡ Intent & Urgency
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
                    {urgency_str}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-amber">{timeline_str}</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="font-style:italic; color:#FDE68A;">"{intent_rat}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col4:
        fit_str = res.ai_tech.ecosystem_fit if res.ai_tech else "Standard Fit"
        tech_rat = res.ai_tech.rationale if res.ai_tech else ""
        st.markdown(f"""
        <div class="ai-feature-card">
            <div>
                <div style="font-size:0.75rem; font-weight:700; color:#34D399; text-transform:uppercase; letter-spacing:0.8px;">
                    💻 Tech Synergy
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:6px; line-height:1.3;">
                    {fit_str}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag-chip tag-emerald">Ecosystem Fit</span>
                </div>
            </div>
            <div style="margin-top:14px; font-size:0.82rem; color:#CBD5E1; line-height:1.4; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <div style="font-style:italic; color:#6EE7B7;">"{tech_rat}"</div>
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

    # 6. Discovery Prompts
    if res.discovery_questions:
        with st.expander("❓ Sales Discovery Prompts (Targeted Questions for SDRs)", expanded=False):
            for q in res.discovery_questions:
                st.markdown(f"• **Discovery Prompt:** *{q}*")
