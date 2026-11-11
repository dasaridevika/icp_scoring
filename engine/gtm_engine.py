"""
Enterprise ICP Revenue Intelligence - Dynamic GTM Engine.
All AI semantic analysis, role hierarchy, niche complexity, tech stack synergy,
and GTM 4-Pillar reasoning follow the Section 6 Authoritative Rubric.
Includes deterministic compliance rules, versioned FX currency normalization,
coverage-weighted mathematical scoring, and fail-loud observability.
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
        def model_dump(self):
            return self.__dict__
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default

from engine.fx import FXEngine
from engine.rules import PolicyEngine, PolicyCheckResult, matches_whole_word, DEFAULT_PROHIBITED_COUNTRIES

# Read worker URL strictly from environment
DEFAULT_WORKER_URL = os.environ.get("ICP_WORKER_URL", "")


# ==============================================================================
# 1. AI Analysis & Output Data Models
# ==============================================================================

class RoleAIAnalysis(BaseModel):
    raw_title: str = ""
    seniority_level: str = "Unspecified"
    seniority_points: int = 1
    persona_type: str = "Unspecified"
    department: str = "Unspecified"
    confidence: float = 0.90
    rationale: str = ""
    is_disqualifier: bool = False


class NicheAIAnalysis(BaseModel):
    raw_niche: str = ""
    suggested_sector: str = ""
    market_complexity: str = "Specialized Enterprise"
    fit_points: int = 3
    rationale: str = ""


class OfferingAIAnalysis(BaseModel):
    offering_category: str = "Product & Solution Offerings"
    matched_offerings: List[str] = Field(default_factory=list)
    fit_points: int = 3
    rationale: str = ""


class IntentAIAnalysis(BaseModel):
    raw_intent: str = ""
    urgency_tier: str = "Unspecified"
    intent_points: int = 0
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
    core_offerings: List[str] = Field(default_factory=lambda: [
        "Project Tracking Databases (Data Centers, Power, Oil & Gas, Hydrogen, Construction, Institutional Buildings, Telecom, Rail, Airports, Manufacturing, Chemicals, Metals, Mining, CCUS, BESS, Semiconductors, Solar)",
        "Syndicated Market Research Reports",
        "Custom Research",
        "Consulting",
    ])
    target_focus_industries: List[str] = Field(default_factory=lambda: [
        "Data Centers",
        "Power & Transmission",
        "Energy, Utilities & Renewables",
        "Oil & Gas / Petrochemicals",
        "Hydrogen",
        "Infrastructure & Construction",
        "Institutional Buildings",
        "Telecom",
        "Rail",
        "Airports",
        "Industrial Goods & Manufacturing",
        "Chemicals",
        "Metals",
        "Mining",
        "CCUS",
        "BESS",
        "Semiconductors",
        "Solar",
    ])
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "India", "Australia", "Singapore", "United Arab Emirates", "Saudi Arabia"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: list(DEFAULT_PROHIBITED_COUNTRIES))
    # Authoritative Section 6 Rubric Weights
    weight_firmographics: float = 0.35
    weight_offering: float = 0.25
    weight_authority: float = 0.25
    weight_intent: float = 0.15
    # Backward compatibility alias
    weight_value: float = 0.25

    # Authoritative Section 6 Tiers & Coverage Threshold
    tier_a_threshold: float = 80.0
    tier_b_threshold: float = 60.0
    tier_c_threshold: float = 40.0
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0
    min_coverage_threshold: float = 60.0


class StreamlinedLeadForm(BaseModel):
    company_name: str = ""
    currency_symbol: str = "$"
    currency_code: str = "USD"
    deal_currency_code: Optional[str] = None
    deal_currency_symbol: Optional[str] = None
    revenue_entered_value: float = 0.0
    revenue_unit: str = "Standard"
    revenue_display_str: str = ""
    deal_entered_value: float = 0.0
    deal_unit: str = "Standard"
    deal_display_str: str = ""
    industry_sector: str = ""
    sub_vertical: str = ""
    annual_revenue_usd: Optional[float] = None
    employee_count: Optional[int] = None
    location: str = ""
    branch_locations: List[str] = Field(default_factory=list)
    contact_name: str = ""
    contact_email: str = ""
    contact_role_title: str = ""
    buying_role: str = ""
    buying_intent: str = ""
    timeline: str = ""
    offering_interest: str = ""
    target_deal_size_usd: Optional[float] = None
    tech_stack_notes: Optional[str] = ""
    uses_existing_platform: Optional[str] = ""
    existing_platform: Optional[str] = ""

    def __init__(self, **data):
        str_fields = {
            "company_name", "currency_symbol", "currency_code", "revenue_unit",
            "revenue_display_str", "deal_unit", "deal_display_str", "industry_sector",
            "sub_vertical", "location", "contact_name", "contact_email",
            "contact_role_title", "buying_role", "buying_intent", "timeline",
            "offering_interest", "tech_stack_notes", "uses_existing_platform",
            "existing_platform",
        }
        for field in str_fields:
            if field in data and data[field] is None:
                data[field] = ""
        for num_field in ("revenue_entered_value", "deal_entered_value"):
            if num_field in data and data[num_field] is None:
                data[num_field] = 0.0
        super().__init__(**data)


FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "zoho.com", "mail.com", "protonmail.com", "proton.me",
    "gmx.com", "yandex.com", "fastmail.com", "live.com", "msn.com"
}


def _clean_str(val: Any) -> Optional[str]:
    """Return stripped text or None for empty / placeholder tokens."""
    if val is None or isinstance(val, bool):
        return None
    s = str(val).strip()
    if s.lower() in {"unknown", "null", "none", "undefined", "n/a", ""}:
        return None
    return s


def _has_text(val: Optional[str]) -> bool:
    """Return True when value has non-placeholder text."""
    return bool(_clean_str(val))


def _one_line_text(val: Any) -> str:
    """Collapse line breaks and repeated whitespace into a single line."""
    if val is None or isinstance(val, bool):
        return ""
    return " ".join(str(val).split())


class FieldScoreReceipt(BaseModel):
    field_name: str = ""
    pillar: str = ""
    raw_value: Any = None
    gtm_points: int = 0
    rationale: str = ""
    is_disqualifier: bool = False


class PillarScoreSummary(BaseModel):
    pillar_name: str
    rating: Optional[int] = None       # 1 to 5, or None if UNKNOWN
    score: Optional[float] = None      # rating * 20, or None if UNKNOWN
    weight_pct: float = 0.0
    is_known: bool = True
    status: str = "VERIFIED"           # "VERIFIED", "INFERRED", "UNKNOWN"
    rationale: str = ""
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
    company_name: str = ""
    master_icp_score: float = 0.0
    coverage_pct: float = 100.0
    priority_tier: str = ""
    is_disqualified: bool = False
    disqualification_reason: str = ""
    needs_review_reason: str = ""
    urgency_sla: str = ""
    recommended_channel: str = ""
    value_wedge: str = ""
    outreach_hook: str = ""
    pillar_firmographics: PillarScoreSummary
    pillar_offering: PillarScoreSummary
    pillar_authority: PillarScoreSummary
    pillar_intent: PillarScoreSummary
    pillar_value: Optional[PillarScoreSummary] = None
    ai_role: Optional[RoleAIAnalysis] = None
    ai_niche: Optional[NicheAIAnalysis] = None
    ai_intent: Optional[IntentAIAnalysis] = None
    ai_tech: Optional[TechStackAIAnalysis] = None
    ai_offering: Optional[OfferingAIAnalysis] = None
    ai_footprint: Optional[FootprintAIAnalysis] = None
    scoring_tracker: List[ScoringTrackerItem] = Field(default_factory=list)
    lead_summary: Dict[str, Any] = Field(default_factory=dict)
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    analysis_mode: str = "live"  # "live" | "degraded" | "failed"
    degraded_reasons: List[str] = Field(default_factory=list)
    model_used: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if self.pillar_value is None and hasattr(self, "pillar_offering"):
            self.pillar_value = self.pillar_offering


# Backward compatibility aliases
LeadFormSubmission = StreamlinedLeadForm
GTMScoringResult = StreamlinedScoringResult


# ==============================================================================
# 2. GTM Scoring Engine & Cloudflare Workers AI Client
# ==============================================================================

class GTMScoringEngine:
    """
    Authoritative GTM ICP Scoring Engine (Section 6 Rubric).
    Deterministic Policy Checks -> Normalized FX -> AI 1-5 Ratings -> Weighted Math Scoring & Tiering in Python.
    """

    @classmethod
    def query_ai_worker(
        cls,
        payload: Dict[str, Any],
        worker_url: Optional[str] = None,
        worker_key: Optional[str] = None,
        timeout: float = 25.0
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        url = worker_url or DEFAULT_WORKER_URL
        if not url:
            return None, "Worker URL is not configured. Set ICP_WORKER_URL environment variable or specify worker_url."

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EnterpriseICPClient/3.6 (Hardened-GTM-Bridge)",
            "Accept": "application/json"
        }
        if worker_key:
            headers["Authorization"] = f"Bearer {worker_key}"

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    resp_body = response.read().decode("utf-8")
                    return json.loads(resp_body), None
                return None, f"Worker returned unexpected HTTP {response.status}"
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_detail = err_json.get("error", err_json)
            except Exception:
                err_detail = e.reason
            return None, f"Worker HTTP {e.code}: {err_detail}"
        except urllib.error.URLError as e:
            return None, f"Network connection failed: {e.reason}"
        except TimeoutError:
            return None, f"Request timed out after {timeout}s"
        except json.JSONDecodeError as e:
            return None, f"Malformed JSON from worker: {str(e)}"
        except Exception as e:
            return None, f"Worker call error: {str(e)}"

    @classmethod
    def evaluate(
        cls,
        form: StreamlinedLeadForm,
        config: Optional[CompanyStandardsConfig] = None,
        worker_url: Optional[str] = None,
        worker_key: Optional[str] = None
    ) -> StreamlinedScoringResult:
        cfg = config or CompanyStandardsConfig()
        sym = form.currency_symbol or cfg.currency_symbol or "$"
        curr_code = form.currency_code or "USD"
        deal_curr_code = form.deal_currency_code or form.currency_code or "USD"
        deal_sym = form.deal_currency_symbol or form.currency_symbol or "$"

        # -------------------------------------------------------------
        # 1. FX Normalization (Unified Field Ingestion - Bug 3.3, 3.4, 3.6)
        # -------------------------------------------------------------
        # Revenue
        native_rev = None
        norm_rev_usd = None
        prospect_rev_str = "Unknown"
        if form.revenue_entered_value > 0:
            native_rev, norm_rev_usd = FXEngine.normalize_to_usd(
                form.revenue_entered_value,
                form.revenue_unit,
                curr_code
            )
            prospect_rev_str = form.revenue_display_str or f"{sym}{form.revenue_entered_value:g} {form.revenue_unit} ({curr_code})"
        elif form.annual_revenue_usd is not None and form.annual_revenue_usd > 0:
            norm_rev_usd = float(form.annual_revenue_usd)
            native_rev = norm_rev_usd
            prospect_rev_str = f"${norm_rev_usd:,.0f} USD"

        # Deal Size / Budget (converted with deal currency, not revenue currency)
        native_deal = None
        norm_deal_usd = None
        prospect_deal_str = "Unknown"
        if form.deal_entered_value > 0:
            native_deal, norm_deal_usd = FXEngine.normalize_to_usd(
                form.deal_entered_value,
                form.deal_unit,
                deal_curr_code
            )
            prospect_deal_str = form.deal_display_str or f"{deal_sym}{form.deal_entered_value:g} {form.deal_unit} ({deal_curr_code})"
        elif form.target_deal_size_usd is not None and form.target_deal_size_usd > 0:
            norm_deal_usd = float(form.target_deal_size_usd)
            native_deal = norm_deal_usd
            prospect_deal_str = f"${norm_deal_usd:,.0f} USD"

        # Headcount
        hc_val = form.employee_count if (form.employee_count is not None and form.employee_count > 0) else None
        hc_str = f"{hc_val:,} employees" if hc_val is not None else "Unknown"

        # -------------------------------------------------------------
        # 2. Hard Stops: Deterministic Compliance Check (Step 1)
        # -------------------------------------------------------------
        policy_res: PolicyCheckResult = PolicyEngine.evaluate_compliance(
            location=form.location,
            role_title=form.contact_role_title,
            branch_locations=form.branch_locations,
            prohibited_countries=cfg.prohibited_countries,
            min_deal_size_usd=cfg.min_deal_size_usd,
            target_deal_size_usd=norm_deal_usd or 0.0
        )

        if policy_res.is_disqualified:
            empty_pillar = PillarScoreSummary(
                pillar_name="Disqualified",
                rating=None,
                score=0.0,
                weight_pct=0.0,
                is_known=False,
                status="UNKNOWN",
                rationale=_one_line_text(policy_res.disqualification_reason) or "Blocked by compliance policy."
            )
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                coverage_pct=0.0,
                priority_tier="Disqualified: Anti-ICP",
                is_disqualified=True,
                disqualification_reason=policy_res.disqualification_reason,
                needs_review_reason="",
                urgency_sla="No Outreach (Archived)",
                recommended_channel="Do Not Contact",
                value_wedge="Account is blocked by organizational compliance policy.",
                outreach_hook="Disqualified prospect.",
                pillar_firmographics=empty_pillar,
                pillar_offering=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="live",
                degraded_reasons=[],
                lead_summary={
                    "industry": form.industry_sector or "Unknown",
                    "location": form.location or "Unknown",
                    "contact_title": form.contact_role_title or "Unknown"
                }
            )

        # -------------------------------------------------------------
        # 3. AI Worker Query & Fail-Loud Observability
        # -------------------------------------------------------------
        summary_lines = []
        if form.company_name: summary_lines.append(f"Company: {form.company_name}")
        if form.industry_sector: summary_lines.append(f"Industry: {form.industry_sector}")
        if form.sub_vertical and form.sub_vertical != form.industry_sector: summary_lines.append(f"Sub-vertical / Specialty: {form.sub_vertical}")
        if form.offering_interest: summary_lines.append(f"Offering Interest: {form.offering_interest}")
        if form.location: summary_lines.append(f"Headquarters: {form.location}")
        if form.branch_locations: summary_lines.append(f"Branch Locations: {', '.join(form.branch_locations)}")
        if form.contact_email: summary_lines.append(f"Work Email: {form.contact_email}")
        if hc_val: summary_lines.append(f"Headcount: {hc_val}")
        if prospect_rev_str != "Unknown": summary_lines.append(f"Annual Revenue: {prospect_rev_str}")
        if form.contact_name: summary_lines.append(f"Contact Name: {form.contact_name}")
        if form.contact_role_title: summary_lines.append(f"Role Title: {form.contact_role_title}")
        if form.buying_role: summary_lines.append(f"Buying Role: {form.buying_role}")
        if form.timeline: summary_lines.append(f"Timeline: {form.timeline}")
        if form.buying_intent: summary_lines.append(f"Buying Intent: {form.buying_intent}")
        if form.existing_platform: summary_lines.append(f"Uses Existing Platform: {form.existing_platform}")
        if prospect_deal_str != "Unknown": summary_lines.append(f"Budget / Deal Size: {prospect_deal_str}")

        lead_text_summary = "\n".join(summary_lines)

        worker_payload = {
            "text": lead_text_summary,
            "prospect_text": lead_text_summary,
            "company_name": form.company_name,
            "industry_sector": form.industry_sector or None,
            "sub_vertical": form.sub_vertical or None,
            "annual_revenue_usd": norm_rev_usd,
            "annual_revenue_native": native_rev,
            "stated_annual_revenue": prospect_rev_str if prospect_rev_str != "Unknown" else None,
            "currency_code": curr_code,
            "currency_symbol": sym,
            "deal_currency_code": deal_curr_code,
            "revenue_unit": form.revenue_unit,
            "employee_count": hc_val,
            "location": form.location or None,
            "branch_locations": form.branch_locations,
            "contact_name": form.contact_name or None,
            "contact_email": form.contact_email or None,
            "contact_role_title": form.contact_role_title or None,
            "buying_role": form.buying_role or None,
            "buying_intent": form.buying_intent or None,
            "timeline": form.timeline or None,
            "offering_interest": form.offering_interest or None,
            "target_deal_size_usd": norm_deal_usd,
            "target_deal_size_native": native_deal,
            "stated_deal_size": prospect_deal_str if prospect_deal_str != "Unknown" else None,
            "deal_unit": form.deal_unit,
            "existing_platform": form.existing_platform or None,
            "company_standards": {
                "org_name": cfg.company_name,
                "core_offerings": cfg.core_offerings,
                "target_focus_industries": cfg.target_focus_industries,
                "tier1_territories": cfg.tier1_territories,
                "prohibited_countries": cfg.prohibited_countries,
                "target_arr_usd": cfg.ideal_revenue_usd,
                "min_deal_size_usd": cfg.min_deal_size_usd,
                "target_deal_size_usd": cfg.target_deal_size_usd
            }
        }

        ai_res, worker_err = cls.query_ai_worker(
            payload=worker_payload,
            worker_url=worker_url,
            worker_key=worker_key
        )

        # Fail loudly if AI is unreachable (Bug 5.1, P0-1 fix)
        if not ai_res or worker_err:
            err_msg = worker_err or "AI engine service unreachable or timed out."
            empty_pillar = PillarScoreSummary(
                pillar_name="Unavailable",
                rating=None,
                score=0.0,
                weight_pct=0.0,
                is_known=False,
                status="UNKNOWN",
                rationale=_one_line_text(err_msg)
            )
            return StreamlinedScoringResult(
                company_name=form.company_name or "Unspecified",
                master_icp_score=0.0,
                coverage_pct=0.0,
                priority_tier="Evaluation Incomplete: AI Engine Offline",
                is_disqualified=False,
                disqualification_reason="",
                needs_review_reason="",
                urgency_sla="Manual Review Required",
                recommended_channel="Hold for System Recovery",
                value_wedge="AI Analysis Engine is offline. Please check connection or retry shortly.",
                outreach_hook="AI Service Offline - Automated outreach hook generation suspended.",
                pillar_firmographics=empty_pillar,
                pillar_offering=empty_pillar,
                pillar_authority=empty_pillar,
                pillar_intent=empty_pillar,
                pillar_value=empty_pillar,
                analysis_mode="failed",
                degraded_reasons=[err_msg],
                lead_summary={
                    "industry": form.industry_sector or "Unknown",
                    "location": form.location or "Unknown",
                    "contact_title": form.contact_role_title or "Unknown"
                }
            )

        # -------------------------------------------------------------
        # 4. Ingest AI Evidence & Strategy Receipts
        # (Only deterministic Python rules evaluate disqualification; AI provides ratings & strategic insights)
        # -------------------------------------------------------------
        raw_evidence = ai_res.get("evidence", {}) or {}
        raw_ai = ai_res.get("ai_analysis", {}) or {}
        raw_strategy = ai_res.get("strategy", {}) or {}
        model_used = str(ai_res.get("model_used", ai_res.get("model", "")))

        # -------------------------------------------------------------
        # 5. Extract Evidence & Ratings 1–5 (Section 6.3)
        # -------------------------------------------------------------

        def extract_rating(p_data: Dict[str, Any], has_data: bool) -> Tuple[Optional[int], str, str]:
            """Extracts rating (1 to 5) or None for Unknown."""
            if not has_data or not p_data:
                return None, "UNKNOWN", "No verified data provided."
            status = str(p_data.get("status", "")).upper()
            if status == "UNKNOWN":
                return None, "UNKNOWN", str(p_data.get("rationale", "No verified data provided."))

            # 1. Direct rating 1-5
            if "rating" in p_data and p_data["rating"] is not None:
                try:
                    r = int(p_data["rating"])
                    if 1 <= r <= 5:
                        return r, ("VERIFIED" if status == "VERIFIED" else "INFERRED"), str(p_data.get("rationale", ""))
                except (ValueError, TypeError):
                    pass

            # 2. Score mapping (0-100 -> 1-5)
            if "score" in p_data and p_data["score"] is not None:
                try:
                    s = float(p_data["score"])
                    if s > 0:
                        r = max(1, min(5, int(round(s / 20.0))))
                        return r, ("VERIFIED" if status == "VERIFIED" else "INFERRED"), str(p_data.get("rationale", ""))
                except (ValueError, TypeError):
                    pass

            return None, "UNKNOWN", str(p_data.get("rationale", "No verified data provided."))

        # Pillar 1: Firmographic Fit (35%)
        # Note: company_name alone does NOT count as firmographic data
        has_firmo_data = bool(
            _has_text(form.industry_sector)
            or (_has_text(form.sub_vertical) and form.sub_vertical.strip() != (form.company_name or "").strip())
            or (norm_rev_usd is not None and norm_rev_usd > 0)
            or (hc_val is not None and hc_val > 0)
            or _has_text(form.location)
            or any(_has_text(b) for b in form.branch_locations)
            or _has_text(form.contact_email)
        )
        ev_firmo = raw_evidence.get("firmographic", {})
        firmo_rating, firmo_status, firmo_rationale = extract_rating(ev_firmo, has_firmo_data)
        firmo_pts = firmo_rating or 0

        # Sub-AI: Role, Niche, Intent, Offering/Tech, Footprint
        r_role = raw_ai.get("role") or {}
        role_seniority = _clean_str(r_role.get("seniority_level")) or "Unspecified"
        try:
            role_conf = float(r_role.get("confidence")) if r_role.get("confidence") is not None else 0.90
        except (TypeError, ValueError):
            role_conf = 0.90
        ai_role = RoleAIAnalysis(
            raw_title=form.contact_role_title,
            seniority_level=role_seniority,
            seniority_points=5 if "+5" in role_seniority else (3 if "+3" in role_seniority else 1),
            persona_type=_clean_str(r_role.get("persona_type")) or "Unspecified",
            department=_clean_str(r_role.get("department")) or "Unspecified",
            confidence=role_conf,
            rationale=_clean_str(r_role.get("rationale")) or "Role authority analysis.",
            is_disqualifier="-5" in role_seniority
        )

        r_niche = raw_ai.get("niche") or {}
        ai_niche = NicheAIAnalysis(
            raw_niche=form.sub_vertical,
            suggested_sector=form.industry_sector,
            market_complexity=_clean_str(r_niche.get("market_complexity")) or "Specialized Enterprise",
            fit_points=3,
            rationale=_clean_str(r_niche.get("rationale")) or "Market complexity analysis."
        )

        r_readiness = raw_ai.get("readiness") or {}
        urgency_tier = _clean_str(r_readiness.get("urgency_tier")) or "Unspecified"
        ai_intent = IntentAIAnalysis(
            raw_intent=form.buying_intent,
            urgency_tier=urgency_tier,
            intent_points=5 if "+5" in urgency_tier else (3 if "+3" in urgency_tier else 0),
            timeline_detected=_clean_str(r_readiness.get("timeline_detected")) or (_clean_str(form.timeline)),
            rationale=_clean_str(r_readiness.get("rationale")) or "Intent and timeline analysis."
        )

        r_footprint = raw_ai.get("footprint") or {}
        ai_footprint = FootprintAIAnalysis(
            headquarters=form.location,
            branch_locations=form.branch_locations,
            total_locations=1 + len(form.branch_locations),
            geographic_reach=_clean_str(r_footprint.get("geographic_reach")) or "Multi-Region Enterprise",
            footprint_points=3,
            rationale=_clean_str(r_footprint.get("rationale")) or "Geographic footprint analysis."
        )

        # Pillar 1 receipts: only attribute positive points to verified signals
        rev_known = bool(norm_rev_usd is not None and norm_rev_usd > 0)
        hc_known = bool(hc_val is not None and hc_val > 0)
        ind_known = bool(_has_text(form.industry_sector) or _has_text(form.sub_vertical))
        geo_known = bool(_has_text(form.location) or any(_has_text(b) for b in form.branch_locations))

        # Email evaluation (business vs free email)
        email_val = (form.contact_email or "").strip()
        email_domain = email_val.split("@")[-1].lower() if "@" in email_val else ""
        is_free_domain = email_domain in FREE_EMAIL_DOMAINS

        if email_val and "@" in email_val and not is_free_domain:
            email_pts = firmo_pts if (firmo_pts > 0) else 0
            email_rat = f"Corporate business email domain (@{email_domain}) verified."
            email_raw = f"Business Domain (@{email_domain})"
        elif email_val and is_free_domain:
            email_pts = 0
            email_rat = f"Free/public email provider (@{email_domain}) detected; lacks corporate domain verification."
            email_raw = f"Free Provider (@{email_domain})"
        elif email_val:
            email_pts = 0
            email_rat = f"Unrecognized email format: {email_val}"
            email_raw = email_val
        else:
            email_pts = 0
            email_rat = "Work email: Unknown / Not Provided"
            email_raw = "Not Provided"

        firmo_receipts = [
            FieldScoreReceipt(
                field_name="Industry & Niche",
                pillar="Firmographics",
                raw_value=f"{form.industry_sector or 'Unknown'} • {form.sub_vertical or 'General'}",
                gtm_points=firmo_pts if (ind_known and firmo_pts > 0) else 0,
                rationale=firmo_rationale if ind_known else "Industry: Unknown / Not Provided"
            ),
            FieldScoreReceipt(
                field_name="Geographic Footprint",
                pillar="Firmographics",
                raw_value=ai_footprint.geographic_reach if geo_known else "Unknown",
                gtm_points=firmo_pts if (geo_known and firmo_pts > 0) else 0,
                rationale=ai_footprint.rationale if geo_known else "Location: Unknown / Not Provided"
            ),
            FieldScoreReceipt(
                field_name="Business Email Domain",
                pillar="Firmographics",
                raw_value=email_raw,
                gtm_points=email_pts,
                rationale=email_rat
            )
        ]
        if rev_known:
            firmo_receipts.insert(0, FieldScoreReceipt(
                field_name="Company Revenue",
                pillar="Firmographics",
                raw_value=prospect_rev_str,
                gtm_points=firmo_pts if firmo_pts > 0 else 0,
                rationale=f"Stated Revenue: {prospect_rev_str}"
            ))
        if hc_known:
            firmo_receipts.insert(1 if rev_known else 0, FieldScoreReceipt(
                field_name="Employee Headcount",
                pillar="Firmographics",
                raw_value=hc_str,
                gtm_points=firmo_pts if firmo_pts > 0 else 0,
                rationale=f"Headcount: {hc_str}"
            ))

        firmo_rat_summary = _one_line_text(
            _clean_str(firmo_rationale)
            or ("No verified firmographic data provided." if not has_firmo_data else "Firmographic fit evaluated from account profile.")
        )
        pillar_firmo = PillarScoreSummary(
            pillar_name="Firmographic Fit",
            rating=firmo_rating,
            score=float(firmo_rating * 20) if firmo_rating is not None else None,
            weight_pct=cfg.weight_firmographics,
            is_known=firmo_rating is not None,
            status=firmo_status,
            rationale=firmo_rat_summary,
            field_receipts=firmo_receipts
        )

        # Pillar 2: Offering Fit (25%) - Replaces Tech Stack (Section 4.1, 6.2)
        # Counted as known only when offering_interest or buying_intent is filled in; industry and sub-vertical describe the company, not what they need.
        has_offering_data = bool(_has_text(form.offering_interest) or _has_text(form.buying_intent))
        ev_offering = raw_evidence.get("offering") or raw_evidence.get("technographic", {})
        offering_rating, offering_status, offering_rationale = extract_rating(ev_offering, has_offering_data)
        offering_pts = offering_rating or 0

        platform_raw = (form.uses_existing_platform or form.existing_platform or "").strip()
        incumbent_str = platform_raw if platform_raw else "None Stated"
        has_incumbent = bool(platform_raw)
        offering_known = bool(offering_rating is not None and offering_rating > 0)

        offering_receipts = [
            FieldScoreReceipt(
                field_name="Offering Alignment",
                pillar="Offering Fit",
                raw_value=form.offering_interest or form.buying_intent or "None Stated",
                gtm_points=offering_pts if offering_known else 0,
                rationale=offering_rationale if offering_known else "No product or solution need stated."
            )
        ]
        if has_incumbent:
            offering_receipts.append(
                FieldScoreReceipt(
                    field_name="Existing Platform / Incumbent",
                    pillar="Offering Fit",
                    raw_value=incumbent_str,
                    gtm_points=offering_pts if offering_known else 0,
                    rationale=f"Incumbent: {incumbent_str}"
                )
            )

        offering_rat_summary = _one_line_text(
            (_clean_str(offering_rationale) or "Offering fit evaluated from stated interest.")
            if has_offering_data
            else "No product or solution need stated."
        )
        pillar_offering = PillarScoreSummary(
            pillar_name="Offering Fit",
            rating=offering_rating,
            score=float(offering_rating * 20) if offering_rating is not None else None,
            weight_pct=cfg.weight_offering,
            is_known=offering_rating is not None,
            status=offering_status,
            rationale=offering_rat_summary,
            field_receipts=offering_receipts
        )

        # Pillar 3: Buyer Authority (25%) (Section 6.2)
        has_auth_data = bool(_has_text(form.contact_role_title) or _has_text(form.buying_role))
        ev_auth = raw_evidence.get("authority") or raw_evidence.get("qualifying", {})
        auth_rating, auth_status, auth_rationale = extract_rating(ev_auth, has_auth_data)

        # Deterministic Section 6 Rubric Fallback if AI marked UNKNOWN despite explicit role title
        if auth_rating is None and has_auth_data:
            role_raw = form.contact_role_title or ""
            role_l = role_raw.lower()
            brole_l = (form.buying_role or "").lower()

            # Special Cases: Product Owner and Channel Partner
            is_product_owner = matches_whole_word("product owner", role_l)
            is_channel_partner = matches_whole_word("channel partner", role_l)

            # Executive Terms (Level 5) - Owner matches unless Product Owner; Partner matches unless Channel Partner
            exec_terms = [
                "vp", "vice president", "chief", "cxo", "cro", "cfo", "cto", "ceo",
                "coo", "cio", "cpo", "cso", "cmo", "cco", "president", "head of",
                "general manager", "founder"
            ]
            if not is_product_owner:
                exec_terms.append("owner")
            if not is_channel_partner:
                exec_terms.append("partner")

            dir_terms = [
                "director", "directors", "senior director", "managing director",
                "executive director", "associate director", "regional director"
            ]
            mgr_terms = [
                "manager", "managers", "senior manager", "lead", "team lead",
                "principal", "supervisor"
            ]
            ic_terms = [
                "engineer", "analyst", "specialist", "coordinator", "associate",
                "consultant", "contractor", "inspector", "technician", "developer",
                "representative", "officer", "scientist", "researcher", "practitioner",
                "account executive", "individual contributor", "staff"
            ]

            is_assistant = matches_whole_word("assistant", role_l)

            # Rule: Treat "Assistant X" as one level below X
            if is_assistant:
                if any(matches_whole_word(t, role_l) for t in ["vice president", "vp", "general manager", "president"]):
                    auth_rating = 4
                    auth_status = "VERIFIED"
                    auth_rationale = f"Assistant Executive (Director-equivalent authority verified): {role_raw}"
                elif any(matches_whole_word(t, role_l) for t in dir_terms):
                    auth_rating = 3
                    auth_status = "VERIFIED"
                    auth_rationale = f"Assistant Director (Manager-equivalent authority verified): {role_raw}"
                elif any(matches_whole_word(t, role_l) for t in mgr_terms):
                    auth_rating = 2
                    auth_status = "VERIFIED"
                    auth_rationale = f"Assistant Manager (Staff authority verified): {role_raw}"
                else:
                    auth_rating = 2
                    auth_status = "VERIFIED"
                    auth_rationale = f"Support assistant / Individual contributor verified: {role_raw}"
            elif is_product_owner and not any(matches_whole_word(t, role_l) for t in exec_terms + dir_terms + mgr_terms):
                auth_rating = 2
                auth_status = "VERIFIED"
                auth_rationale = f"Product Owner (Individual contributor verified): {role_raw}"
            # Highest matching level wins (exec > director > manager > staff)
            elif any(matches_whole_word(t, role_l) for t in exec_terms):
                auth_rating = 5
                auth_status = "VERIFIED"
                auth_rationale = f"Executive C-Suite/VP decision authority verified: {role_raw}"
            elif any(matches_whole_word(t, role_l) for t in dir_terms):
                auth_rating = 4
                auth_status = "VERIFIED"
                auth_rationale = f"Director-level authority verified: {role_raw}"
            elif any(matches_whole_word(t, role_l) for t in mgr_terms) or is_channel_partner:
                auth_rating = 3
                auth_status = "VERIFIED"
                auth_rationale = f"Management-level authority verified: {role_raw}"
            elif any(matches_whole_word(t, role_l) for t in ic_terms) or is_product_owner:
                auth_rating = 2
                auth_status = "VERIFIED"
                auth_rationale = f"Individual contributor verified: {role_raw}"
            elif matches_whole_word("economic buyer", brole_l):
                auth_rating = 4
                auth_status = "INFERRED"
                auth_rationale = f"Economic buyer authority inferred: {form.buying_role}"
            else:
                # Unrecognized title: do NOT default to 2. Leave unknown for manual review.
                auth_rating = None
                auth_status = "UNKNOWN"
                auth_rationale = f"Unrecognized title requiring manual review: {role_raw}"

        auth_pts = auth_rating or 0

        auth_val = f"{form.contact_role_title or 'Unspecified'} ({form.buying_role or ai_role.persona_type})"
        auth_rat_summary = _one_line_text(
            (_clean_str(auth_rationale) or _clean_str(ai_role.rationale) or "Buyer authority evaluated from role title.")
            if has_auth_data
            else "No verified buyer authority data provided."
        )
        pillar_auth = PillarScoreSummary(
            pillar_name="Buyer Authority",
            rating=auth_rating,
            score=float(auth_rating * 20) if auth_rating is not None else None,
            weight_pct=cfg.weight_authority,
            is_known=auth_rating is not None,
            status=auth_status,
            rationale=auth_rat_summary,
            field_receipts=[
                FieldScoreReceipt(field_name="Role Title & Buying Persona", pillar="Buyer Authority", raw_value=auth_val, gtm_points=auth_pts, rationale=auth_rat_summary)
            ]
        )

        # Pillar 4: Intent & Velocity (15%) (Section 6.2)
        has_intent_data = bool(_has_text(form.buying_intent) or _has_text(form.timeline))
        ev_intent = raw_evidence.get("intent") or raw_evidence.get("readiness", {})
        intent_rating, intent_status, intent_rationale = extract_rating(ev_intent, has_intent_data)
        intent_pts = intent_rating or 0

        intent_val = f"{form.buying_intent or 'Unspecified'} (Timeline: {form.timeline or ai_intent.timeline_detected or 'Unspecified'})"
        intent_rat_summary = _one_line_text(
            (_clean_str(intent_rationale) or "Buying intent evaluated from prospect message.")
            if has_intent_data
            else "No buying intent or timeline provided."
        )
        pillar_intent = PillarScoreSummary(
            pillar_name="Intent & Velocity",
            rating=intent_rating,
            score=float(intent_rating * 20) if intent_rating is not None else None,
            weight_pct=cfg.weight_intent,
            is_known=intent_rating is not None,
            status=intent_status,
            rationale=intent_rat_summary,
            field_receipts=[
                FieldScoreReceipt(field_name="Buying Intent & Timeline", pillar="Intent", raw_value=intent_val, gtm_points=intent_pts, rationale=intent_rat_summary)
            ]
        )

        # -------------------------------------------------------------
        # 6. Authoritative Scoring & Tiering in Python (Section 6.4, 6.5)
        # -------------------------------------------------------------
        all_pillars = [
            (cfg.weight_firmographics, pillar_firmo),
            (cfg.weight_offering, pillar_offering),
            (cfg.weight_authority, pillar_auth),
            (cfg.weight_intent, pillar_intent)
        ]
        known_pillars = [(w, p) for w, p in all_pillars if p.is_known and p.rating is not None]

        sum_known_weights = sum(w for w, p in known_pillars)
        coverage_pct = round(sum_known_weights * 100.0, 1)

        if not known_pillars or sum_known_weights == 0:
            master_score = 0.0
        else:
            sum_weighted_ratings = sum(w * p.rating for w, p in known_pillars)
            # Section 6.4 formula: (sum of weight * rating) / (sum of known weights) * 20
            master_score = round((sum_weighted_ratings / sum_known_weights) * 20.0, 1)

        # Section 6.5: Needs review wins over score if coverage < 60% or buyer authority unknown,
        # or when the AI flags is_disqualified or rates buyer authority 1 (non-commercial persona).
        ai_is_disqualified = bool(ai_res.get("is_disqualified") or ai_res.get("scores", {}).get("is_disqualified"))
        ai_disq_reason = _clean_str(ai_res.get("disqualification_reason")) or _clean_str((ai_res.get("scores") or {}).get("disqualification_reason")) or ""

        review_reasons = []
        if ai_is_disqualified or (pillar_auth.rating == 1):
            auth_rat = ""
            if pillar_auth.field_receipts and pillar_auth.field_receipts[0].rationale:
                auth_rat = pillar_auth.field_receipts[0].rationale
            review_reasons.append(ai_disq_reason or auth_rat or "Non-commercial contact or low buyer authority detected (Authority rating: 1).")
        if coverage_pct < cfg.min_coverage_threshold:
            review_reasons.append(f"Data coverage is below minimum threshold ({coverage_pct:.0f}% < {cfg.min_coverage_threshold:.0f}%).")
        if not pillar_auth.is_known:
            review_reasons.append("Buyer authority is unknown / unverified.")

        needs_review_reason = " ".join(review_reasons) if review_reasons else None
        if review_reasons:
            priority_tier = "Tier: Needs review"
        elif master_score >= cfg.tier_a_threshold:
            priority_tier = "Tier A: Contact First"
        elif master_score >= cfg.tier_b_threshold:
            priority_tier = "Tier B: Follow Up"
        elif master_score >= cfg.tier_c_threshold:
            priority_tier = "Tier C: Nurture"
        else:
            priority_tier = "Tier D: Low Priority"

        # SLA and Next Actions
        if priority_tier == "Tier: Needs review":
            urgency_sla = "Manual Sales Review Required"
            recommended_channel = "Human Qualification Call / LinkedIn Verification"
        elif "Tier A" in priority_tier:
            urgency_sla = "< 2 Hours (Executive Callback)"
            recommended_channel = "Direct Phone & Bespoke Executive Email"
        elif "Tier B" in priority_tier:
            urgency_sla = "< 24 Hours (Dedicated SDR Sequence)"
            recommended_channel = "Multi-Touch Email & LinkedIn InMail"
        elif "Tier C" in priority_tier:
            urgency_sla = "Within 48 Hours"
            recommended_channel = "Automated Marketing Nurture & Educational Sequences"
        else:
            urgency_sla = "Automated Marketing Nurture"
            recommended_channel = "Marketing Newsletter & Long-Tail Documentation"

        sub_niche = form.sub_vertical or form.industry_sector or "target initiatives"
        comp = form.company_name or "your team"
        contact = form.contact_name or "there"
        org_ref = cfg.company_name if cfg.company_name else "our team"

        val_w = _clean_str(raw_strategy.get("value_wedge")) or _clean_str(ai_res.get("value_wedge"))
        value_wedge = val_w or f"Accelerate strategic initiatives for {sub_niche} at {comp}."

        hook_w = _clean_str(raw_strategy.get("outreach_hook")) or _clean_str(ai_res.get("outreach_hook"))
        outreach_hook = hook_w or f"Hi {contact}, noticed your team's focus on {sub_niche} at {comp}—wanted to share how {org_ref} supports similar organizations."

        # Audit Tracker (Section 6.4: Normalized points contribution reflecting unknown pillar weight reallocation)
        tracker = []
        if sum_known_weights > 0:
            raw_contribs = []
            for w, p in all_pillars:
                if p.is_known and p.rating is not None:
                    adj_weight = w / sum_known_weights
                    raw_contribs.append(adj_weight * p.rating * 20.0)
                else:
                    raw_contribs.append(0.0)

            rounded_contribs = [round(c, 1) for c in raw_contribs]
            known_indices = [i for i, (w, p) in enumerate(all_pillars) if p.is_known and p.rating is not None]
            if known_indices:
                diff = round(master_score - sum(rounded_contribs), 1)
                if abs(diff) > 0 and abs(diff) <= 0.2:
                    largest_idx = max(known_indices, key=lambda i: raw_contribs[i])
                    rounded_contribs[largest_idx] = round(rounded_contribs[largest_idx] + diff, 1)

            for i, (w, p) in enumerate(all_pillars):
                tracker.append(
                    ScoringTrackerItem(
                        pillar_name=p.pillar_name,
                        allotted_score=float(p.score) if p.score is not None else 0.0,
                        weight_pct=p.weight_pct,
                        points_contributed=rounded_contribs[i],
                        basis_criterion=f"{p.status} (Rating: {p.rating}/5)" if p.is_known else "UNKNOWN (No Data)",
                        verified_signals=[r.field_name for r in p.field_receipts if r.gtm_points > 0],
                        deduction_gaps=[r.field_name for r in p.field_receipts if r.gtm_points == 0],
                        decision_rationale=p.rationale or (p.field_receipts[0].rationale if p.field_receipts else "Pillar evaluation.")
                    )
                )
        else:
            for w, p in all_pillars:
                tracker.append(
                    ScoringTrackerItem(
                        pillar_name=p.pillar_name,
                        allotted_score=0.0,
                        weight_pct=p.weight_pct,
                        points_contributed=0.0,
                        basis_criterion="UNKNOWN (No Data)",
                        verified_signals=[],
                        deduction_gaps=[r.field_name for r in p.field_receipts],
                        decision_rationale="No verified data provided."
                    )
                )

        def _clean_list(key: str) -> List[str]:
            raw_items = ai_res.get(key)
            if not isinstance(raw_items, list) or not raw_items:
                raw_items = raw_strategy.get(key)
            if not isinstance(raw_items, list):
                return []
            return [item for item in (_clean_str(x) for x in raw_items) if item]

        discovery_questions = _clean_list("discovery_questions")
        key_strengths = _clean_list("key_strengths")
        key_risks = _clean_list("key_risks")

        return StreamlinedScoringResult(
            company_name=form.company_name or "Unspecified",
            master_icp_score=master_score,
            coverage_pct=coverage_pct,
            priority_tier=priority_tier,
            is_disqualified=False,
            disqualification_reason="",
            needs_review_reason=needs_review_reason or "",
            urgency_sla=urgency_sla,
            recommended_channel=recommended_channel,
            value_wedge=value_wedge,
            outreach_hook=outreach_hook,
            pillar_firmographics=pillar_firmo,
            pillar_offering=pillar_offering,
            pillar_authority=pillar_auth,
            pillar_intent=pillar_intent,
            pillar_value=pillar_offering,
            ai_role=ai_role,
            ai_niche=ai_niche,
            ai_intent=ai_intent,
            ai_footprint=ai_footprint,
            scoring_tracker=tracker,
            lead_summary={
                "industry": form.industry_sector or "Unknown",
                "sub_vertical": form.sub_vertical or "Unknown",
                "location": form.location or "Unknown",
                "branches": form.branch_locations,
                "contact_title": form.contact_role_title or "Unknown",
                "buying_role": form.buying_role or "Unknown",
                "buying_intent": form.buying_intent or "Unknown",
                "timeline": form.timeline or "Unknown",
                "stated_revenue": prospect_rev_str,
                "stated_deal": prospect_deal_str,
                "headcount": hc_str
            },
            discovery_questions=discovery_questions,
            key_strengths=key_strengths,
            key_risks=key_risks,
            analysis_mode="live",
            degraded_reasons=[needs_review_reason] if needs_review_reason else [],
            model_used=model_used
        )
