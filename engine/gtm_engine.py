"""
Enterprise ICP Revenue Intelligence - Dynamic GTM Engine.
All AI semantic analysis, role hierarchy, niche complexity, tech stack synergy,
and GTM Partners 4-Pillar reasoning are handled 100% dynamically by the Cloudflare Workers AI engine.
Includes deterministic policy rules (sanctions, anti-ICP roles), FX currency normalization,
and fail-loud observability.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Union, Tuple
try:
    from pydantic import BaseModel, Field
except (ImportError, ModuleNotFoundError):
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default

from engine.fx import FXEngine
from engine.rules import PolicyEngine, PolicyCheckResult

DEFAULT_WORKER_URL = os.environ.get(
    "ICP_WORKER_URL",
    "https://icp-revenue-intelligence-worker.devika-worker.workers.dev"
)


# ==============================================================================
# 1. AI Analysis & Output Data Models
# ==============================================================================

class RoleAIAnalysis(BaseModel):
    raw_title: str = ""
    seniority_level: str = "Individual Contributor (+1)"
    seniority_points: int = 1
    persona_type: str = "Technical Champion"
    department: str = "Operations"
    confidence: float = 0.90
    rationale: str = ""
    is_disqualifier: bool = False


class NicheAIAnalysis(BaseModel):
    raw_niche: str = ""
    suggested_sector: str = ""
    market_complexity: str = "Specialized Enterprise"
    fit_points: int = 3
    rationale: str = ""


class IntentAIAnalysis(BaseModel):
    raw_intent: str = ""
    urgency_tier: str = "Active Evaluation (+3)"
    intent_points: int = 3
    timeline_detected: Optional[str] = None
    extracted_signals: List[str] = Field(default_factory=list)
    rationale: str = ""


class TechStackAIAnalysis(BaseModel):
    raw_stack: str = ""
    modern_tools: List[str] = Field(default_factory=list)
    legacy_blockers: List[str] = Field(default_factory=list)
    ecosystem_fit: str = "Standard Modern Cloud (+3)"
    tech_points: int = 3
    rationale: str = ""


class FootprintAIAnalysis(BaseModel):
    headquarters: str = ""
    branch_locations: List[str] = Field(default_factory=list)
    total_locations: int = 1
    geographic_reach: str = "Multi-Region Enterprise"
    tier1_matches: List[str] = Field(default_factory=list)
    prohibited_matches: List[str] = Field(default_factory=list)
    footprint_points: int = 3
    rationale: str = ""


class CompanyStandardsConfig(BaseModel):
    company_name: str = "Blackridge Research & Consulting"
    currency_symbol: str = "$"
    currency_code: str = "USD"
    min_deal_size_usd: float = 5000.0
    target_deal_size_usd: float = 25000.0
    min_company_revenue_usd: float = 5000000.0
    ideal_revenue_usd: float = 50000000.0
    min_headcount: int = 20
    ideal_headcount: int = 500
    target_focus_industries: List[str] = Field(default_factory=lambda: [
        "Energy, Utilities & Renewables",
        "Infrastructure & Construction",
        "Oil, Gas & Petrochemicals",
        "Industrial Goods & Manufacturing",
        "Automotive & Electric Mobility",
        "Chemicals & Materials",
        "Technology & Telecom"
    ])
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "India", "Australia", "Singapore", "United Arab Emirates", "Saudi Arabia"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: [
        "North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"
    ])
    weight_firmographics: float = 0.30
    weight_authority: float = 0.25
    weight_intent: float = 0.25
    weight_value: float = 0.20
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0


class StreamlinedLeadForm(BaseModel):
    company_name: str = ""
    currency_symbol: str = "$"
    currency_code: str = "USD"
    revenue_entered_value: float = 0.0
    revenue_unit: str = "Standard"
    revenue_display_str: str = ""
    deal_entered_value: float = 0.0
    deal_unit: str = "Standard"
    deal_display_str: str = ""
    industry_sector: str = ""
    sub_vertical: str = ""
    annual_revenue_usd: float = 0.0
    employee_count: int = 0
    location: str = ""
    branch_locations: List[str] = Field(default_factory=list)
    contact_name: str = ""
    contact_email: str = ""
    contact_role_title: str = ""
    buying_role: str = ""
    buying_intent: str = ""
    timeline: str = ""
    target_deal_size_usd: float = 0.0
    tech_stack_notes: Optional[str] = ""
    uses_existing_platform: Optional[str] = ""
    existing_platform: Optional[str] = ""


class FieldScoreReceipt(BaseModel):
    field_name: str = ""
    pillar: str = ""
    raw_value: Any = None
    gtm_points: int = 0
    rationale: str = ""
    is_disqualifier: bool = False


class PillarScoreSummary(BaseModel):
    pillar_name: str
    score: float
    weight_pct: float
    field_receipts: List[FieldScoreReceipt] = Field(default_factory=list)


class ScoringTrackerItem(BaseModel):
    pillar_name: str
    allotted_score: float
    weight_pct: float
    points_contributed: float
    basis_criterion: str
    verified_signals: List[str] = Field(default_factory=list)
    deduction_gaps: List[str] = Field(default_factory=list)
    decision_rationale: str


class StreamlinedScoringResult(BaseModel):
    company_name: str
    master_icp_score: float
    priority_tier: str
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
    ai_footprint: Optional[FootprintAIAnalysis] = None
    scoring_tracker: List[ScoringTrackerItem] = Field(default_factory=list)
    lead_summary: Dict[str, Any] = Field(default_factory=dict)
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    analysis_mode: str = "live"  # "live" | "degraded" | "failed"
    degraded_reasons: List[str] = Field(default_factory=list)


# Backward compatibility aliases
LeadFormSubmission = StreamlinedLeadForm
GTMScoringResult = StreamlinedScoringResult


# ==============================================================================
# 2. Cloudflare Workers AI Client & GTM Scoring Engine
# ==============================================================================

class GTMScoringEngine:
    """
    Evaluates prospect leads by combining deterministic compliance policy checks,
    versioned FX currency normalization, and semantic AI reasoning.
    """

    @classmethod
    def query_ai_worker(
        cls,
        payload: Dict[str, Any],
        worker_url: Optional[str] = None,
        timeout: float = 25.0
    ) -> Optional[Dict[str, Any]]:
        url = worker_url or DEFAULT_WORKER_URL
        if not url:
            return None

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "EnterpriseICPClient/3.6 (Hardened-GTM-Bridge)",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except Exception:
            return None
        return None

    @classmethod
    def evaluate(
        cls,
        form: StreamlinedLeadForm,
        config: Optional[CompanyStandardsConfig] = None,
        worker_url: Optional[str] = None
    ) -> StreamlinedScoringResult:
        cfg = config or CompanyStandardsConfig()
        sym = form.currency_symbol or cfg.currency_symbol or "$"
        curr_code = form.currency_code or "USD"

        # 1. Normalize Native Currency to True USD (FX Engine)
        native_rev, norm_rev_usd = FXEngine.normalize_to_usd(
            form.revenue_entered_value,
            form.revenue_unit,
            curr_code
        )
        native_deal, norm_deal_usd = FXEngine.normalize_to_usd(
            form.deal_entered_value,
            form.deal_unit,
            curr_code
        )

        prospect_rev_str = form.revenue_display_str or f"{sym}{native_rev:,.0f} {curr_code}"
        prospect_deal_str = form.deal_display_str or f"{sym}{native_deal:,.0f} {curr_code}"

        # 2. Deterministic Policy & Compliance Check (Short-circuit on Sanctions/Anti-ICP)
        policy_res: PolicyCheckResult = PolicyEngine.evaluate_compliance(
            location=form.location,
            role_title=form.contact_role_title,
            prohibited_countries=cfg.prohibited_countries,
            min_deal_size_usd=cfg.min_deal_size_usd,
            target_deal_size_usd=norm_deal_usd
        )

        if policy_res.is_disqualified:
            empty_pillar = PillarScoreSummary(pillar_name="Disqualified", score=0.0, weight_pct=0.0, field_receipts=[])
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                priority_tier="Disqualified: Compliance / Anti-ICP",
                is_disqualified=True,
                disqualification_reason=policy_res.disqualification_reason,
                urgency_sla="No Outreach (Archived)",
                recommended_channel="Do Not Contact",
                value_wedge="Account is blocked by organizational compliance policy.",
                outreach_hook="Disqualified prospect.",
                pillar_firmographics=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="live",
                degraded_reasons=[],
                lead_summary={
                    "industry": form.industry_sector,
                    "location": form.location,
                    "contact_title": form.contact_role_title
                }
            )

        # 3. Build enriched payload for Cloudflare Workers AI
        worker_payload = {
            "company_name": form.company_name,
            "industry_sector": form.industry_sector,
            "sub_vertical": form.sub_vertical,
            "annual_revenue_usd": norm_rev_usd,
            "annual_revenue_native": native_rev,
            "stated_annual_revenue": prospect_rev_str,
            "currency_code": curr_code,
            "currency_symbol": sym,
            "revenue_unit": form.revenue_unit,
            "employee_count": form.employee_count,
            "location": form.location,
            "branch_locations": form.branch_locations,
            "contact_name": form.contact_name,
            "contact_email": form.contact_email,
            "contact_role_title": form.contact_role_title,
            "buying_role": form.buying_role,
            "buying_intent": form.buying_intent,
            "timeline": form.timeline,
            "target_deal_size_usd": norm_deal_usd,
            "target_deal_size_native": native_deal,
            "stated_deal_size": prospect_deal_str,
            "deal_unit": form.deal_unit,
            "tech_stack_notes": form.tech_stack_notes,
            "existing_platform": form.existing_platform or "",
            "company_standards": {
                "org_name": cfg.company_name,
                "target_focus_industries": cfg.target_focus_industries,
                "tier1_territories": cfg.tier1_territories,
                "prohibited_countries": cfg.prohibited_countries,
                "target_arr_usd": cfg.ideal_revenue_usd,
                "min_deal_size_usd": cfg.min_deal_size_usd,
                "target_deal_size_usd": cfg.target_deal_size_usd
            }
        }

        # 4. Query Cloudflare Workers AI
        ai_res = cls.query_ai_worker(worker_payload, worker_url=worker_url)

        # 5. Fail Loudly if AI is Unreachable (P0-1 Fix: Never silently fabricate fake scores)
        if not ai_res or "scores" not in ai_res:
            empty_pillar = PillarScoreSummary(pillar_name="Unavailable", score=0.0, weight_pct=0.0, field_receipts=[])
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                priority_tier="Evaluation Incomplete: AI Engine Offline",
                is_disqualified=False,
                disqualification_reason="AI service is currently unreachable. Scoring was halted to avoid data fabrication.",
                urgency_sla="Manual Review Required",
                recommended_channel="Hold for System Recovery",
                value_wedge="AI Analysis Engine is offline. Please check connection or retry shortly.",
                outreach_hook="AI Service Offline - Automated outreach hook generation suspended.",
                pillar_firmographics=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="failed",
                degraded_reasons=["Cloudflare Workers AI engine unreachable or timed out."],
                lead_summary={
                    "industry": form.industry_sector,
                    "location": form.location,
                    "contact_title": form.contact_role_title
                }
            )

        # 6. Parse Validated AI Analysis & Evidence
        raw_ai = ai_res.get("ai_analysis", {}) or {}
        raw_evidence = ai_res.get("evidence", {}) or {}
        raw_strategy = ai_res.get("strategy", {}) or {}
        raw_scores = ai_res.get("scores", {}) or {}

        # AI Role & Authority
        r_role = raw_ai.get("role", {})
        sen_level = r_role.get("seniority_level", "Individual Contributor (+1)")
        sen_pts = 5 if "+5" in sen_level else (3 if "+3" in sen_level else (-5 if "-5" in sen_level else 1))
        ai_role = RoleAIAnalysis(
            raw_title=form.contact_role_title,
            seniority_level=sen_level,
            seniority_points=sen_pts,
            persona_type=r_role.get("persona_type", "Technical Champion"),
            department=r_role.get("department", "Operations"),
            confidence=float(r_role.get("confidence", 0.95)),
            rationale=r_role.get("rationale", f"Authority evaluation for {form.contact_role_title or 'contact'}."),
            is_disqualifier="-5" in sen_level
        )

        # AI Niche & Market Complexity
        r_niche = raw_ai.get("niche", {})
        mkt_comp = r_niche.get("market_complexity", "Mid-Market Specialized")
        fit_pts = 5 if "High-Margin" in mkt_comp else (3 if "Mid-Market" in mkt_comp else 1)
        ai_niche = NicheAIAnalysis(
            raw_niche=form.sub_vertical,
            suggested_sector=form.industry_sector,
            market_complexity=mkt_comp,
            fit_points=fit_pts,
            rationale=r_niche.get("rationale", f"Market complexity analysis for {form.sub_vertical or form.industry_sector}.")
        )

        # AI Intent & Urgency
        r_readiness = raw_ai.get("readiness", {})
        urg_tier = r_readiness.get("urgency_tier", "Active Evaluation (+3)")
        intent_pts = 5 if "+5" in urg_tier else (3 if "+3" in urg_tier else 1)
        ai_intent = IntentAIAnalysis(
            raw_intent=form.buying_intent,
            urgency_tier=urg_tier,
            intent_points=intent_pts,
            timeline_detected=form.timeline or r_readiness.get("timeline_detected", "< 60 Days"),
            extracted_signals=r_readiness.get("catalysts", []),
            rationale=r_readiness.get("rationale", "Commercial intent velocity analysis.")
        )

        # AI Tech Stack Ecosystem
        r_tech = raw_ai.get("tech", {})
        eco_fit = r_tech.get("ecosystem_fit", "Standard Modern Cloud (+3)")
        tech_pts = 5 if "+5" in eco_fit else (3 if "+3" in eco_fit else (-3 if "-3" in eco_fit else -1))
        ai_tech = TechStackAIAnalysis(
            raw_stack=form.tech_stack_notes or "",
            modern_tools=r_tech.get("modern_tools", []),
            legacy_blockers=r_tech.get("legacy_blockers", []),
            ecosystem_fit=eco_fit,
            tech_points=tech_pts,
            rationale=r_tech.get("rationale", "Ecosystem integration compatibility analysis.")
        )

        # AI Global Footprint
        r_footprint = raw_ai.get("footprint", {})
        branches = [b.strip() for b in form.branch_locations if b.strip()]
        geo_reach = r_footprint.get("geographic_reach") or (
            "Global Multi-Region Enterprise" if len(branches) >= 2 else (
                "Cross-Border Multi-Branch" if len(branches) == 1 else "Single-Market Hub"
            )
        )
        ai_footprint = FootprintAIAnalysis(
            headquarters=form.location or "Primary Region",
            branch_locations=branches,
            total_locations=max(1, len(branches) + (1 if form.location else 0)),
            geographic_reach=geo_reach,
            tier1_matches=r_footprint.get("tier1_matches", []),
            prohibited_matches=r_footprint.get("prohibited_matches", []),
            footprint_points=5 if "Global" in geo_reach else 3,
            rationale=r_footprint.get("rationale", "Geographic footprint analysis.")
        )

        # -------------------------------------------------------------
        # 4-Pillar Scores (Evidence-based ingestion)
        # -------------------------------------------------------------
        firmo_score = float(raw_evidence.get("firmographic", {}).get("score", 70.0))
        techno_score = float(raw_evidence.get("technographic", {}).get("score", 65.0))
        qual_score = float(raw_evidence.get("qualifying", {}).get("score", 70.0))
        readiness_score = float(raw_evidence.get("readiness", {}).get("score", 70.0))

        firmo_pts = max(1, min(5, int(round(firmo_score / 20.0))))
        techno_pts = max(1, min(5, int(round(techno_score / 20.0))))

        pillar_firmo = PillarScoreSummary(
            pillar_name="Firmographics Scale",
            score=firmo_score,
            weight_pct=cfg.weight_firmographics,
            field_receipts=[
                FieldScoreReceipt(field_name="Company Revenue", pillar="Firmographics", raw_value=prospect_rev_str, gtm_points=firmo_pts, rationale=f"ARR: {prospect_rev_str} (~${norm_rev_usd:,.0f} USD)"),
                FieldScoreReceipt(field_name="Employee Headcount", pillar="Firmographics", raw_value=f"{form.employee_count:,} employees", gtm_points=firmo_pts, rationale=f"Headcount: {form.employee_count:,}"),
                FieldScoreReceipt(field_name="Industry & AI Niche", pillar="Firmographics", raw_value=f"{form.industry_sector} • {form.sub_vertical or 'General'}", gtm_points=ai_niche.fit_points, rationale=ai_niche.rationale),
                FieldScoreReceipt(field_name="Global Footprint (AI)", pillar="Firmographics", raw_value=geo_reach, gtm_points=ai_footprint.footprint_points, rationale=ai_footprint.rationale)
            ]
        )

        auth_val = f"{form.contact_role_title or 'Unspecified'} • {form.buying_role or ai_role.persona_type}" if form.buying_role else f"{form.contact_role_title or 'Unspecified'} ({ai_role.persona_type})"
        pillar_auth = PillarScoreSummary(
            pillar_name="Decision Authority",
            score=qual_score,
            weight_pct=cfg.weight_authority,
            field_receipts=[
                FieldScoreReceipt(field_name="Role Title & Buying Persona", pillar="Decision Authority", raw_value=auth_val, gtm_points=ai_role.seniority_points, rationale=ai_role.rationale)
            ]
        )

        intent_val = f"{form.buying_intent or 'Active Evaluation'} (Timeline: {form.timeline or ai_intent.timeline_detected})" if form.timeline else (form.buying_intent or "Standard")
        pillar_intent = PillarScoreSummary(
            pillar_name="Buying Intent & Velocity",
            score=readiness_score,
            weight_pct=cfg.weight_intent,
            field_receipts=[
                FieldScoreReceipt(field_name="Buying Intent & Timeline", pillar="Buying Intent", raw_value=intent_val, gtm_points=ai_intent.intent_points, rationale=ai_intent.rationale)
            ]
        )

        platform_raw = (form.uses_existing_platform or form.existing_platform or "").strip()
        if platform_raw:
            p_lower = platform_raw.lower()
            if p_lower in ["false", "no", "0", "none"]:
                platform_desc = "No Incumbent (Greenfield Lead)"
            elif p_lower in ["true", "yes", "1"]:
                platform_desc = "Has Existing Incumbent"
            else:
                platform_desc = f"Incumbent: {platform_raw}"
            tech_receipt_val = f"{form.tech_stack_notes} • {platform_desc}" if form.tech_stack_notes else platform_desc
        else:
            tech_receipt_val = form.tech_stack_notes or "Cloud Baseline"

        pillar_val = PillarScoreSummary(
            pillar_name="Technographics & Ecosystem Fit",
            score=techno_score,
            weight_pct=cfg.weight_value,
            field_receipts=[
                FieldScoreReceipt(field_name="Budget Range (ACV)", pillar="Commercial Scale", raw_value=prospect_deal_str, gtm_points=techno_pts, rationale=f"Budget: {prospect_deal_str} (~${norm_deal_usd:,.0f} USD)"),
                FieldScoreReceipt(field_name="Tech Stack Ecosystem (AI)", pillar="Technographics", raw_value=tech_receipt_val, gtm_points=ai_tech.tech_points, rationale=ai_tech.rationale)
            ]
        )

        # Master Score & Priority Tier Calculation
        raw_composite = (
            (pillar_firmo.score * cfg.weight_firmographics)
            + (pillar_auth.score * cfg.weight_authority)
            + (pillar_intent.score * cfg.weight_intent)
            + (pillar_val.score * cfg.weight_value)
        )
        master_score = round(raw_composite, 1)

        priority_tier = raw_scores.get("priority_tier") or (
            "Tier A1: Strategic Inbound" if master_score >= cfg.tier_a1_threshold else (
                "Tier A2: High Priority Outbound" if master_score >= cfg.tier_a2_threshold else (
                    "Tier B1: Mid-Market Fast Track" if master_score >= cfg.tier_b1_threshold else "Tier C: Low Priority / Nurture"
                )
            )
        )

        sub_niche = form.sub_vertical or form.industry_sector
        comp = form.company_name or "your team"
        contact = form.contact_name or "there"

        urgency_sla = raw_strategy.get("urgency_sla") or "< 24 Hours (Dedicated SDR Sequence)"
        recommended_channel = raw_strategy.get("recommended_channel") or "Multi-Touch Email & LinkedIn InMail"
        value_wedge = raw_strategy.get("value_wedge") or f"Accelerate strategic market intelligence for {sub_niche} initiatives at {comp}."
        outreach_hook = raw_strategy.get("outreach_hook") or f"Hi {contact}, noticed your team's focus on {sub_niche} at {comp}—wanted to share how {cfg.company_name} supports similar enterprise teams."

        discovery_questions = ai_res.get("discovery_questions", [])
        key_strengths = ai_res.get("key_strengths", [])
        key_risks = ai_res.get("key_risks", []) + policy_res.warnings

        # 4-Pillar Scoring Audit Trail & Decision Tracker
        ev_firmo = raw_evidence.get("firmographic", {})
        ev_techno = raw_evidence.get("technographic", {})
        ev_qual = raw_evidence.get("qualifying", {})
        ev_readiness = raw_evidence.get("readiness", {})

        tracker = [
            ScoringTrackerItem(
                pillar_name="1. Firmographics Scale",
                allotted_score=firmo_score,
                weight_pct=round(cfg.weight_firmographics * 100, 1),
                points_contributed=round(firmo_score * cfg.weight_firmographics, 2),
                basis_criterion=f"Annual ARR ({prospect_rev_str} / ~${norm_rev_usd:,.0f} USD), Headcount ({form.employee_count:,}), Niche Complexity ({ai_niche.market_complexity}), and Branch Footprint ({geo_reach}).",
                verified_signals=ev_firmo.get("evidence_points", [f"ARR: {prospect_rev_str}", f"Headcount: {form.employee_count:,} FTEs", f"Footprint: {geo_reach}"]),
                deduction_gaps=ev_firmo.get("missing_points", []),
                decision_rationale=ev_firmo.get("rationale", "") or f"Firmographic scale evaluation for {form.company_name or 'account'}."
            ),
            ScoringTrackerItem(
                pillar_name="2. Technographics & Ecosystem",
                allotted_score=techno_score,
                weight_pct=round(cfg.weight_value * 100, 1),
                points_contributed=round(techno_score * cfg.weight_value, 2),
                basis_criterion=f"Cloud ecosystem synergy ({ai_tech.ecosystem_fit}), modern stack tools, and absence of blocker legacy monoliths.",
                verified_signals=ev_techno.get("evidence_points", [f"Modern Stack Tools: {', '.join(ai_tech.modern_tools) if ai_tech.modern_tools else 'Cloud Baseline'}"]),
                deduction_gaps=ev_techno.get("missing_points", []),
                decision_rationale=ev_techno.get("rationale", "") or ai_tech.rationale
            ),
            ScoringTrackerItem(
                pillar_name="3. Decision Authority",
                allotted_score=qual_score,
                weight_pct=round(cfg.weight_authority * 100, 1),
                points_contributed=round(qual_score * cfg.weight_authority, 2),
                basis_criterion=f"Organizational seniority ({ai_role.seniority_level}), Buyer Persona ({ai_role.persona_type}), and budget ownership in {ai_role.department}.",
                verified_signals=ev_qual.get("evidence_points", [f"Contact: {form.contact_name or 'Unspecified'} ({ai_role.seniority_level})", f"Persona Archetype: {ai_role.persona_type}"]),
                deduction_gaps=ev_qual.get("missing_points", []),
                decision_rationale=ev_qual.get("rationale", "") or ai_role.rationale
            ),
            ScoringTrackerItem(
                pillar_name="4. Readiness to Buy",
                allotted_score=readiness_score,
                weight_pct=round(cfg.weight_intent * 100, 1),
                points_contributed=round(readiness_score * cfg.weight_intent, 2),
                basis_criterion=f"Commercial intent velocity ({ai_intent.urgency_tier}), stated buying horizon ({ai_intent.timeline_detected or '< 60 Days'}), and project triggers.",
                verified_signals=ev_readiness.get("evidence_points", [f"Buying Velocity: {ai_intent.urgency_tier}", f"Timeline: {ai_intent.timeline_detected or 'Immediate'}"]),
                deduction_gaps=ev_readiness.get("missing_points", []),
                decision_rationale=ev_readiness.get("rationale", "") or ai_intent.rationale
            )
        ]

        return StreamlinedScoringResult(
            company_name=form.company_name,
            master_icp_score=master_score,
            priority_tier=priority_tier,
            is_disqualified=False,
            disqualification_reason="",
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
            ai_footprint=ai_footprint,
            scoring_tracker=tracker,
            lead_summary={
                "industry": form.industry_sector,
                "sub_vertical": form.sub_vertical,
                "location": form.location,
                "branches": branches,
                "contact_title": form.contact_role_title,
                "buying_role": form.buying_role,
                "buying_intent": form.buying_intent,
                "timeline": form.timeline,
                "tech_stack": form.tech_stack_notes,
                "existing_platform": form.existing_platform or ""
            },
            discovery_questions=discovery_questions,
            key_strengths=key_strengths,
            key_risks=key_risks,
            analysis_mode="live",
            degraded_reasons=[]
        )
