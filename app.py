"""
Enterprise ICP Revenue Intelligence Studio (v2.5)
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

# Ultra-High Contrast Theme-Safe CSS
st.markdown("""
<style>
    /* Main container padding */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Headings and Subheadings */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #0F172A !important;
        margin-bottom: 0.15rem;
    }

    .main-subtitle {
        font-size: 0.98rem;
        color: #334155 !important;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }

    /* Section Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* All markdown paragraphs and labels */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] div,
    label,
    div[data-baseweb="tab-list"] button {
        color: #0F172A !important;
        font-weight: 500;
    }

    /* High-contrast Badges */
    .badge-tier-a1 {
        background-color: #059669;
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.25);
    }

    .badge-tier-a2 {
        background-color: #2563EB;
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
    }

    .badge-tier-b1 {
        background-color: #D97706;
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(217, 119, 6, 0.25);
    }

    .badge-disq {
        background-color: #DC2626;
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 24px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.25);
    }

    .ai-pill-tag {
        background-color: #EEF2FF;
        color: #4338CA !important;
        border: 1px solid #C7D2FE;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }

    /* Container Card Enhancements */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_config" not in st.session_state:
    st.session_state["company_config"] = CompanyStandardsConfig()

cfg: CompanyStandardsConfig = st.session_state["company_config"]

# Header
st.markdown('<div class="main-title">⚡ Enterprise ICP Revenue Intelligence Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">AI Semantic Text Field Analysis • Dynamic Settings Thresholds • Deterministic GTM Scoring</div>', unsafe_allow_html=True)

# Master Tabs
tab_form, tab_settings = st.tabs(["📋 Lead Qualification Studio", "⚙️ Company ICP Standards & Thresholds"])

# ==============================================================================
# TAB 1: LEAD QUALIFICATION STUDIO
# ==============================================================================
with tab_form:
    # Active Framework Status Bar
    with st.container(border=True):
        st_c1, st_c2, st_c3, st_c4 = st.columns([3, 2, 2, 3])
        with st_c1:
            st.markdown(f"🏢 **Active Org Standards**: **{cfg.company_name}**")
        with st_c2:
            st.markdown(f"🎯 **Min ACV**: **${cfg.min_deal_size_usd:,.0f}**")
        with st_c3:
            st.markdown(f"📈 **Target ARR**: **${cfg.ideal_revenue_usd:,.0f}**")
        with st_c4:
            st.markdown('<span class="ai-pill-tag">🟢 AI Semantic Classifiers Online</span>', unsafe_allow_html=True)

    # Main Lead Qualification Form
    with st.form("streamlined_lead_form"):
        col_f1, col_f2 = st.columns(2, gap="large")

        with col_f1:
            st.markdown("### 🏢 1. Company Scale & Vertical Profile")
            f_company = st.text_input("1. Company Name", value=st.session_state.get("f_company", ""), placeholder="e.g. Acme Corporation")
            f_loc = st.text_input("2. Location / Territory", value=st.session_state.get("f_loc", ""), placeholder="e.g. United States, United Kingdom, UAE")

            c_ind1, c_ind2 = st.columns(2)
            with c_ind1:
                cur_ind = st.session_state.get("f_ind", MASTER_INDUSTRY_SECTORS[0])
                ind_idx = MASTER_INDUSTRY_SECTORS.index(cur_ind) if cur_ind in MASTER_INDUSTRY_SECTORS else 0
                f_ind = st.selectbox("3. Macro Industry Sector", options=MASTER_INDUSTRY_SECTORS, index=ind_idx)
            with c_ind2:
                f_subv = st.text_input("Sub-Vertical / Niche (AI Analyzed)", value=st.session_state.get("f_subv", ""), placeholder="e.g. Solar Energy Farm Infrastructure")

            c_sc1, c_sc2 = st.columns(2)
            with c_sc1:
                f_rev = st.number_input("4. Annual Revenue ($ USD)", min_value=0.0, max_value=1000000000.0, value=float(st.session_state.get("f_rev", 0.0)), step=500000.0)
            with c_sc2:
                f_hc = st.number_input("Employee Headcount", min_value=1, max_value=500000, value=int(st.session_state.get("f_hc", 50)), step=25)

        with col_f2:
            st.markdown("### 👤 2. Contact Authority, Intent & Tech Stack")
            c_ct1, c_ct2 = st.columns(2)
            with c_ct1:
                f_name = st.text_input("5. Contact Name", value=st.session_state.get("f_name", ""), placeholder="e.g. Jane Doe")
            with c_ct2:
                f_email = st.text_input("Work Email", value=st.session_state.get("f_email", ""), placeholder="e.g. jane@company.com")

            f_role = st.text_input("6. Role Title (AI Analyzes Seniority & Persona)", value=st.session_state.get("f_role", ""), placeholder="e.g. VP of Global Supply Chain, Principal DevOps Architect, Intern")

            c_in1, c_in2 = st.columns(2)
            with c_in1:
                f_intent = st.text_input("Buying Intent & Notes (AI Urgency Signal)", value=st.session_state.get("f_intent", ""), placeholder="e.g. Need pricing for 50 seats before Q4 renewal")
            with c_in2:
                f_deal = st.number_input("Target Contract Size ($ USD)", min_value=0.0, max_value=5000000.0, value=float(st.session_state.get("f_deal", 0.0)), step=5000.0)

            f_tech = st.text_input("Tech Stack & Tools (AI Ecosystem Analysis)", value=st.session_state.get("f_tech", ""), placeholder="e.g. SAP S/4HANA, AWS, Snowflake, Salesforce")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        c_btn1, c_btn2, _ = st.columns([2, 1, 3])
        with c_btn1:
            calc_btn = st.form_submit_button("🚀 Run AI Analysis & Score Lead", type="primary", use_container_width=True)
        with c_btn2:
            clear_btn = st.form_submit_button("🔄 Clear Form", use_container_width=True)

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

    # Process Form
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

    st.markdown("---")

    # Display Results / Framework Ready State
    if "streamlined_res" in st.session_state:
        res: StreamlinedScoringResult = st.session_state["streamlined_res"]

        # Header Badge & Master Score Bar
        c_res1, c_res2 = st.columns([3, 1])
        with c_res1:
            st.markdown(f"## **{res.company_name or 'Unspecified Account'}**")
            st.markdown(f"Standards: **{cfg.company_name}** &nbsp;•&nbsp; Master ICP Fit: **{res.master_icp_score:.1f}/100** &nbsp;•&nbsp; SLA: **{res.urgency_sla}**")
        with c_res2:
            badge_class = "badge-disq" if res.is_disqualified else ("badge-tier-a1" if "A1" in res.priority_tier else ("badge-tier-a2" if "A2" in res.priority_tier else "badge-tier-b1"))
            st.markdown(f'<div style="text-align:right; margin-top:8px;"><span class="{badge_class}">{res.priority_tier}</span></div>', unsafe_allow_html=True)

        if res.is_disqualified:
            st.error(f"❌ **Hard Disqualification Detected**: {res.disqualification_reason}")

        # 🤖 AI Semantic Text Intelligence Panel
        st.markdown("### 🤖 AI Semantic Text Field Intelligence")
        ai_c1, ai_c2, ai_c3, ai_c4 = st.columns(4)

        with ai_c1:
            with st.container(border=True):
                st.markdown("#### 👤 Role & Persona")
                if res.ai_role:
                    st.markdown(f"**{res.ai_role.raw_title}**")
                    st.markdown(f"Level: **{res.ai_role.seniority_level}**")
                    st.markdown(f"Persona: **{res.ai_role.persona_type}**")
                    st.caption(f"Dept: {res.ai_role.department}")
                    st.caption(f"_{res.ai_role.rationale}_")

        with ai_c2:
            with st.container(border=True):
                st.markdown("#### 🏢 Vertical Niche")
                if res.ai_niche:
                    st.markdown(f"**{res.ai_niche.raw_niche}**")
                    st.markdown(f"Market: **{res.ai_niche.market_complexity}**")
                    st.caption(f"_{res.ai_niche.rationale}_")

        with ai_c3:
            with st.container(border=True):
                st.markdown("#### ⚡ Intent & Timeline")
                if res.ai_intent:
                    st.markdown(f"**{res.ai_intent.raw_intent or 'Standard Inquiry'}**")
                    st.markdown(f"Urgency: **{res.ai_intent.urgency_tier}**")
                    st.caption(f"Timeline: **{res.ai_intent.timeline_detected or 'Unspecified'}**")
                    st.caption(f"_{res.ai_intent.rationale}_")

        with ai_c4:
            with st.container(border=True):
                st.markdown("#### 💻 Tech Ecosystem")
                if res.ai_tech:
                    st.markdown(f"**{res.ai_tech.raw_stack}**")
                    st.markdown(f"Fit: **{res.ai_tech.ecosystem_fit}**")
                    st.caption(f"_{res.ai_tech.rationale}_")

        # 4 Core Pillar Score KPI Cards
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("### ⚡ 4-Dimensional Revenue Intelligence Scores")
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric(
                label=f"1. FIRMOGRAPHIC SCALE ({cfg.weight_firmographics*100:.0f}%)",
                value=f"{res.pillar_firmographics.score:.0f} / 100",
                delta=f"{res.pillar_firmographics.score - 50:+.0f} pts vs base"
            )

        with k2:
            st.metric(
                label=f"2. DECISION AUTHORITY ({cfg.weight_authority*100:.0f}%)",
                value=f"{res.pillar_authority.score:.0f} / 100",
                delta=f"{res.pillar_authority.score - 50:+.0f} pts vs base"
            )

        with k3:
            st.metric(
                label=f"3. BUYING INTENT ({cfg.weight_intent*100:.0f}%)",
                value=f"{res.pillar_intent.score:.0f} / 100",
                delta=f"{res.pillar_intent.score - 50:+.0f} pts vs base"
            )

        with k4:
            st.metric(
                label=f"4. CONTRACT VALUE ({cfg.weight_value*100:.0f}%)",
                value=f"{res.pillar_value.score:.0f} / 100",
                delta=f"{res.pillar_value.score - 50:+.0f} pts vs base"
            )

        # Action Box
        with st.container(border=True):
            st.markdown(f"#### 🎯 Next Best Action & Routing (SLA: `{res.urgency_sla}`)")
            st.markdown(f"**Recommended Channel:** {res.recommended_channel}")
            st.markdown(f"**Strategic Value Wedge:** {res.value_wedge}")
            st.info(f"🔥 **1-Sentence Sales Opener:** \"{res.outreach_hook}\"")

        # Strengths vs Risks
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

        # Full Explainable Point Receipt
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

        # Discovery Questions
        if res.discovery_questions:
            with st.expander("❓ Sales Discovery Prompts (Targeted Questions for SDRs)", expanded=False):
                for q in res.discovery_questions:
                    st.markdown(f"• **Discovery Question:** *{q}*")
    else:
        # Framework Ready State
        st.markdown("### ⚡ System Readiness & Active ICP Framework")
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            with st.container(border=True):
                st.markdown("#### 1. FIRMOGRAPHIC SCALE")
                st.markdown(f"Min ARR: **${cfg.min_company_revenue_usd:,.0f}**")
                st.markdown(f"Min Headcount: **{cfg.min_headcount}**")
                st.caption(f"Weight: {cfg.weight_firmographics*100:.0f}%")
        with r2:
            with st.container(border=True):
                st.markdown("#### 2. DECISION AUTHORITY")
                st.markdown("AI Role Classifier: **Online**")
                st.markdown("Freemail Filter: **Active**")
                st.caption(f"Weight: {cfg.weight_authority*100:.0f}%")
        with r3:
            with st.container(border=True):
                st.markdown("#### 3. BUYING INTENT")
                st.markdown("Timeline Extraction: **Active**")
                st.markdown("Urgency Signal: **Active**")
                st.caption(f"Weight: {cfg.weight_intent*100:.0f}%")
        with r4:
            with st.container(border=True):
                st.markdown("#### 4. CONTRACT VALUE")
                st.markdown(f"Target ACV: **${cfg.target_deal_size_usd:,.0f}**")
                st.markdown("Ecosystem Synergies: **Active**")
                st.caption(f"Weight: {cfg.weight_value*100:.0f}%")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.info("💡 Fill in the prospect signals in the form above and click **🚀 Run AI Analysis & Score Lead** to calculate the real-time ICP qualification score and targeted outreach strategy.")


# ==============================================================================
# TAB 2: COMPANY ICP STANDARDS & THRESHOLDS (SETTINGS)
# ==============================================================================
with tab_settings:
    st.markdown("### ⚙️ Company ICP Standards & Thresholds Studio")
    st.caption("Configure your company's own minimum deal size, target industries, allowed territories, and 4-pillar weights:")

    with st.form("company_standards_settings_form"):
        col_s1, col_s2 = st.columns(2, gap="large")

        with col_s1:
            st.markdown("#### 🏢 Commercial & Scale Margins")
            s_name = st.text_input("Your Company Org Name", value=cfg.company_name)
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                s_min_deal = st.number_input("Min Viable Deal Size ($)", min_value=1000.0, max_value=500000.0, value=cfg.min_deal_size_usd, step=5000.0)
            with c_s2:
                s_target_deal = st.number_input("Target Ideal Deal Size ($)", min_value=5000.0, max_value=2000000.0, value=cfg.target_deal_size_usd, step=10000.0)

            c_s3, c_s4 = st.columns(2)
            with c_s3:
                s_min_rev = st.number_input("Min Prospect Revenue ($)", min_value=0.0, max_value=50000000.0, value=cfg.min_company_revenue_usd, step=500000.0)
            with c_s4:
                s_ideal_rev = st.number_input("Ideal Prospect Revenue ($)", min_value=1000000.0, max_value=500000000.0, value=cfg.ideal_revenue_usd, step=5000000.0)

            c_s5, c_s6 = st.columns(2)
            with c_s5:
                s_min_hc = st.number_input("Min Headcount Threshold", min_value=1, max_value=1000, value=cfg.min_headcount, step=10)
            with c_s6:
                s_ideal_hc = st.number_input("Ideal Headcount Sweet Spot", min_value=20, max_value=10000, value=cfg.ideal_headcount, step=50)

            st.markdown("#### 🎯 Target Focus Industries")
            s_focus_ind = st.multiselect(
                "Primary Sweet-Spot Verticals (Awards +5 points)",
                options=MASTER_INDUSTRY_SECTORS,
                default=[i for i in cfg.target_focus_industries if i in MASTER_INDUSTRY_SECTORS]
            )

        with col_s2:
            st.markdown("#### 🌍 Geographic Territories")
            s_t1_geo = st.text_area(
                "Tier 1 Supported Territories (Comma-separated)",
                value=", ".join(cfg.tier1_territories),
                height=70
            )
            s_proh_geo = st.text_input(
                "Prohibited / Sanctioned Territories (Hard Disqualification)",
                value=", ".join(cfg.prohibited_countries)
            )

            st.markdown("#### ⚖️ Pillar Percentage Weights (Must Sum to 100%)")
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                s_w_firmo = st.slider("Firmographics Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_firmographics*100), step=5)
                s_w_auth = st.slider("Decision Authority Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_authority*100), step=5)
            with c_w2:
                s_w_intent = st.slider("Buying Intent Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_intent*100), step=5)
                s_w_val = st.slider("Contract Value Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_value*100), step=5)

            total_w = s_w_firmo + s_w_auth + s_w_intent + s_w_val
            if total_w != 100:
                st.warning(f"⚠️ Current weight sum is {total_w}%. Please adjust so the sum equals exactly 100%.")
            else:
                st.success("✓ Weights sum to exactly 100%.")

            st.markdown("#### 🏷️ Priority Tier Cutoff Margins")
            c_t_a1, c_t_a2, c_t_b1 = st.columns(3)
            with c_t_a1:
                s_tier_a1 = st.number_input("Tier A1 Cutoff", min_value=70.0, max_value=95.0, value=cfg.tier_a1_threshold, step=5.0)
            with c_t_a2:
                s_tier_a2 = st.number_input("Tier A2 Cutoff", min_value=55.0, max_value=85.0, value=cfg.tier_a2_threshold, step=5.0)
            with c_t_b1:
                s_tier_b1 = st.number_input("Tier B1 Cutoff", min_value=40.0, max_value=70.0, value=cfg.tier_b1_threshold, step=5.0)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        save_cfg_btn = st.form_submit_button("💾 Save Company ICP Standards & Recalibrate", type="primary", use_container_width=True)

    if save_cfg_btn:
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
        st.success("✓ Company ICP Standards & Thresholds updated successfully! All lead scoring will now reflect these standards.")
        st.rerun()
