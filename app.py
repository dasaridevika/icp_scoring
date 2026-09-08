"""
Enterprise ICP Revenue Intelligence Studio
Steps 1-4: Extraction, Polarized Scoring (-5 to +5), Master Tiers & Operational Sales Activation
Framework: GTM Partners & Saber ICP Framework
"""

import streamlit as st
import json
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from engine import (
    ProspectExtractor,
    ExtractedProspectData,
    PillarScorer,
    FourPillarBreakdown,
    PillarEvaluation,
    MasterScoreResult
)
from workers.base_worker import WorkerAIClient

# Page Configuration
st.set_page_config(
    page_title="ICP Revenue Intelligence Studio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Playfair Display Typography & Modern Luxury Dark Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div, span, label {
        font-family: 'Playfair Display', serif !important;
    }
    
    .title-text {
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 50%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }

    .subtitle-text {
        color: #94A3B8;
        font-size: 1.05rem;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
    
    .kpi-card {
        background: linear-gradient(145deg, #1E1B4B 0%, #0F172A 100%);
        border: 2px solid #6366F1;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 20px 15px;
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
    }
    
    /* 4 Pillar Cards with Built-in Custom Progress Track */
    .pillar-card {
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        min-height: 165px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3);
    }
    
    .pillar-firmo {
        background: linear-gradient(145deg, #2E1065 0%, #1E1B4B 100%);
        border-left: 6px solid #A855F7;
    }
    .pillar-techno {
        background: linear-gradient(145deg, #083344 0%, #0F172A 100%);
        border-left: 6px solid #06B6D4;
    }
    .pillar-intent {
        background: linear-gradient(145deg, #064E3B 0%, #0F172A 100%);
        border-left: 6px solid #10B981;
    }
    .pillar-persona {
        background: linear-gradient(145deg, #451A03 0%, #0F172A 100%);
        border-left: 6px solid #F59E0B;
    }
    
    .gtm-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }
    .gtm-badge-pos5 { background: rgba(16, 185, 129, 0.3); color: #34D399; border: 1px solid #10B981; }
    .gtm-badge-pos3 { background: rgba(59, 130, 246, 0.3); color: #60A5FA; border: 1px solid #3B82F6; }
    .gtm-badge-pos1 { background: rgba(168, 85, 247, 0.3); color: #C084FC; border: 1px solid #A855F7; }
    .gtm-badge-neg1 { background: rgba(245, 158, 11, 0.3); color: #FBBF24; border: 1px solid #F59E0B; }
    .gtm-badge-neg3 { background: rgba(239, 68, 68, 0.3); color: #F87171; border: 1px solid #EF4444; }
    .gtm-badge-neg5 { background: rgba(220, 38, 38, 0.4); color: #FCA5A5; border: 1px solid #DC2626; }
    
    /* Vibrant Tier Badges */
    .badge-tier1 {
        background: linear-gradient(135deg, #10B981 0%, #047857 100%);
        color: white; padding: 6px 16px; border-radius: 24px; font-weight: 700; font-size: 0.95rem;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.45); display: inline-block;
    }
    .badge-tier2 {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white; padding: 6px 16px; border-radius: 24px; font-weight: 700; font-size: 0.95rem;
        box-shadow: 0 0 14px rgba(59, 130, 246, 0.45); display: inline-block;
    }
    .badge-tier3 {
        background: linear-gradient(135deg, #F59E0B 0%, #B45309 100%);
        color: white; padding: 6px 16px; border-radius: 24px; font-weight: 700; font-size: 0.95rem;
        box-shadow: 0 0 14px rgba(245, 158, 11, 0.45); display: inline-block;
    }
    .badge-disqualified {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%);
        color: white; padding: 6px 16px; border-radius: 24px; font-weight: 700; font-size: 0.95rem;
        box-shadow: 0 0 14px rgba(239, 68, 68, 0.45); display: inline-block;
    }

    .progress-track {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        height: 8px;
        width: 100%;
        margin-top: 14px;
        overflow: hidden;
    }
    .progress-fill-firmo { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #A855F7, #C084FC); }
    .progress-fill-techno { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #06B6D4, #38BDF8); }
    .progress-fill-intent { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #10B981, #34D399); }
    .progress-fill-persona { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #F59E0B, #FBBF24); }

    .discovery-box {
        background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%);
        border: 1px solid #C084FC;
        border-radius: 14px;
        padding: 20px;
        margin-top: 15px;
    }
    
    .pitch-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%);
        border: 1px solid #C084FC;
        border-radius: 14px;
        padding: 24px;
        margin-top: 15px;
        box-shadow: 0 4px 20px rgba(192, 132, 252, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Client
worker_client = WorkerAIClient()

# Header
st.markdown('<div class="title-text">Enterprise ICP Revenue Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">GTM Partners & Saber ICP Framework — Production Qualification Suite</div>', unsafe_allow_html=True)

# Lead Input Section
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    prospect_text = st.text_area(
        "Paste Lead Text / Contact Form / RFP Details:",
        height=200,
        placeholder="Company: NextEra Clean Infrastructure\nContact: Arthur Pendelton (VP of Strategy & Corporate Development)\nLocation: United States | $450M ARR | 1,200 Employees\nInquiry: Requesting custom proposal for multi-GW renewable portfolio...",
        key="lead_input_text"
    )

with col_in2:
    st.markdown("#### Parameters")
    custom_deal_size = st.number_input(
        "Estimated Deal Size ($)",
        min_value=1000,
        max_value=5000000,
        value=50000,
        step=5000
    )
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    score_btn = st.button("Score & Qualify Prospect", type="primary", use_container_width=True)

if score_btn:
    if not prospect_text.strip():
        st.error("Please paste lead details above.")
    else:
        with st.spinner("Executing full ICP qualification engine..."):
            raw_ai = worker_client.score_prospect(prospect_text, custom_deal_size) if worker_client.is_connected() else None
            # Step 1: Extraction
            extracted: ExtractedProspectData = ProspectExtractor.extract(raw_text=prospect_text, ai_data=raw_ai)
            # Step 2: Polarized Pillar Scoring
            breakdown: FourPillarBreakdown = PillarScorer.evaluate_all_pillars(extracted)
            # Step 3 & 4: Master Score & Operational Activation
            master_result: MasterScoreResult = PillarScorer.compute_master_score(extracted, breakdown, custom_deal_size)
            
            st.session_state["step1_data"] = extracted
            st.session_state["step2_breakdown"] = breakdown
            st.session_state["step3_master"] = master_result

if "step1_data" in st.session_state and "step3_master" in st.session_state:
    data: ExtractedProspectData = st.session_state["step1_data"]
    breakdown: FourPillarBreakdown = st.session_state["step2_breakdown"]
    master: MasterScoreResult = st.session_state["step3_master"]

    st.markdown("---")
    st.markdown(f"### Qualification Results: **{data.company_name}**")

    # Step 3 Master KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #6366F1;">
            <span style="color: #A5B4FC; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">MASTER ICP SCORE</span>
            <div style="color: #67E8F9; margin: 8px 0; font-size: 2.5rem; font-weight:900; line-height: 1;">
                {master.final_score} <span style="font-size:1.1rem; color:#94A3B8; font-weight:600;">/ 100</span>
            </div>
            <span style="color:#CBD5E1; font-size:0.8rem;">Conversion Probability: <strong>{master.conversion_probability}%</strong></span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        badge_class = (
            "badge-tier1" if "Tier 1" in master.tier_name
            else "badge-tier2" if "Tier 2" in master.tier_name
            else "badge-tier3" if "Tier 3" in master.tier_name
            else "badge-disqualified"
        )
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #10B981; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);">
            <span style="color: #6EE7B7; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">SALES TIER CATEGORY</span>
            <div style="margin: 8px 0;"><span class="{badge_class}">{master.tier_name}</span></div>
            <span style="color:#A7F3D0; font-size:0.8rem; font-weight:600;">{master.priority_level}</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #F59E0B; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);">
            <span style="color: #FDE68A; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">QUALITY-WEIGHTED VALUE</span>
            <div style="color: #FBBF24; margin: 8px 0; font-size: 2.3rem; font-weight:900; line-height: 1;">
                ${master.quality_weighted_value:,.0f}
            </div>
            <span style="color:#FDE68A; font-size:0.8rem;">Deal Size × ({master.final_score}%)</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #EC4899; box-shadow: 0 4px 20px rgba(236, 72, 153, 0.25);">
            <span style="color: #FBCFE8; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">TARGET DECISION MAKER</span>
            <div style="color: #F472B6; margin: 8px 0; font-size: 1.25rem; font-weight:800; line-height: 1.2; word-break: break-word;">
                {data.contact_name}
            </div>
            <span style="color:#FBCFE8; font-size:0.85rem; font-weight:600;">{data.job_title}</span>
        </div>
        """, unsafe_allow_html=True)

    # Step 2: 4 Symmetrical Pillar Cards with GTM Badges & Progress Tracks
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Four-Pillar Score Breakdown (GTM Scale: -5 to +5)")
    p_col1, p_col2 = st.columns(2)

    def get_badge_class(val: int) -> str:
        if val == 5: return "gtm-badge-pos5"
        if val == 3: return "gtm-badge-pos3"
        if val == 1: return "gtm-badge-pos1"
        if val == -1: return "gtm-badge-neg1"
        if val == -3: return "gtm-badge-neg3"
        return "gtm-badge-neg5"

    with p_col1:
        # 1. Firmographics
        f_p = breakdown.firmographic
        st.markdown(f"""
        <div class="pillar-card pillar-firmo">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#E9D5FF; font-weight:700; font-size:1.05rem;">1. {f_p.name} (30% Weight)</span>
                    <span class="gtm-badge {get_badge_class(f_p.gtm_scale)}">{f_p.gtm_label}</span>
                </div>
                <div style="color:#DDD6FE; font-size:0.9rem; margin-top:10px; line-height:1.4;">
                    {f_p.rationale}
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; color:#C084FC; font-size:0.85rem; font-weight:600; margin-top:8px;">
                    <span>Raw Score: {int(f_p.score_100)} / 100</span>
                    <span>Weighted Points: +{f_p.points_contributed}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-firmo" style="width: {int(f_p.score_100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Technographics
        t_p = breakdown.technographic
        st.markdown(f"""
        <div class="pillar-card pillar-techno">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#CFFAFE; font-weight:700; font-size:1.05rem;">2. {t_p.name} (25% Weight)</span>
                    <span class="gtm-badge {get_badge_class(t_p.gtm_scale)}">{t_p.gtm_label}</span>
                </div>
                <div style="color:#A5F3FC; font-size:0.9rem; margin-top:10px; line-height:1.4;">
                    {t_p.rationale}
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; color:#22D3EE; font-size:0.85rem; font-weight:600; margin-top:8px;">
                    <span>Raw Score: {int(t_p.score_100)} / 100</span>
                    <span>Weighted Points: +{t_p.points_contributed}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-techno" style="width: {int(t_p.score_100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        # 3. Intent & Timing
        i_p = breakdown.intent
        st.markdown(f"""
        <div class="pillar-card pillar-intent">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#D1FAE5; font-weight:700; font-size:1.05rem;">3. {i_p.name} (25% Weight)</span>
                    <span class="gtm-badge {get_badge_class(i_p.gtm_scale)}">{i_p.gtm_label}</span>
                </div>
                <div style="color:#A7F3D0; font-size:0.9rem; margin-top:10px; line-height:1.4;">
                    {i_p.rationale}
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; color:#34D399; font-size:0.85rem; font-weight:600; margin-top:8px;">
                    <span>Raw Score: {int(i_p.score_100)} / 100</span>
                    <span>Weighted Points: +{i_p.points_contributed}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-intent" style="width: {int(i_p.score_100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. Persona & Authority
        p_p = breakdown.persona
        st.markdown(f"""
        <div class="pillar-card pillar-persona">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#FEF3C7; font-weight:700; font-size:1.05rem;">4. {p_p.name} (20% Weight)</span>
                    <span class="gtm-badge {get_badge_class(p_p.gtm_scale)}">{p_p.gtm_label}</span>
                </div>
                <div style="color:#FDE68A; font-size:0.9rem; margin-top:10px; line-height:1.4;">
                    {p_p.rationale}
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; color:#FBBF24; font-size:0.85rem; font-weight:600; margin-top:8px;">
                    <span>Raw Score: {int(p_p.score_100)} / 100</span>
                    <span>Weighted Points: +{p_p.points_contributed}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill-persona" style="width: {int(p_p.score_100)}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Step 4: 2D Matrix (6sense & MadKudu Fit vs Intent)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"""
        <div style="background: rgba(30, 27, 75, 0.6); border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 12px; padding: 16px; text-align:center;">
            <span style="color:#C084FC; font-size:0.85rem; font-weight:700;">OVERALL ACCOUNT FIT INDEX</span>
            <div style="color:#E9D5FF; font-size:1.7rem; font-weight:800; margin:4px 0;">{master.fit_index} / 100</div>
            <span style="color:#DDD6FE; font-size:0.82rem;">Firmographic Scale + Technographic Readiness</span>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div style="background: rgba(6, 78, 59, 0.4); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 16px; text-align:center;">
            <span style="color:#34D399; font-size:0.85rem; font-weight:700;">BUYER INTENT & SURGE INDEX</span>
            <div style="color:#D1FAE5; font-size:1.7rem; font-weight:800; margin:4px 0;">{master.intent_index} / 100</div>
            <span style="color:#A7F3D0; font-size:0.82rem;">Procurement Urgency + Decision Authority</span>
        </div>
        """, unsafe_allow_html=True)

    # Step 4: Recommended Sales Cadence
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: 1px solid #38BDF8; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.15);">
        <h4 style="color:#38BDF8; margin:0 0 8px 0; font-size:1.15rem;">Recommended Sales Department Cadence</h4>
        <p style="color:#E2E8F0; font-size:0.98rem; margin:0; line-height:1.5;">{master.sales_action}</p>
    </div>
    """, unsafe_allow_html=True)

    # Step 4: Personalized Deal Strategy & Outreach Copy
    if master.strategy.value_wedge or master.strategy.outreach_hook:
        st.markdown(f"""
        <div class="pitch-card">
            <h4 style="color:#F472B6; margin:0 0 12px 0; font-size:1.2rem;">Personalized Deal Strategy & Outreach Copy</h4>
            <div style="color:#E9D5FF; margin-bottom:10px; font-size:0.98rem; line-height:1.5;">
                <strong style="color:#F472B6;">Value Wedge:</strong> {master.strategy.value_wedge}
            </div>
            <div style="color:#FDF4FF; margin-bottom:0; font-size:0.98rem; line-height:1.5;">
                <strong style="color:#38BDF8;">Cold Outreach Opener:</strong> <em>"{master.strategy.outreach_hook}"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sales Discovery Gap-Filling Box
    if data.discovery_questions:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="discovery-box">
            <h4 style="color:#C084FC; margin:0 0 12px 0; font-size:1.15rem;">Sales Discovery Questions (Gap-Filling for First Call)</h4>
        """, unsafe_allow_html=True)
        for i, q in enumerate(data.discovery_questions, 1):
            st.markdown(f"<p style='color:#F1F5F9; margin-bottom:8px; font-size:0.95rem;'><strong>{i}.</strong> {q}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Step 4: 1-Click Salesforce / HubSpot CRM Integration Payload
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    with st.expander("CRM Field Sync Payload (Salesforce / HubSpot)"):
        st.markdown("Ready-to-sync custom field values for your CRM:")
        st.json(master.crm_payload)
        st.download_button(
            label="Download CRM JSON",
            data=json.dumps(master.crm_payload, indent=2),
            file_name=f"{data.company_name.lower().replace(' ', '_')}_crm_payload.json",
            mime="application/json"
        )
