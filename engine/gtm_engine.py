"""
Enterprise ICP Revenue Intelligence - Streamlined 6-Field High-Velocity Engine.
Focuses on the essential 6 core signals that drive 90% of B2B qualification accuracy:
1. Company Name & Domain
2. Industry & Niche
3. Company Scale (Revenue & Headcount)
4. Location / Territory
5. Contact Role & Seniority
6. Buying Intent & Target Deal Size ($)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from .ai_analyzer import (
    AITextAnalyzer,
    RoleAIAnalysis,
    NicheAIAnalysis,
    IntentAIAnalysis,
    TechStackAIAnalysis
)


MASTER_INDUSTRY_SECTORS = [
    "Manufacturing & Industrial Goods",
    "Energy, Utilities & Renewables",
    "Technology, SaaS & IT",
    "Financial Services & FinTech",
    "Healthcare & Life Sciences",
    "Logistics, Freight & Supply Chain",
    "Retail, Wholesale & E-Commerce",
    "Construction & Real Estate",
    "Professional & Business Services",
    "Telecommunications & Media",
    "Education & Public Sector"
]

DISPOSABLE_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "proton.me", "protonmail.com", "tempmail.com", "mailinator.com"
}


# ==========================================
# 1. Company Standards Configuration (Settings)
# ==========================================
class CompanyStandardsConfig(BaseModel):
    company_name: str = "My Enterprise Revenue Org"
    min_deal_size_usd: float = 10000.0
    target_deal_size_usd: float = 50000.0
    min_company_revenue_usd: float = 2000000.0
    ideal_revenue_usd: float = 20000000.0
    min_headcount: int = 50
    ideal_headcount: int = 250
    target_focus_industries: List[str] = Field(default_factory=lambda: [
        "Manufacturing & Industrial Goods",
        "Energy, Utilities & Renewables",
        "Technology, SaaS & IT"
    ])
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "United Kingdom", "United Arab Emirates", "European Union",
        "Canada", "Australia", "Singapore", "India", "Germany", "France", "UAE", "UK", "USA"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: [
        "North Korea", "Iran", "Syria", "Cuba"
    ])
    weight_firmographics: float = 0.30
    weight_authority: float = 0.25
    weight_intent: float = 0.25
    weight_value: float = 0.20
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0


# ==========================================
# 2. Streamlined 6-Field Lead Submission
# ==========================================
class StreamlinedLeadForm(BaseModel):
    company_name: str = ""
    industry_sector: str = "Technology, SaaS & IT"
    sub_vertical: str = ""
    annual_revenue_usd: float = 0.0
    employee_count: int = 1
    location: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_role_title: str = ""
    contact_seniority: str = "Director (+3)"
    buying_intent: str = "Active Pricing Inquiry (+3)"
    target_deal_size_usd: float = 0.0
    tech_stack_notes: Optional[str] = ""


# ==========================================
# 3. Isolated Field Receipt & Output Models
# ==========================================
class FieldScoreReceipt(BaseModel):
    field_name: str
    pillar: str
    raw_value: Any
    gtm_points: int  # -5, -3, -1, +1, +3, +5
    rationale: str
    is_disqualifier: bool = False


class PillarScoreSummary(BaseModel):
    pillar_name: str
    score: float  # 0.0 to 100.0
    weight_pct: float
    field_receipts: List[FieldScoreReceipt] = Field(default_factory=list)


class StreamlinedScoringResult(BaseModel):
    company_name: str
    master_icp_score: float  # 0.0 to 100.0
    priority_tier: str  # Tier A1, Tier A2, Tier B1, Tier C, Disqualified
    is_disqualified: bool
    disqualification_reason: str
    urgency_sla: str
    recommended_channel: str
    value_wedge: str
    outreach_hook: str
    pillar_firmographics: PillarScoreSummary
    pillar_authority: PillarScoreSummary
    pillar_intent: PillarScoreSummary
    pillar_value: PillarScoreSummary
    ai_role: Optional[RoleAIAnalysis] = None
    ai_niche: Optional[NicheAIAnalysis] = None
    ai_intent: Optional[IntentAIAnalysis] = None
    ai_tech: Optional[TechStackAIAnalysis] = None
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)


# Backward compatibility aliases
LeadFormSubmission = StreamlinedLeadForm
GTMScoringResult = StreamlinedScoringResult


# ==========================================
# 4. Streamlined Calculation Engine
# ==========================================
class GTMScoringEngine:
    """
    Evaluates the 6 essential B2B signals against company standards with realistic calibration.
    """

    @classmethod
    def evaluate(
        cls,
        form: StreamlinedLeadForm,
        config: Optional[CompanyStandardsConfig] = None
    ) -> StreamlinedScoringResult:
        cfg = config or CompanyStandardsConfig()
        is_disqualified = False
        disq_reasons = []
        discovery_questions = []
        key_strengths = []
        key_risks = []

        def points_to_score(pts: List[int]) -> float:
            if not pts:
                return 50.0
            n = len(pts)
            norm = ((sum(pts) - (-5.0 * n)) / (10.0 * n)) * 100.0
            return max(0.0, min(100.0, norm))

        # Execute AI Semantic Analysis on Text Input Fields
        ai_role = AITextAnalyzer.analyze_role(form.contact_role_title)
        ai_niche = AITextAnalyzer.analyze_niche(form.sub_vertical, form.industry_sector)
        ai_intent = AITextAnalyzer.analyze_intent(form.buying_intent)
        ai_tech = AITextAnalyzer.analyze_tech_stack(form.tech_stack_notes or "")

        # -------------------------------------------------------------
        # 1. FIRMOGRAPHICS (Scale, Geography & Niche Fit)
        # -------------------------------------------------------------
        firmo_receipts = []

        # Revenue
        rev = form.annual_revenue_usd
        if rev >= cfg.ideal_revenue_usd:
            p_rev = 5
            r_rev = f"Revenue (${rev:,.0f}) exceeds ideal threshold (${cfg.ideal_revenue_usd:,.0f})"
            key_strengths.append(f"Enterprise Revenue: ${rev:,.0f} ARR")
        elif rev >= cfg.min_company_revenue_usd:
            p_rev = 3
            r_rev = f"Revenue (${rev:,.0f}) meets minimum viable standard"
        elif rev > 0:
            p_rev = -1
            r_rev = f"Revenue (${rev:,.0f}) is below minimum target"
            key_risks.append("Sub-scale revenue scale")
        else:
            p_rev = -1
            r_rev = "Revenue unstated"
            discovery_questions.append("What is your current annual operating budget?")

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Company Revenue", pillar="Firmographics", raw_value=f"${rev:,.0f}", gtm_points=p_rev, rationale=r_rev
        ))

        # Headcount
        hc = form.employee_count
        if hc >= cfg.ideal_headcount:
            p_hc = 5
            r_hc = f"Headcount ({hc:,}) indicates strong organizational scale"
            key_strengths.append(f"Headcount: {hc:,} employees")
        elif hc >= cfg.min_headcount:
            p_hc = 3
            r_hc = f"Headcount ({hc:,}) is within viable operating range"
        else:
            p_hc = 1
            r_hc = f"Small team ({hc:,}); limited seat expansion"

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Headcount Scale", pillar="Firmographics", raw_value=f"{hc:,} employees", gtm_points=p_hc, rationale=r_hc
        ))

        # Industry & AI Niche Analysis
        ind = form.industry_sector
        if ind in cfg.target_focus_industries:
            p_ind = 5
            r_ind = f"Target sweet-spot industry: {ind} [AI Niche: {ai_niche.market_complexity}]"
            key_strengths.append(f"Core Target Industry: {ind}")
        elif ai_niche.fit_points == 5:
            p_ind = 5
            r_ind = f"AI Classified High-Margin Vertical: {ai_niche.raw_niche} ({ai_niche.market_complexity})"
            key_strengths.append(f"High-Margin Sub-Vertical: {form.sub_vertical}")
        elif ind in MASTER_INDUSTRY_SECTORS:
            p_ind = 3
            r_ind = f"Established commercial B2B sector: {ind}"
        else:
            p_ind = 1
            r_ind = f"General commercial sector: {ind}"

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Industry & Niche Fit (AI)", pillar="Firmographics", raw_value=f"{ind} • {form.sub_vertical or 'General'}", gtm_points=p_ind, rationale=r_ind
        ))

        # Location
        loc = form.location.strip()
        is_proh = any(p.lower() in loc.lower() for p in cfg.prohibited_countries)
        if is_proh:
            p_loc = -5
            r_loc = f"Located in prohibited/sanctioned territory: {loc}"
            is_disqualified = True
            disq_reasons.append(r_loc)
        elif any(t.lower() in loc.lower() for t in cfg.tier1_territories):
            p_loc = 5
            r_loc = f"Tier 1 supported direct market: {loc}"
            key_strengths.append(f"Tier 1 Geography: {loc}")
        elif loc:
            p_loc = 3
            r_loc = f"Supported global territory: {loc}"
        else:
            p_loc = -1
            r_loc = "Location unstated"
            discovery_questions.append("Where is your operational headquarters located?")

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Location / Territory", pillar="Firmographics", raw_value=loc or "Unspecified", gtm_points=p_loc, rationale=r_loc, is_disqualifier=is_proh
        ))

        firmo_score = points_to_score([r.gtm_points for r in firmo_receipts])
        pillar_firmo = PillarScoreSummary(
            pillar_name="Firmographics Scale",
            score=firmo_score,
            weight_pct=cfg.weight_firmographics,
            field_receipts=firmo_receipts
        )

        # -------------------------------------------------------------
        # 2. DECISION AUTHORITY & PERSONA (AI Analyzed)
        # -------------------------------------------------------------
        auth_receipts = []
        email = form.contact_email.lower().strip()
        domain = email.split("@")[-1] if "@" in email else ""

        if domain in DISPOSABLE_DOMAINS:
            p_auth = -5
            r_auth = f"Personal freemail address (@{domain}); non-commercial inquiry"
            is_disqualified = True
            disq_reasons.append(f"Personal freemail domain (@{domain})")
        elif ai_role.is_disqualifier:
            p_auth = -5
            r_auth = f"AI Classified Non-Buyer Persona: {ai_role.seniority_level} ({form.contact_role_title})"
            is_disqualified = True
            disq_reasons.append(f"Non-buyer persona ({form.contact_role_title})")
        else:
            p_auth = ai_role.seniority_points
            r_auth = f"AI Role Analysis: {ai_role.seniority_level} • Persona: {ai_role.persona_type} • Dept: {ai_role.department}"
            if p_auth >= 5:
                key_strengths.append(f"Executive Economic Buyer: {form.contact_name or 'Champion'} ({form.contact_role_title}) [{ai_role.department}]")
            elif p_auth >= 3:
                key_strengths.append(f"Technical Champion: {form.contact_role_title} [{ai_role.department}]")
            else:
                discovery_questions.append(f"Who is the executive budget owner in {ai_role.department}?")

        auth_receipts.append(FieldScoreReceipt(
            field_name="Contact Role & Authority (AI)",
            pillar="Decision Authority",
            raw_value=f"{form.contact_name or 'Contact'} — {form.contact_role_title or 'Unspecified'} ({email or 'No email'})",
            gtm_points=p_auth,
            rationale=r_auth,
            is_disqualifier=domain in DISPOSABLE_DOMAINS or ai_role.is_disqualifier
        ))

        auth_score = points_to_score([r.gtm_points for r in auth_receipts])
        pillar_auth = PillarScoreSummary(
            pillar_name="Decision Authority",
            score=auth_score,
            weight_pct=cfg.weight_authority,
            field_receipts=auth_receipts
        )

        # -------------------------------------------------------------
        # 3. BUYING INTENT & VELOCITY (AI Analyzed)
        # -------------------------------------------------------------
        intent_receipts = []
        p_intent = ai_intent.intent_points
        r_intent = f"AI Intent Classification: {ai_intent.urgency_tier} • {ai_intent.rationale}"
        if ai_intent.timeline_detected:
            r_intent += f" [Timeline: {ai_intent.timeline_detected}]"

        if p_intent >= 5:
            key_strengths.append(f"High Intent Velocity: {ai_intent.urgency_tier}")
        elif p_intent == 1:
            discovery_questions.append("What is your targeted deployment / live go-date?")

        intent_receipts.append(FieldScoreReceipt(
            field_name="Buying Intent & Urgency (AI)", pillar="Buying Intent", raw_value=form.buying_intent or "Standard", gtm_points=p_intent, rationale=r_intent
        ))

        intent_score = points_to_score([r.gtm_points for r in intent_receipts])
        pillar_intent = PillarScoreSummary(
            pillar_name="Buying Intent & Velocity",
            score=intent_score,
            weight_pct=cfg.weight_intent,
            field_receipts=intent_receipts
        )

        # -------------------------------------------------------------
        # 4. CONTRACT VALUE & TECH STACK (AI Analyzed)
        # -------------------------------------------------------------
        val_receipts = []
        deal = form.target_deal_size_usd

        if deal >= cfg.target_deal_size_usd:
            p_deal = 5
            r_deal = f"Contract size (${deal:,.0f}) meets or exceeds ideal deal target (${cfg.target_deal_size_usd:,.0f})"
            key_strengths.append(f"Target Contract Size: ${deal:,.0f}")
        elif deal >= cfg.min_deal_size_usd:
            p_deal = 3
            r_deal = f"Contract size (${deal:,.0f}) meets minimum viable contract threshold"
        elif deal > 0:
            p_deal = -1
            r_deal = f"Contract size (${deal:,.0f}) is below minimum target"
            key_risks.append("Deal size is below ideal ACV threshold")
        else:
            p_deal = 1
            r_deal = "Target deal size unstated; defaulting to exploratory baseline"

        val_receipts.append(FieldScoreReceipt(
            field_name="Contract Size ($)", pillar="Contract Value", raw_value=f"${deal:,.0f}", gtm_points=p_deal, rationale=r_deal
        ))

        # Tech Stack Receipt (AI)
        if form.tech_stack_notes:
            val_receipts.append(FieldScoreReceipt(
                field_name="Tech Stack Ecosystem (AI)",
                pillar="Contract Value",
                raw_value=form.tech_stack_notes,
                gtm_points=ai_tech.tech_points,
                rationale=f"AI Stack Analysis: {ai_tech.ecosystem_fit} • {ai_tech.rationale}"
            ))
            if ai_tech.modern_tools:
                key_strengths.append(f"Modern Ecosystem Match: {', '.join(ai_tech.modern_tools)}")
            if ai_tech.legacy_blockers:
                key_risks.append(f"Legacy Architecture Detected: {', '.join(ai_tech.legacy_blockers)}")

        val_score = points_to_score([r.gtm_points for r in val_receipts])
        pillar_val = PillarScoreSummary(
            pillar_name="Contract Value & Scale",
            score=val_score,
            weight_pct=cfg.weight_value,
            field_receipts=val_receipts
        )

        # -------------------------------------------------------------
        # 5. MASTER SCORE & REALISTIC TIER CALIBRATION
        # -------------------------------------------------------------
        if is_disqualified:
            master_score = 0.0
            priority_tier = "Disqualified: Anti-ICP"
            urgency_sla = "No Outreach (Archived)"
            recommended_channel = "Do Not Contact"
            value_wedge = "Account does not meet commercial eligibility compliance."
            outreach_hook = "Disqualified inquiry."
        else:
            # Composite weighted calculation with enterprise calibration
            raw_composite = (
                (pillar_firmo.score * cfg.weight_firmographics)
                + (pillar_auth.score * cfg.weight_authority)
                + (pillar_intent.score * cfg.weight_intent)
                + (pillar_val.score * cfg.weight_value)
            )

            master_score = round(raw_composite, 1)

            if master_score >= cfg.tier_a1_threshold and pillar_intent.score >= 75.0:
                priority_tier = "Tier A1: Strategic Inbound"
                urgency_sla = "< 2 Hours (Executive Callback)"
                recommended_channel = "Direct Phone & Bespoke Executive Email"
            elif master_score >= cfg.tier_a2_threshold:
                priority_tier = "Tier A2: High Priority Outbound"
                urgency_sla = "< 24 Hours (Dedicated SDR Sequence)"
                recommended_channel = "Multi-Touch Email & LinkedIn InMail"
            elif master_score >= cfg.tier_b1_threshold:
                priority_tier = "Tier B1: Mid-Market Fast Track"
                urgency_sla = "Within 48 Hours"
                recommended_channel = "Inside Sales Discovery Call"
            else:
                priority_tier = "Tier C: Low Priority / Nurture"
                urgency_sla = "Automated Marketing Nurture"
                recommended_channel = "Marketing Newsletter & Documentation"

            # Dynamic Value Wedge & Hook
            sub_niche = form.sub_vertical or form.industry_sector
            comp = form.company_name or "your team"
            contact = form.contact_name or "there"
            
            value_wedge = f"Accelerate operational throughput for {sub_niche} initiatives at {comp}."
            outreach_hook = f"Hi {contact}, saw your initiative around {sub_niche} at {comp}—wanted to share how we support similar {ai_role.department} teams with tailored integration for your stack."

        return StreamlinedScoringResult(
            company_name=form.company_name,
            master_icp_score=master_score,
            priority_tier=priority_tier,
            is_disqualified=is_disqualified,
            disqualification_reason="; ".join(disq_reasons),
            urgency_sla=urgency_sla,
            recommended_channel=recommended_channel,
            value_wedge=value_wedge,
            outreach_hook=outreach_hook,
            pillar_firmographics=pillar_firmo,
            pillar_authority=pillar_auth,
            pillar_intent=pillar_intent,
            pillar_value=pillar_val,
            ai_role=ai_role,
            ai_niche=ai_niche,
            ai_intent=ai_intent,
            ai_tech=ai_tech,
            discovery_questions=discovery_questions,
            key_strengths=key_strengths,
            key_risks=key_risks
        )

