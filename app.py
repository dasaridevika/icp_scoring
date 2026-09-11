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

# Modern Luxury Dark & Neon RevOps Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div, span, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .title-gradient {
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.15rem;
    }

    .subtitle-text {
        color: #94A3B8;
        font-size: 0.92rem;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(167, 139, 250, 0.4);
    }

    .metric-label {
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .metric-value {
        font-size: 2.0rem;
        font-weight: 800;
        margin: 4px 0;
        letter-spacing: -0.5px;
    }

    .badge-a1 {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
        display: inline-block; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
        display: inline-block; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
        display: inline-block; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }
    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
        display: inline-block; box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    }

    .action-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #2D124D 100%);
        border: 1px solid #A855F7;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
    }
    
    .section-header {
        background: rgba(255, 255, 255, 0.03);
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #8B5CF6;
        font-weight: 700;
        font-size: 0.92rem;
        color: #F1F5F9;
        margin-top: 6px;
        margin-bottom: 12px;
    }

    .ai-pill {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        color: #DDD6FE;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_config" not in st.session_state:
    st.session_state["company_config"] = CompanyStandardsConfig()

cfg: CompanyStandardsConfig = st.session_state["company_config"]

# Header
st.markdown('<div class="title-gradient">⚡ Enterprise ICP Revenue Intelligence Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">AI Semantic Text Field Analysis • Dynamic Settings Thresholds • Deterministic GTM Scoring</div>', unsafe_allow_html=True)

# Master Tabs
tab_form, tab_settings = st.tabs(["📋 Lead Qualification Studio", "⚙️ Company ICP Standards & Thresholds"])

# ==============================================================================
# TAB 1: LEAD QUALIFICATION STUDIO
# ==============================================================================
with tab_form:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="section-header">📝 Prospect & Account Signals</div>', unsafe_allow_html=True)
        
        # Form Container
        with st.form("streamlined_lead_form"):
            st.markdown("##### 🏢 1. Company Scale & Vertical")
            f_company = st.text_input("Company Name", value=st.session_state.get("f_company", ""), placeholder="e.g. Acme Corporation")
            f_loc = st.text_input("Location / Territory", value=st.session_state.get("f_loc", ""), placeholder="e.g. United States, United Kingdom, UAE")

            c_ind1, c_ind2 = st.columns(2)
            with c_ind1:
                cur_ind = st.session_state.get("f_ind", MASTER_INDUSTRY_SECTORS[0])
                ind_idx = MASTER_INDUSTRY_SECTORS.index(cur_ind) if cur_ind in MASTER_INDUSTRY_SECTORS else 0
                f_ind = st.selectbox("Macro Industry Sector", options=MASTER_INDUSTRY_SECTORS, index=ind_idx)
            with c_ind2:
                f_subv = st.text_input("Sub-Vertical / Niche", value=st.session_state.get("f_subv", ""), placeholder="e.g. Solar Energy Farm Infrastructure")

            c_sc1, c_sc2 = st.columns(2)
            with c_sc1:
                f_rev = st.number_input("Annual Revenue ($ USD)", min_value=0.0, max_value=1000000000.0, value=float(st.session_state.get("f_rev", 0.0)), step=500000.0)
            with c_sc2:
                f_hc = st.number_input("Employee Headcount", min_value=1, max_value=500000, value=int(st.session_state.get("f_hc", 50)), step=25)

            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 👤 2. Contact Authority, Intent & Ecosystem")
            
            c_ct1, c_ct2 = st.columns(2)
            with c_ct1:
                f_name = st.text_input("Contact Name", value=st.session_state.get("f_name", ""), placeholder="e.g. Jane Doe")
            with c_ct2:
                f_email = st.text_input("Work Email", value=st.session_state.get("f_email", ""), placeholder="e.g. jane@company.com")

            f_role = st.text_input("Role Title (AI Analyzes Seniority & Persona)", value=st.session_state.get("f_role", ""), placeholder="e.g. VP of Global Supply Chain, Principal DevOps Architect, Intern")

            c_in1, c_in2 = st.columns(2)
            with c_in1:
                f_intent = st.text_input("Buying Intent & Timeline Notes", value=st.session_state.get("f_intent", ""), placeholder="e.g. Need pricing for 50 seats before Q4 renewal")
            with c_in2:
                f_deal = st.number_input("Target Contract Size ($ USD)", min_value=0.0, max_value=5000000.0, value=float(st.session_state.get("f_deal", 0.0)), step=5000.0)

            f_tech = st.text_input("Current Tech Stack & Tools", value=st.session_state.get("f_tech", ""), placeholder="e.g. SAP S/4HANA, AWS, Snowflake, Salesforce")

            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            c_btn1, c_btn2 = st.columns([2, 1])
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

        # Process Form Submission
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

    with col_output:
        st.markdown('<div class="section-header">📊 Revenue Intelligence & AI Insights</div>', unsafe_allow_html=True)
        
        # Display Results
        if "streamlined_res" in st.session_state:
            res: StreamlinedScoringResult = st.session_state["streamlined_res"]
            
            # Header Badge & Summary
            c_res1, c_res2 = st.columns([3, 2])
            with c_res1:
                st.markdown(f"### **{res.company_name or 'Unspecified Account'}**")
                st.caption(f"Standards: **{cfg.company_name}** • Master Score: **{res.master_icp_score:.1f}/100**")
            with c_res2:
                badge_class = "badge-disq" if res.is_disqualified else ("badge-a1" if "A1" in res.priority_tier else ("badge-a2" if "A2" in res.priority_tier else "badge-b1"))
                st.markdown(f'<div style="text-align:right;"><span class="{badge_class}">{res.priority_tier}</span></div>', unsafe_allow_html=True)
            
            if res.is_disqualified:
                st.error(f"❌ **Disqualification**: {res.disqualification_reason}")

            # 4 Core Pillar Score KPI Cards
            k1, k2, k3, k4 = st.columns(4)

            with k1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">1. SCALE</div>
                    <div class="metric-value" style="color: #A78BFA;">{res.pillar_firmographics.score:.0f}<span style="font-size:0.9rem; color:#94A3B8;">/100</span></div>
                    <div style="color: #94A3B8; font-size:0.72rem;">Wt: <b>{cfg.weight_firmographics*100:.0f}%</b></div>
                </div>
                """, unsafe_allow_html=True)

            with k2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">2. AUTHORITY</div>
                    <div class="metric-value" style="color: #34D399;">{res.pillar_authority.score:.0f}<span style="font-size:0.9rem; color:#94A3B8;">/100</span></div>
                    <div style="color: #94A3B8; font-size:0.72rem;">Wt: <b>{cfg.weight_authority*100:.0f}%</b></div>
                </div>
                """, unsafe_allow_html=True)

            with k3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">3. INTENT</div>
                    <div class="metric-value" style="color: #60A5FA;">{res.pillar_intent.score:.0f}<span style="font-size:0.9rem; color:#94A3B8;">/100</span></div>
                    <div style="color: #94A3B8; font-size:0.72rem;">Wt: <b>{cfg.weight_intent*100:.0f}%</b></div>
                </div>
                """, unsafe_allow_html=True)

            with k4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">4. CONTRACT</div>
                    <div class="metric-value" style="color: #F472B6;">{res.pillar_value.score:.0f}<span style="font-size:0.9rem; color:#94A3B8;">/100</span></div>
                    <div style="color: #94A3B8; font-size:0.72rem;">Wt: <b>{cfg.weight_value*100:.0f}%</b></div>
                </div>
                """, unsafe_allow_html=True)

            # 🤖 AI Text Field Intelligence Insights Panel
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 🤖 AI Text Extraction Intelligence")
            ai_c1, ai_c2 = st.columns(2)

            with ai_c1:
                if res.ai_role:
                    persona_badge_color = "#10B981" if res.ai_role.seniority_points >= 5 else ("#3B82F6" if res.ai_role.seniority_points >= 3 else "#F59E0B")
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="metric-label">👤 Role & Persona</span>
                            <span style="background:{persona_badge_color}; color:white; font-size:0.72rem; font-weight:700; padding:2px 7px; border-radius:10px;">{res.ai_role.seniority_level}</span>
                        </div>
                        <div style="font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-top:4px;">{res.ai_role.raw_title}</div>
                        <div style="font-size:0.80rem; color:#A78BFA; margin-top:2px;"><b>Persona:</b> {res.ai_role.persona_type} &nbsp;•&nbsp; <b>Dept:</b> {res.ai_role.department}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px; font-style:italic;">"{res.ai_role.rationale}"</div>
                    </div>
                    """, unsafe_allow_html=True)

                if res.ai_niche:
                    niche_color = "#10B981" if res.ai_niche.fit_points == 5 else "#3B82F6"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="metric-label">🏢 Sub-Vertical / Niche</span>
                            <span style="background:{niche_color}; color:white; font-size:0.72rem; font-weight:700; padding:2px 7px; border-radius:10px;">{res.ai_niche.market_complexity}</span>
                        </div>
                        <div style="font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-top:4px;">{res.ai_niche.raw_niche}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px; font-style:italic;">"{res.ai_niche.rationale}"</div>
                    </div>
                    """, unsafe_allow_html=True)

            with ai_c2:
                if res.ai_intent:
                    intent_color = "#10B981" if res.ai_intent.intent_points >= 5 else ("#3B82F6" if res.ai_intent.intent_points >= 3 else "#F59E0B")
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="metric-label">⚡ Intent & Urgency</span>
                            <span style="background:{intent_color}; color:white; font-size:0.72rem; font-weight:700; padding:2px 7px; border-radius:10px;">{res.ai_intent.urgency_tier}</span>
                        </div>
                        <div style="font-size:0.90rem; font-weight:700; color:#F8FAFC; margin-top:4px;">{res.ai_intent.raw_intent or 'Standard Inquiry'}</div>
                        <div style="font-size:0.80rem; color:#38BDF8; margin-top:2px;"><b>Timeline:</b> {res.ai_intent.timeline_detected or 'Unspecified'}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px; font-style:italic;">"{res.ai_intent.rationale}"</div>
                    </div>
                    """, unsafe_allow_html=True)

                if res.ai_tech:
                    tech_color = "#10B981" if res.ai_tech.tech_points >= 5 else ("#EF4444" if res.ai_tech.tech_points < 0 else "#3B82F6")
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="metric-label">💻 Tech Stack Ecosystem</span>
                            <span style="background:{tech_color}; color:white; font-size:0.72rem; font-weight:700; padding:2px 7px; border-radius:10px;">{res.ai_tech.ecosystem_fit}</span>
                        </div>
                        <div style="font-size:0.90rem; font-weight:700; color:#F8FAFC; margin-top:4px;">{res.ai_tech.raw_stack}</div>
                        <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px; font-style:italic;">"{res.ai_tech.rationale}"</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Action Box
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="action-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.0rem; font-weight:700; color:#E9D5FF;">🎯 Deterministic Next Best Action:</span>
                    <span style="background:rgba(255,255,255,0.15); padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;">SLA: {res.urgency_sla}</span>
                </div>
                <div style="font-size:0.82rem; color:#D8B4FE; margin-top:6px;"><b>Channel:</b> {res.recommended_channel}</div>
                <div style="font-size:0.82rem; color:#E2E8F0; margin-top:4px;"><b>Value Wedge:</b> {res.value_wedge}</div>
                <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:10px; margin-top:10px;">
                    <div style="font-size:0.78rem; font-weight:700; color:#38BDF8;">🔥 1-SENTENCE COLD OUTREACH OPENER:</div>
                    <div style="font-size:0.82rem; color:#F1F5F9; font-style:italic; margin-top:3px;">"{res.outreach_hook}"</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Strengths vs Risks
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            c_why, c_risk = st.columns(2)
            with c_why:
                st.markdown("###### 🟢 Key Strengths")
                if res.key_strengths:
                    for s in res.key_strengths:
                        st.success(f"✓ {s}")
                else:
                    st.info("Standard baseline profile.")
            with c_risk:
                st.markdown("###### ⚠️ Risks & Missing Evidence")
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
                            "Impact Points": pts_str,
                            "Business Rationale": rec.rationale
                        })
                    st.table(receipt_data)

            # Discovery Questions
            if res.discovery_questions:
                with st.expander("❓ Sales Discovery Prompts (Targeted Questions for SDRs)", expanded=False):
                    for q in res.discovery_questions:
                        st.markdown(f"• *{q}*")
        else:
            st.info("💡 Fill out the prospect details on the left and click **🚀 Run AI Analysis & Score Lead** to calculate the 4-pillar ICP score, AI persona extraction, and Next Best Action.")


# ==============================================================================
# TAB 2: COMPANY ICP STANDARDS & THRESHOLDS (SETTINGS)
# ==============================================================================
with tab_settings:
    st.markdown("### ⚙️ Company ICP Standards & Thresholds Studio")
    st.caption("Configure your company's own minimum deal size, target industries, allowed territories, and 4-pillar weights:")

    with st.form("company_standards_settings_form"):
        col_s1, col_s2 = st.columns(2)

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



