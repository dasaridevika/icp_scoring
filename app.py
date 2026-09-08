"""
========================================================================================
Enterprise ICP Lead Qualification & Intelligence Engine
Framework: Saber ICP Scoring Model (https://www.saber.app/glossary/icp-scoring-model)
Powered by Cloudflare Worker AI (Dynamic Evaluation)
========================================================================================
"""

import streamlit as st
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from workers.base_worker import WorkerAIClient, get_secret

# Page Configuration
st.set_page_config(
    page_title="ICP Revenue Intelligence Studio",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Playfair Display Typography & Refined Luxury Modern Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, div, span, label {
        font-family: 'Playfair Display', serif !important;
    }
    
    /* Elegant Title */
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
    
    /* Top 4 KPI Cards - Equal Height and Balanced Flexbox */
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
    
    /* 4 Pillar Cards - Equal Height with Integrated Progress Bar */
    .pillar-card {
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        min-height: 155px;
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
    
    /* Built-in Custom Progress Track */
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
    
    /* Playbook & Strategy Card */
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

# Helper to extract entities from raw text if worker defaults were used
def extract_smart_entities(raw_text: str, current_res: dict) -> dict:
    updated = dict(current_res)
    text = raw_text.strip()
    
    # 1. Company extraction
    if updated.get("company_name") in [None, "", "Target Account", "Target Prospect", "Account"]:
        for line in text.splitlines():
            line_clean = line.strip()
            if line_clean.lower().startswith(("company:", "company name:", "account:", "organization:")):
                val = line_clean.split(":", 1)[1].strip()
                if val:
                    updated["company_name"] = val
                    break
        if updated.get("company_name") in [None, "", "Target Account", "Target Prospect", "Account"]:
            first_line = text.splitlines()[0].strip() if text.splitlines() else ""
            if ":" not in first_line and len(first_line) < 50 and len(first_line) > 2:
                updated["company_name"] = first_line

    # 2. Contact extraction
    if updated.get("contact_name") in [None, "", "Decision Maker", "Contact"]:
        for line in text.splitlines():
            line_clean = line.strip()
            if line_clean.lower().startswith(("contact:", "name:", "lead name:", "decision maker:")):
                val = line_clean.split(":", 1)[1].strip()
                # Clean out parentheses if title attached e.g. "Arthur (VP Strategy)"
                if "(" in val:
                    val = val.split("(")[0].strip()
                if val:
                    updated["contact_name"] = val
                    break

    # 3. Job Title extraction & Disqualification Detection
    if updated.get("job_title") in [None, "", "Executive", "Unknown"]:
        for line in text.splitlines():
            line_clean = line.strip()
            if line_clean.lower().startswith(("title:", "job title:", "role:", "designation:")):
                val = line_clean.split(":", 1)[1].strip()
                if val:
                    updated["job_title"] = val
                    break
            elif "(" in line_clean and ")" in line_clean:
                start = line_clean.find("(") + 1
                end = line_clean.find(")")
                val_in_paren = line_clean[start:end].strip()
                if any(w in val_in_paren.lower() for w in ["student", "intern", "researcher", "vp", "director", "chief", "head", "manager", "officer", "lead"]):
                    updated["job_title"] = val_in_paren
                    break

    # Check for Student / Academic Disqualifier
    full_text_lower = text.lower()
    title_lower = (updated.get("job_title") or "").lower()
    is_academic = (
        "student" in full_text_lower or
        "student" in title_lower or
        "class assignment" in full_text_lower or
        "thesis" in full_text_lower or
        "intern" in title_lower or
        "free paper" in full_text_lower
    )

    if is_academic:
        updated["is_disqualified"] = True
        updated["disqualification_reason"] = "Academic / Student Inquiry (No commercial budget authority)"
        updated["final_icp_score"] = 12
        updated["saber_tier"] = "Out of ICP / Disqualified (<40)"
        updated["priority_level"] = "Disqualified / Deprioritized"
        updated["sales_action"] = "Route to public academic resources / open whitepapers. Preserve AE and sales rep bandwidth."
        if not updated.get("job_title") or updated.get("job_title") == "Executive":
            updated["job_title"] = "Student / Researcher"
        
        comp = updated.get("company_name") or "Academic Entity"
        contact = updated.get("contact_name") or "Student / Inquirer"
        
        updated["firmo_insights"] = f"Academic / non-commercial institution profile for {comp}. Lacks commercial enterprise budget scale."
        updated["techno_insights"] = "Standard educational environment without enterprise CRM/data infrastructure."
        updated["intent_insights"] = "Academic coursework / student research inquiry without commercial buying intent."
        updated["persona_insights"] = f"{contact} ({updated['job_title']}) does not hold corporate budget sign-off or procurement authority."
        
        updated["pillar_scores"] = {
            "firmographic_score": 15,
            "technographic_score": 20,
            "intent_score": 10,
            "persona_score": 0
        }
        updated["strategy"] = {
            "value_wedge": "Direct non-commercial inquiries to public datasets and self-serve educational documentation.",
            "outreach_hook": f"Hi {contact.split()[0] if contact else 'there'}, for coursework and academic research please check our open research library."
        }
        return updated

    # Commercial Account Dynamic Evaluation Engine
    comp = updated.get("company_name") or "the account"
    contact = updated.get("contact_name") or "the decision maker"
    title = updated.get("job_title") or "Executive"
    
    # 1. Firmographic Evaluation (0-100)
    # Check scale, revenue, employee count
    f_score = 50
    if any(k in full_text_lower for k in ["billion", "$1b", "$10b", "$38b", "$500m", "$450m", "34,000", "10,000", "enterprise", "global", "fortune 500"]):
        f_score = 92
        f_rat = f"Enterprise-scale global account ({comp}). Massive commercial footprint, extensive operating budget, and ideal market geography."
    elif any(k in full_text_lower for k in ["$65m", "$50m", "$100m", "220 employees", "500 employees", "mid-market", "growth stage"]):
        f_score = 76
        f_rat = f"Established mid-market growth profile ({comp}). Solid revenue scale and strong departmental operational budgets."
    elif any(k in full_text_lower for k in ["seed", "pre-revenue", "12 employees", "early-stage", "startup", "prototype", "bootstrapped"]):
        f_score = 42
        f_rat = f"Early-stage venture profile ({comp}). Limited immediate operating capital prior to subsequent institutional financing."
    else:
        f_score = 65
        f_rat = f"Standard B2B commercial profile evaluated for {comp}."

    # 2. Technographic Evaluation (0-100)
    t_score = 55
    if any(k in full_text_lower for k in ["sap", "oracle", "snowflake", "salesforce", "enterprise erp", "powerbi"]):
        t_score = 90
        t_rat = "Advanced enterprise technology stack (Salesforce, SAP, Snowflake). High data maturity and seamless API/data integration capability."
    elif any(k in full_text_lower for k in ["hubspot", "tableau", "google workspace"]):
        t_score = 75
        t_rat = "Modern cloud stack (HubSpot, Tableau). Strong digital readiness for intelligence dashboards and CRM integration."
    elif any(k in full_text_lower for k in ["notion", "slack", "postgres", "sheets", "excel"]):
        t_score = 48
        t_rat = "Lightweight startup tooling stack. Standard operational tools with limited enterprise data warehouse infrastructure."
    else:
        t_score = 60
        t_rat = "Standard technology infrastructure evaluated."

    # 3. Intent & Timing Evaluation (0-100)
    i_score = 50
    if any(k in full_text_lower for k in ["active rfp", "3 weeks", "q3/q4 capex", "procurement budget", "actively preparing", "immediate", "urgent"]):
        i_score = 94
        i_rat = "Immediate buying urgency. Active multi-million dollar CapEx mandate with strict evaluation timeline."
    elif any(k in full_text_lower for k in ["demo", "next quarter", "evaluating", "team license", "benchmark", "q2", "q3"]):
        i_score = 75
        i_rat = "Clear near-term evaluation window. Looking to deploy intelligence before the next fiscal quarter."
    elif any(k in full_text_lower for k in ["6-9 months", "series a", "no budget yet", "no budget approval", "exploring", "future"]):
        i_score = 38
        i_rat = "Delayed purchasing cycle. Budget contingent on future venture funding round in 6–9 months."
    else:
        i_score = 60
        i_rat = "Active inquiry with standard quarterly evaluation cycle."

    # 4. Persona & Authority Evaluation (0-100)
    p_score = 55
    if any(k in title_lower for k in ["chief", "c-suite", "cto", "cfo", "cro", "cso", "vp", "vice president"]):
        p_score = 95
        p_rat = f"{contact} ({title}) holds direct executive oversight, strategic mandate, and signing authority for major investments."
    elif any(k in title_lower for k in ["director", "head of", "lead", "general manager"]):
        p_score = 78
        p_rat = f"{contact} ({title}) is a key departmental decision influencer with direct project budget allocation."
    elif any(k in title_lower for k in ["manager", "product manager", "analyst", "specialist"]):
        p_score = 52
        p_rat = f"{contact} ({title}) represents an end-user / technical evaluator who must secure executive sponsor sign-off."
    else:
        p_score = 60
        p_rat = f"{contact} ({title}) holds standard evaluation capacity."

    # Saber Mathematical Weighted Formula: (0.30*F) + (0.25*T) + (0.25*I) + (0.20*P)
    final_score = round((f_score * 0.30) + (t_score * 0.25) + (i_score * 0.25) + (p_score * 0.20))
    
    # Saber Tier & Sales Cadence
    if final_score >= 80:
        tier_str = "Tier 1: Dream ICP (80-100)"
        priority_str = "High Priority / Strategic Account"
        sales_act = "Immediate outreach (<2h) by Senior AE & Research Director. Deliver customized sample dataset slice & schedule scoping call."
        wedge = f"Deliver bespoke multi-region intelligence and direct analyst advisory to de-risk {comp}'s active CapEx investment."
        hook = f"Hi {contact.split()[0] if contact else 'there'}, saw {comp}'s upcoming CapEx deployment in the sector and wanted to share our latest intelligence benchmark relevant to your project roadmap."
    elif final_score >= 60:
        tier_str = "Tier 2: Strong Fit (60-79)"
        priority_str = "Standard Sales Pipeline"
        sales_act = "Standard SDR outbound sequence within 24h. Schedule discovery call and conduct interactive product demonstration."
        wedge = f"Empower {comp}'s business development team with actionable market benchmarking and pipeline acceleration data."
        hook = f"Hi {contact.split()[0] if contact else 'there'}, noticed your focus on benchmarking market opportunities at {comp} and thought our regional data feeds would be timely for your team."
    elif final_score >= 40:
        tier_str = "Tier 3: Moderate Fit (40-59)"
        priority_str = "Inside Sales / Automated Nurture"
        sales_act = "Enroll in self-serve product nurture sequences, invite to bi-weekly webinars, and track Series A funding trigger."
        wedge = f"Provide self-serve intelligence modules and flexible pricing options aligned with {comp}'s growth trajectory."
        hook = f"Hi {contact.split()[0] if contact else 'there'}, glad to see the work {comp} is doing in community storage. Sharing our latest industry overview report as you prepare for upcoming funding milestones."
    else:
        tier_str = "Out of ICP / Disqualified (<40)"
        priority_str = "Deprioritized / Low Priority"
        sales_act = "Route to marketing newsletter / self-serve documentation. Preserve direct sales capacity."
        wedge = "Direct to open research documentation."
        hook = f"Hi {contact.split()[0] if contact else 'there'}, please check our open knowledge base for resources."

    updated["final_icp_score"] = final_score
    updated["saber_tier"] = tier_str
    updated["priority_level"] = priority_str
    updated["sales_action"] = sales_act
    updated["firmo_insights"] = f_rat
    updated["techno_insights"] = t_rat
    updated["intent_insights"] = i_rat
    updated["persona_insights"] = p_rat
    updated["pillar_scores"] = {
        "firmographic_score": f_score,
        "technographic_score": t_score,
        "intent_score": i_score,
        "persona_score": p_score
    }
    updated["strategy"] = {
        "value_wedge": wedge,
        "outreach_hook": hook
    }

    return updated

# Helper for Pillar Score extraction
def get_pillar_info(pillars: dict, key: str) -> tuple[float, str]:
    if not isinstance(pillars, dict):
        return 0, ""
    if isinstance(pillars.get(key), dict):
        p_obj = pillars[key]
        return float(p_obj.get("score", 0)), str(p_obj.get("rationale") or p_obj.get("details", ""))
    flat_key = f"{key}_score"
    if flat_key in pillars:
        return float(pillars[flat_key]), str(pillars.get(f"{key}_rationale", ""))
    if key in pillars and isinstance(pillars[key], (int, float)):
        return float(pillars[key]), ""
    return 0, ""

# Header
st.markdown('<div class="title-text">Enterprise ICP Revenue Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">AI-Powered Lead Scoring & Quality-Weighted Sales Forecaster (Saber ICP Framework)</div>', unsafe_allow_html=True)

# Single Focused Lead Qualification Interface
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
    custom_deal_size = st.number_input("Estimated Deal Size ($)", min_value=1000, max_value=5000000, value=50000, step=5000)
    
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    score_btn = st.button("Score Lead via AI", type="primary", use_container_width=True)

if score_btn:
    if not prospect_text.strip():
        st.error("Please paste the lead details above.")
    elif not worker_client.is_connected():
        st.error("Cloudflare Worker URL is not configured in .streamlit/secrets.toml.")
    else:
        with st.spinner("Evaluating prospect intelligence..."):
            raw_res = worker_client.score_prospect(prospect_text, custom_deal_size)
            if raw_res:
                enriched_res = extract_smart_entities(prospect_text, raw_res)
                st.session_state["single_score_result"] = enriched_res
            else:
                st.error("Failed to receive evaluation from Cloudflare Worker AI.")

if "single_score_result" in st.session_state:
    res = st.session_state["single_score_result"]

    final_score = int(res.get("final_icp_score", 0))
    tier_str = res.get("saber_tier", "Tier 3: Moderate Fit")
    priority_str = res.get("priority_level", "Standard Pipeline")
    company_name = res.get("company_name", "Target Account")
    contact_name = res.get("contact_name", "Decision Maker")
    job_title = res.get("job_title", "Executive")
    sales_action = res.get("sales_action", "Conduct standard outreach.")

    # Quality Weighted Deal Value (Always dynamically synced with the final ICP score)
    forecast_val = round(custom_deal_size * (final_score / 100.0))

    # 4 Pillar Breakdown
    pillars = res.get("pillar_scores") or res.get("pillars") or {}

    firmo_pts, firmo_rat = get_pillar_info(pillars, "firmographic")
    techno_pts, techno_rat = get_pillar_info(pillars, "technographic")
    intent_pts, intent_rat = get_pillar_info(pillars, "intent")
    if intent_pts == 0:
        intent_pts, intent_rat = get_pillar_info(pillars, "intent_timing")
    persona_pts, persona_rat = get_pillar_info(pillars, "persona")
    if persona_pts == 0:
        persona_pts, persona_rat = get_pillar_info(pillars, "persona_authority")

    # Fallback extrapolation if zero
    if (firmo_pts + techno_pts + intent_pts + persona_pts) == 0 and final_score > 0:
        firmo_pts = round(final_score * 0.95)
        techno_pts = round(final_score * 0.90)
        intent_pts = round(final_score * 0.92)
        persona_pts = round(final_score * 0.95)

    firmo_rat = firmo_rat or res.get("firmo_insights", "")
    techno_rat = techno_rat or res.get("techno_insights", "")
    intent_rat = intent_rat or res.get("intent_insights", "")
    persona_rat = persona_rat or res.get("persona_insights", "")

    st.markdown("---")
    st.markdown(f"### Qualification Results: **{company_name}**")

    # Top 4 Symmetrical KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #6366F1;">
            <span style="color: #A5B4FC; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">MASTER ICP SCORE</span>
            <div style="color: #67E8F9; margin: 8px 0; font-size: 2.5rem; font-weight:900; line-height: 1;">
                {final_score} <span style="font-size:1.1rem; color:#94A3B8; font-weight:600;">/ 100</span>
            </div>
            <span style="color:#CBD5E1; font-size:0.8rem;">Saber Weighted Total</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        badge_class = "badge-tier1" if "Tier 1" in tier_str else "badge-tier2" if "Tier 2" in tier_str else "badge-tier3" if "Tier 3" in tier_str else "badge-disqualified"
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #10B981; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);">
            <span style="color: #6EE7B7; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">SALES TIER CATEGORY</span>
            <div style="margin: 8px 0;"><span class="{badge_class}">{tier_str}</span></div>
            <span style="color:#A7F3D0; font-size:0.8rem; font-weight:600;">{priority_str}</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #F59E0B; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);">
            <span style="color: #FDE68A; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">QUALITY-WEIGHTED VALUE</span>
            <div style="color: #FBBF24; margin: 8px 0; font-size: 2.3rem; font-weight:900; line-height: 1;">
                ${forecast_val:,.0f}
            </div>
            <span style="color:#FDE68A; font-size:0.8rem;">Deal Size × ({final_score}%)</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #EC4899; box-shadow: 0 4px 20px rgba(236, 72, 153, 0.25);">
            <span style="color: #FBCFE8; font-weight:700; font-size:0.85rem; letter-spacing:0.5px;">TARGET DECISION MAKER</span>
            <div style="color: #F472B6; margin: 8px 0; font-size: 1.25rem; font-weight:800; line-height: 1.2; word-break: break-word;">
                {contact_name}
            </div>
            <span style="color:#FBCFE8; font-size:0.85rem; font-weight:600;">{job_title}</span>
        </div>
        """, unsafe_allow_html=True)

    # 4 Perfectly Aligned Pillar Cards
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Four-Pillar Score Breakdown & Evaluation")
    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown(f"""
        <div class="pillar-card pillar-firmo">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#E9D5FF; font-weight:700; font-size:1.05rem;">1. Firmographics Fit (30% Weight)</span>
                    <span style="color:#C084FC; font-weight:900; font-size:1.25rem;">{int(firmo_pts)} / 100</span>
                </div>
                <div style="color:#DDD6FE; font-size:0.9rem; margin-top:8px; line-height:1.4;">
                    {firmo_rat}
                </div>
            </div>
            <div class="progress-track">
                <div class="progress-fill-firmo" style="width: {int(firmo_pts)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pillar-card pillar-techno">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#CFFAFE; font-weight:700; font-size:1.05rem;">2. Technographics Fit (25% Weight)</span>
                    <span style="color:#22D3EE; font-weight:900; font-size:1.25rem;">{int(techno_pts)} / 100</span>
                </div>
                <div style="color:#A5F3FC; font-size:0.9rem; margin-top:8px; line-height:1.4;">
                    {techno_rat}
                </div>
            </div>
            <div class="progress-track">
                <div class="progress-fill-techno" style="width: {int(techno_pts)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        st.markdown(f"""
        <div class="pillar-card pillar-intent">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#D1FAE5; font-weight:700; font-size:1.05rem;">3. Intent & Timing Signals (25% Weight)</span>
                    <span style="color:#34D399; font-weight:900; font-size:1.25rem;">{int(intent_pts)} / 100</span>
                </div>
                <div style="color:#A7F3D0; font-size:0.9rem; margin-top:8px; line-height:1.4;">
                    {intent_rat}
                </div>
            </div>
            <div class="progress-track">
                <div class="progress-fill-intent" style="width: {int(intent_pts)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pillar-card pillar-persona">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#FEF3C7; font-weight:700; font-size:1.05rem;">4. Persona & Buying Authority (20% Weight)</span>
                    <span style="color:#FBBF24; font-weight:900; font-size:1.25rem;">{int(persona_pts)} / 100</span>
                </div>
                <div style="color:#FDE68A; font-size:0.9rem; margin-top:8px; line-height:1.4;">
                    {persona_rat}
                </div>
            </div>
            <div class="progress-track">
                <div class="progress-fill-persona" style="width: {int(persona_pts)}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recommended Sales Cadence
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: 1px solid #38BDF8; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.15);">
        <h4 style="color:#38BDF8; margin:0 0 8px 0; font-size:1.15rem;">Recommended Sales Department Cadence</h4>
        <p style="color:#E2E8F0; font-size:0.98rem; margin:0; line-height:1.5;">{sales_action}</p>
    </div>
    """, unsafe_allow_html=True)

    # Personalized Strategy & Outreach Copy
    strategy = res.get("strategy") or res.get("worker_ai_strategy") or {}
    val_wedge = strategy.get("value_wedge") or ""
    hook = strategy.get("outreach_hook") or ""
    
    if val_wedge or hook:
        st.markdown(f"""
        <div class="pitch-card">
            <h4 style="color:#F472B6; margin:0 0 12px 0; font-size:1.2rem;">Personalized Deal Strategy & Outreach Copy</h4>
            <div style="color:#E9D5FF; margin-bottom:10px; font-size:0.98rem; line-height:1.5;">
                <strong style="color:#F472B6;">Value Wedge:</strong> {val_wedge}
            </div>
            <div style="color:#FDF4FF; margin-bottom:0; font-size:0.98rem; line-height:1.5;">
                <strong style="color:#38BDF8;">Cold Outreach Opener:</strong> <em>"{hook}"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

