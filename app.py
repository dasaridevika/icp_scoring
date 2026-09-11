"""
Enterprise ICP Revenue Intelligence Studio (v2.0)
GTM Partners 4-Pillar Form-Based Scoring & Company ICP Standards Studio.
100% Pure Python • Deterministic {-5, -3, -1, +1, +3, +5} Forced Choice Scoring.
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
    LeadFormSubmission,
    FirmographicsForm,
    TechnographicsForm,
    QualifyingForm,
    ReadinessForm,
    GTMScoringEngine,
    GTMScoringResult
)

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
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .title-gradient {
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-fill-color: transparent;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.1rem;
    }

    .subtitle-text {
        color: #94A3B8;
        font-size: 0.90rem;
        margin-bottom: 1.0rem;
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
        font-size: 0.78rem;
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
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
    }
    .badge-a2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
    }
    .badge-b1 {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
    }
    .badge-disq {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.90rem;
    }

    .action-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #311042 100%);
        border: 1px solid #A855F7;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
    }
    
    .section-header {
        background: rgba(255, 255, 255, 0.04);
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #8B5CF6;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "company_config" not in st.session_state:
    st.session_state["company_config"] = CompanyStandardsConfig()

cfg: CompanyStandardsConfig = st.session_state["company_config"]

# Header
st.markdown('<div class="title-gradient">⚡ Enterprise ICP Revenue Intelligence Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">GTM Partners 4-Pillar Qualification • Dynamic Company Thresholds • Deterministic {-5 to +5} Scoring</div>', unsafe_allow_html=True)

# Master Tabs
tab_form, tab_settings = st.tabs(["📋 Lead Qualification Form", "⚙️ Company ICP Standards & Thresholds"])

# ==============================================================================
# TAB 1: LEAD QUALIFICATION FORM
# ==============================================================================
with tab_form:
    # Quick Preset Bar
    c_pre1, c_pre2, c_pre3, c_pre4 = st.columns([2, 1, 1, 1])
    with c_pre1:
        st.caption("Fill in the prospect attributes across the 4 pillars below to calculate the official GTM Partners ICP score:")
    with c_pre2:
        if st.button("🏢 Load Parveen Mfg Lead", use_container_width=True):
            st.session_state["f_company"] = "Parveen Industries Pvt. Ltd."
            st.session_state["f_rev"] = 75000000.0
            st.session_state["f_ind"] = "Energy, Utilities & Renewables"
            st.session_state["f_subv"] = "Solar Power & Oilfield Infrastructure"
            st.session_state["f_hc"] = 1500
            st.session_state["f_hq"] = "United Arab Emirates (UAE)"
            st.session_state["f_hubs"] = "UAE, India, Middle East"
            st.session_state["t_comp"] = "SAP, AWS"
            st.session_state["t_block"] = ""
            st.session_state["t_soph"] = "Hybrid Enterprise"
            st.session_state["t_ren"] = "Renewal in 3-6 months"
            st.session_state["q_seats"] = 50
            st.session_state["q_team"] = 15
            st.session_state["q_name"] = "Gabriel Martinez"
            st.session_state["q_email"] = "sales@parvenoilfield.com"
            st.session_state["q_role"] = "Commercial Sales & Procurement Director"
            st.session_state["q_sen"] = "VP / Head of (+5)"
            st.session_state["q_bud"] = "Approved & Allocated Budget (+5)"
            st.session_state["q_price"] = "Comfortable with Premium Pricing (+5)"
            st.session_state["q_acc"] = "Active Business Expansion (+5)"
            st.session_state["r_deal"] = 75000.0
            st.session_state["r_hire"] = "Aggressive Hiring in Buying Dept (+5)"
            st.session_state["r_fund"] = "Bootstrapped & Highly Profitable (+5)"
            st.session_state["r_sig"] = "Executive Callback / Demo Scheduled (+5)"
            st.session_state["r_grow"] = ["New Facility / Physical Assets (+5)", "New Product Line Expansion (+3)"]
            st.session_state["r_mkt"] = ["Global Geographic Expansion (+5)"]
            st.rerun()

    with c_pre3:
        if st.button("⚡ Load SaaS Mid-Market", use_container_width=True):
            st.session_state["f_company"] = "CloudScale Dynamics Inc."
            st.session_state["f_rev"] = 18000000.0
            st.session_state["f_ind"] = "Technology, SaaS & IT"
            st.session_state["f_subv"] = "Cloud Infrastructure & FinOps"
            st.session_state["f_hc"] = 280
            st.session_state["f_hq"] = "United States"
            st.session_state["f_hubs"] = "USA, UK, Canada"
            st.session_state["t_comp"] = "Salesforce, Snowflake, AWS"
            st.session_state["t_block"] = ""
            st.session_state["t_soph"] = "Modern Cloud-Native"
            st.session_state["t_ren"] = "Renewal in <3 months"
            st.session_state["q_seats"] = 30
            st.session_state["q_team"] = 8
            st.session_state["q_name"] = "Sarah Jenkins"
            st.session_state["q_email"] = "s.jenkins@cloudscale.io"
            st.session_state["q_role"] = "VP of Infrastructure & DevOps"
            st.session_state["q_sen"] = "VP / Head of (+5)"
            st.session_state["q_bud"] = "Approved & Allocated Budget (+5)"
            st.session_state["q_price"] = "Comfortable with Premium Pricing (+5)"
            st.session_state["q_acc"] = "Urgent Compliance (+5)"
            st.session_state["r_deal"] = 60000.0
            st.session_state["r_hire"] = "Aggressive Hiring in Buying Dept (+5)"
            st.session_state["r_fund"] = "Series A / B Funded (+5)"
            st.session_state["r_sig"] = "Inbound RFP Submitted (+5)"
            st.session_state["r_grow"] = ["New Product Line Expansion (+3)"]
            st.session_state["r_mkt"] = ["Major Rebranding / Repositioning (+3)"]
            st.rerun()

    with c_pre4:
        if st.button("🔄 Reset Blank Form", use_container_width=True):
            st.session_state["f_company"] = ""
            st.session_state["f_rev"] = 5000000.0
            st.session_state["f_ind"] = MASTER_INDUSTRY_SECTORS[0]
            st.session_state["f_subv"] = ""
            st.session_state["f_hc"] = 100
            st.session_state["f_hq"] = ""
            st.session_state["f_hubs"] = ""
            st.session_state["t_comp"] = ""
            st.session_state["t_block"] = ""
            st.session_state["t_soph"] = "Hybrid Enterprise"
            st.session_state["t_ren"] = "Unknown"
            st.session_state["q_seats"] = 10
            st.session_state["q_team"] = 5
            st.session_state["q_name"] = ""
            st.session_state["q_email"] = ""
            st.session_state["q_role"] = ""
            st.session_state["q_sen"] = "Director / Principal (+3)"
            st.session_state["q_bud"] = "Discretionary Budget Pending (+3)"
            st.session_state["q_price"] = "Standard Commercial Fit (+3)"
            st.session_state["q_acc"] = "Standard Review (+1)"
            st.session_state["r_deal"] = 35000.0
            st.session_state["r_hire"] = "General Expansion (+3)"
            st.session_state["r_fund"] = "Bootstrapped & Highly Profitable (+5)"
            st.session_state["r_sig"] = "Active Pricing Inquiry (+3)"
            st.session_state["r_grow"] = []
            st.session_state["r_mkt"] = []
            st.rerun()

    # Form Container
    with st.form("gtm_lead_qualification_form"):
        col_p1, col_p2 = st.columns(2)

        # -------------------------------------------------------------
        # PILLAR 1: FIRMOGRAPHICS
        # -------------------------------------------------------------
        with col_p1:
            st.markdown('<div class="section-header">🏢 1. Firmographics (Scale & Market Fit)</div>', unsafe_allow_html=True)
            f_company = st.text_input("Company Name", value=st.session_state.get("f_company", "Parveen Industries Pvt. Ltd."))
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                f_rev = st.number_input("Annual Revenue ($ USD)", min_value=0.0, max_value=1000000000.0, value=float(st.session_state.get("f_rev", 75000000.0)), step=1000000.0)
            with c_f2:
                f_hc = st.number_input("Employee Headcount", min_value=1, max_value=500000, value=int(st.session_state.get("f_hc", 1500)), step=50)

            c_f3, c_f4 = st.columns(2)
            with c_f3:
                cur_ind = st.session_state.get("f_ind", "Energy, Utilities & Renewables")
                ind_idx = MASTER_INDUSTRY_SECTORS.index(cur_ind) if cur_ind in MASTER_INDUSTRY_SECTORS else 0
                f_ind = st.selectbox("Industry Macro-Sector", options=MASTER_INDUSTRY_SECTORS, index=ind_idx)
            with c_f4:
                f_subv = st.text_input("Sub-Vertical / Niche", value=st.session_state.get("f_subv", "Solar Power & Oilfield Infrastructure"))

            c_f5, c_f6 = st.columns(2)
            with c_f5:
                f_hq = st.text_input("Headquarters Location", value=st.session_state.get("f_hq", "United Arab Emirates (UAE)"))
            with c_f6:
                f_hubs = st.text_input("Operating Regions / Hubs", value=st.session_state.get("f_hubs", "UAE, India, Middle East"), help="Comma-separated operating countries or hubs")

        # -------------------------------------------------------------
        # PILLAR 2: TECHNOGRAPHICS
        # -------------------------------------------------------------
        with col_p2:
            st.markdown('<div class="section-header">💻 2. Technographics (Stack Maturity & Ecosystem)</div>', unsafe_allow_html=True)
            t_comp = st.text_input("Complementary Tools & Ecosystem", value=st.session_state.get("t_comp", "SAP, AWS"), help="Tools they use that you partner or integrate with (comma-separated)")
            t_block = st.text_input("Blocking / Competing Stack", value=st.session_state.get("t_block", ""), help="Incumbent competitors locked in (comma-separated)")

            c_t1, c_t2 = st.columns(2)
            with c_t1:
                soph_opts = ["Modern Cloud-Native", "Hybrid Enterprise", "Legacy On-Premise", "Unknown"]
                cur_soph = st.session_state.get("t_soph", "Hybrid Enterprise")
                soph_idx = soph_opts.index(cur_soph) if cur_soph in soph_opts else 1
                t_soph = st.selectbox("Stack Sophistication", options=soph_opts, index=soph_idx)
            with c_t2:
                ren_opts = ["Renewal in <3 months", "Renewal in 3-6 months", "Renewal in 6-12 months", "Multi-year Locked", "Unknown"]
                cur_ren = st.session_state.get("t_ren", "Renewal in 3-6 months")
                ren_idx = ren_opts.index(cur_ren) if cur_ren in ren_opts else 1
                t_ren = st.selectbox("Contract Renewal Timing", options=ren_opts, index=ren_idx)

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        col_p3, col_p4 = st.columns(2)

        # -------------------------------------------------------------
        # PILLAR 3: QUALIFYING CHARACTERISTICS
        # -------------------------------------------------------------
        with col_p3:
            st.markdown('<div class="section-header">🎯 3. Qualifying Characteristics (Authority & Budget)</div>', unsafe_allow_html=True)
            c_q1, c_q2 = st.columns(2)
            with c_q1:
                q_name = st.text_input("Contact Name", value=st.session_state.get("q_name", "Gabriel Martinez"))
            with c_q2:
                q_email = st.text_input("Work Email", value=st.session_state.get("q_email", "sales@parvenoilfield.com"))

            c_q3, c_q4 = st.columns(2)
            with c_q3:
                q_role = st.text_input("Role Title", value=st.session_state.get("q_role", "Commercial Sales & Procurement Director"))
            with c_q4:
                sen_opts = [
                    "C-Suite / Founder (+5)",
                    "VP / Head of (+5)",
                    "Director / Principal (+3)",
                    "Manager (+1)",
                    "Individual Contributor (+1)",
                    "Student / Intern (-5)"
                ]
                cur_sen = st.session_state.get("q_sen", "VP / Head of (+5)")
                sen_idx = sen_opts.index(cur_sen) if cur_sen in sen_opts else 1
                q_sen = st.selectbox("Seniority Level", options=sen_opts, index=sen_idx)

            c_q5, c_q6 = st.columns(2)
            with c_q5:
                q_seats = st.number_input("Potential User Seats", min_value=1, max_value=50000, value=int(st.session_state.get("q_seats", 50)))
            with c_q6:
                q_team = st.number_input("Team Members in Org", min_value=1, max_value=10000, value=int(st.session_state.get("q_team", 15)))

            c_q7, c_q8 = st.columns(2)
            with c_q7:
                bud_opts = [
                    "Approved & Allocated Budget (+5)",
                    "Discretionary Budget Pending (+3)",
                    "Exploratory / No Budget Yet (-1)"
                ]
                cur_bud = st.session_state.get("q_bud", "Approved & Allocated Budget (+5)")
                bud_idx = bud_opts.index(cur_bud) if cur_bud in bud_opts else 0
                q_bud = st.selectbox("Budget Line Item", options=bud_opts, index=bud_idx)
            with c_q8:
                price_opts = [
                    "Comfortable with Premium Pricing (+5)",
                    "Standard Commercial Fit (+3)",
                    "Discount / Budget Squeeze (-1)",
                    "Price Inhibitor (-3)"
                ]
                cur_price = st.session_state.get("q_price", "Comfortable with Premium Pricing (+5)")
                price_idx = price_opts.index(cur_price) if cur_price in price_opts else 0
                q_price = st.selectbox("Pricing Fit & Inhibitors", options=price_opts, index=price_idx)

            acc_opts = [
                "Active Business Expansion (+5)",
                "Urgent Compliance (+5)",
                "Project Deadline (+3)",
                "Standard Review (+1)",
                "None (-1)"
            ]
            cur_acc = st.session_state.get("q_acc", "Active Business Expansion (+5)")
            acc_idx = acc_opts.index(cur_acc) if cur_acc in acc_opts else 0
            q_acc = st.selectbox("Accelerators & Motivating Triggers", options=acc_opts, index=acc_idx)

        # -------------------------------------------------------------
        # PILLAR 4: READINESS TO BUY
        # -------------------------------------------------------------
        with col_p4:
            st.markdown('<div class="section-header">⚡ 4. Readiness to Buy (Intent & Velocity Signals)</div>', unsafe_allow_html=True)
            r_deal = st.number_input("Target Contract Size ($ USD)", min_value=1000.0, max_value=5000000.0, value=float(st.session_state.get("r_deal", 75000.0)), step=5000.0)

            c_r1, c_r2 = st.columns(2)
            with c_r1:
                hire_opts = [
                    "Aggressive Hiring in Buying Dept (+5)",
                    "General Expansion (+3)",
                    "Stable (+1)",
                    "Unknown (-1)",
                    "Layoffs (-5)"
                ]
                cur_hire = st.session_state.get("r_hire", "Aggressive Hiring in Buying Dept (+5)")
                hire_idx = hire_opts.index(cur_hire) if cur_hire in hire_opts else 0
                r_hire = st.selectbox("Hiring Status", options=hire_opts, index=hire_idx)
            with c_r2:
                fund_opts = [
                    "Bootstrapped & Highly Profitable (+5)",
                    "Series A / B Funded (+5)",
                    "Series C+ / PE Backed (+5)",
                    "Public Enterprise (+3)",
                    "Pre-Seed / Unfunded (-1)"
                ]
                cur_fund = st.session_state.get("r_fund", "Bootstrapped & Highly Profitable (+5)")
                fund_idx = fund_opts.index(cur_fund) if cur_fund in fund_opts else 0
                r_fund = st.selectbox("Funding & Capital Round", options=fund_opts, index=fund_idx)

            sig_opts = [
                "Executive Callback / Demo Scheduled (+5)",
                "Inbound RFP Submitted (+5)",
                "Active Pricing Inquiry (+3)",
                "General Browsing (+1)"
            ]
            cur_sig = st.session_state.get("r_sig", "Executive Callback / Demo Scheduled (+5)")
            sig_idx = sig_opts.index(cur_sig) if cur_sig in sig_opts else 0
            r_sig = st.selectbox("In-Market Buying Signals", options=sig_opts, index=sig_idx)

            grow_all = [
                "New Facility / Physical Assets (+5)",
                "M&A Acquisition (+5)",
                "New Product Line Expansion (+3)",
                "None"
            ]
            cur_grow = st.session_state.get("r_grow", ["New Facility / Physical Assets (+5)", "New Product Line Expansion (+3)"])
            r_grow = st.multiselect("Growth Investments", options=grow_all, default=[g for g in cur_grow if g in grow_all])

            mkt_all = [
                "Global Geographic Expansion (+5)",
                "Major Rebranding / Repositioning (+3)",
                "New GTM Launch (+3)",
                "None"
            ]
            cur_mkt = st.session_state.get("r_mkt", ["Global Geographic Expansion (+5)"])
            r_mkt = st.multiselect("Marketing Updates", options=mkt_all, default=[m for m in cur_mkt if m in mkt_all])

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Calculate GTM Partners ICP Revenue Score", type="primary", use_container_width=True)

    # Process Form
    if submit_btn or "gtm_result" not in st.session_state:
        submission = LeadFormSubmission(
            firmographics=FirmographicsForm(
                company_name=f_company,
                annual_revenue_usd=f_rev,
                industry_sector=f_ind,
                sub_vertical=f_subv,
                employee_count=f_hc,
                hq_location=f_hq,
                operating_regions=[h.strip() for h in f_hubs.split(",") if h.strip()]
            ),
            technographics=TechnographicsForm(
                complementary_tools=[c.strip() for c in t_comp.split(",") if c.strip()],
                blocking_competitors=[b.strip() for b in t_block.split(",") if b.strip()],
                stack_sophistication=t_soph,
                contract_renewal_timing=t_ren
            ),
            qualifying=QualifyingForm(
                potential_user_seats=q_seats,
                team_members_count=q_team,
                contact_name=q_name,
                contact_email=q_email,
                contact_role_title=q_role,
                contact_seniority=q_sen,
                budget_line_item=q_bud,
                pricing_fit=q_price,
                accelerators_trigger=q_acc
            ),
            readiness=ReadinessForm(
                target_deal_size_usd=r_deal,
                hiring_status=r_hire,
                funding_round=r_fund,
                buying_signals=r_sig,
                growth_investments=r_grow,
                marketing_updates=r_mkt
            )
        )
        res = GTMScoringEngine.evaluate(submission, cfg)
        st.session_state["gtm_result"] = res

    # Display Results
    if "gtm_result" in st.session_state:
        res: GTMScoringResult = st.session_state["gtm_result"]
        
        st.markdown("---")
        
        # Header Badge & Summary
        c_res1, c_res2 = st.columns([3, 1])
        with c_res1:
            st.markdown(f"## **{res.company_name or 'Unspecified Account'}**")
            st.caption(f"Evaluated against **{cfg.company_name}** standards | Model: **GTM Partners Forced Choice (±1, ±3, ±5)**")
        with c_res2:
            badge_class = "badge-disq" if res.is_disqualified else ("badge-a1" if "A1" in res.priority_tier else ("badge-a2" if "A2" in res.priority_tier else "badge-b1"))
            st.markdown(f'<div style="text-align:right;"><span class="{badge_class}">{res.priority_tier}</span></div>', unsafe_allow_html=True)
            if res.is_disqualified:
                st.error(f"Disqualification Reason: {res.disqualification_reason}")

        # 4 Core Pillar Score KPI Cards
        st.markdown("#### ⚡ 4-Dimensional GTM Revenue Intelligence Scores")
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">1. FIRMOGRAPHICS</div>
                <div class="metric-value" style="color: #A78BFA;">{res.firmographics_summary.normalized_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem;">Net Impact: <b>{res.firmographics_summary.net_gtm_points:+d} pts</b> (Weight: {cfg.weight_firmographics*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">2. TECHNOGRAPHICS</div>
                <div class="metric-value" style="color: #34D399;">{res.technographics_summary.normalized_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem;">Net Impact: <b>{res.technographics_summary.net_gtm_points:+d} pts</b> (Weight: {cfg.weight_technographics*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">3. QUALIFYING FIT</div>
                <div class="metric-value" style="color: #60A5FA;">{res.qualifying_summary.normalized_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem;">Net Impact: <b>{res.qualifying_summary.net_gtm_points:+d} pts</b> (Weight: {cfg.weight_qualifying*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">4. READINESS & INTENT</div>
                <div class="metric-value" style="color: #F472B6;">{res.readiness_summary.normalized_score:.0f}<span style="font-size:1rem; color:#94A3B8;">/100</span></div>
                <div style="color: #94A3B8; font-size:0.75rem;">Net Impact: <b>{res.readiness_summary.net_gtm_points:+d} pts</b> (Weight: {cfg.weight_readiness*100:.0f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        # Action Box
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="action-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.1rem; font-weight:700; color:#E9D5FF;">🎯 Deterministic Next Best Action:</span>
                <span style="background:rgba(255,255,255,0.15); padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;">SLA: {res.urgency_sla}</span>
            </div>
            <div style="font-size:0.85rem; color:#D8B4FE; margin-top:8px;"><b>Recommended Channel:</b> {res.recommended_channel}</div>
            <div style="font-size:0.85rem; color:#E2E8F0; margin-top:8px;"><b>Strategic Value Wedge:</b> {res.value_wedge}</div>
            <div style="background:rgba(0,0,0,0.25); border-radius:8px; padding:12px; margin-top:12px;">
                <div style="font-size:0.8rem; font-weight:700; color:#38BDF8;">🔥 1-SENTENCE COLD OUTREACH OPENER:</div>
                <div style="font-size:0.85rem; color:#F1F5F9; font-style:italic; margin-top:4px;">"{res.outreach_hook}"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Strengths vs Risks
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        c_why, c_risk = st.columns(2)
        with c_why:
            st.markdown("##### 🟢 Key Strengths & Value Drivers (+5 / +3)")
            if res.key_strengths:
                for s in res.key_strengths:
                    st.success(f"✓ {s}")
            else:
                st.info("Standard baseline profile.")
        with c_risk:
            st.markdown("##### ⚠️ Risks & Cost-to-Serve Inefficiencies (-3 / -5)")
            if res.key_risks:
                for r in res.key_risks:
                    st.warning(f"⚠ {r}")
            else:
                st.success("Zero critical risks detected.")

        # Full 19-Field Audit Receipt
        with st.expander("🧾 View Full 19-Field Score Audit Receipt (Explainable GTM Breakdown)", expanded=False):
            st.markdown("Every discrete field is scored on the official **$\\{-5, -3, -1, +1, +3, +5\\}$** impact scale:")
            all_summaries = [
                res.firmographics_summary,
                res.technographics_summary,
                res.qualifying_summary,
                res.readiness_summary
            ]
            for p_sum in all_summaries:
                st.markdown(f"**{p_sum.pillar_name} (Normalized Score: {p_sum.normalized_score:.0f}/100 | Net Points: {p_sum.net_gtm_points:+d})**")
                receipt_data = []
                for rec in p_sum.field_receipts:
                    pts_str = f"+{rec.gtm_points}" if rec.gtm_points > 0 else str(rec.gtm_points)
                    receipt_data.append({
                        "Field": rec.field_name,
                        "Submitted Value": str(rec.raw_value),
                        "GTM Score": pts_str,
                        "Business Rationale": rec.rationale
                    })
                st.table(receipt_data)

        # Discovery Questions
        if res.discovery_questions:
            with st.expander("❓ Sales Discovery Prompts (Targeted for Missing or -1 Uncertain Attributes)", expanded=True):
                for q in res.discovery_questions:
                    st.markdown(f"• **Discovery Prompt:** *{q}*")


# ==============================================================================
# TAB 2: COMPANY ICP STANDARDS & THRESHOLDS (SETTINGS)
# ==============================================================================
with tab_settings:
    st.markdown("### ⚙️ Company ICP Standards & Thresholds Studio")
    st.caption("Configure your company's specific margins, deal size boundaries, target industries, allowed territories, and pillar weights:")

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
            st.markdown("#### 🌍 Geographic & Ecosystem Whitelists")
            s_t1_geo = st.text_area(
                "Tier 1 Supported Territories (Comma-separated)",
                value=", ".join(cfg.tier1_territories),
                height=70
            )
            s_proh_geo = st.text_input(
                "Prohibited / Sanctioned Territories (Hard Disqualification)",
                value=", ".join(cfg.prohibited_countries)
            )

            s_comp_white = st.text_input(
                "Complementary Partner Tools (Awards +5 / +3 points)",
                value=", ".join(cfg.complementary_whitelist)
            )
            s_block_black = st.text_input(
                "Blocking Competitor Tools (Applies -3 penalty)",
                value=", ".join(cfg.blocker_blacklist)
            )

            st.markdown("#### ⚖️ Pillar Percentage Weights (Must Sum to 100%)")
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                s_w_firmo = st.slider("Firmographics Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_firmographics*100), step=5)
                s_w_techno = st.slider("Technographics Weight (%)", min_value=5, max_value=60, value=int(cfg.weight_technographics*100), step=5)
            with c_w2:
                s_w_qual = st.slider("Qualifying Characteristics (%)", min_value=5, max_value=60, value=int(cfg.weight_qualifying*100), step=5)
                s_w_ready = st.slider("Readiness & Intent (%)", min_value=5, max_value=60, value=int(cfg.weight_readiness*100), step=5)

            total_w = s_w_firmo + s_w_techno + s_w_qual + s_w_ready
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
            complementary_whitelist=[c.strip() for c in s_comp_white.split(",") if c.strip()],
            blocker_blacklist=[b.strip() for b in s_block_black.split(",") if b.strip()],
            weight_firmographics=s_w_firmo / 100.0,
            weight_technographics=s_w_techno / 100.0,
            weight_qualifying=s_w_qual / 100.0,
            weight_readiness=s_w_ready / 100.0,
            tier_a1_threshold=s_tier_a1,
            tier_a2_threshold=s_tier_a2,
            tier_b1_threshold=s_tier_b1
        )
        st.session_state["company_config"] = new_cfg
        st.success("✓ Company ICP Standards & Thresholds updated successfully! All lead scoring will now reflect these standards.")
        st.rerun()

