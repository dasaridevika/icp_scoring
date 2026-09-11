"""
Enterprise ICP Revenue Intelligence - GTM Partners 4-Pillar Form Scoring Engine.
Implements the official GTM Partners {-5, -3, -1, +1, +3, +5} forced-choice scale
across all 19 discrete fields with isolated metric calculations and configurable company standards.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


# 11 Master Macro-Sectors (GICS / NAICS standard)
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
# 1. Company Standards Configuration (Settings Tab)
# ==========================================
class CompanyStandardsConfig(BaseModel):
    """
    Company-specific standards, thresholds, and margins configured in Settings.
    """
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
    target_buyer_departments: List[str] = Field(default_factory=lambda: [
        "Procurement", "Commercial Sales", "Operations", "Engineering / IT"
    ])
    tier1_territories: List[str] = Field(default_factory=lambda: [
        "United States", "United Kingdom", "United Arab Emirates", "European Union",
        "Canada", "Australia", "Singapore", "India", "Germany", "France", "UAE", "UK", "USA"
    ])
    prohibited_countries: List[str] = Field(default_factory=lambda: [
        "North Korea", "Iran", "Syria", "Cuba"
    ])
    complementary_whitelist: List[str] = Field(default_factory=lambda: [
        "Salesforce", "AWS", "Snowflake", "HubSpot", "Azure", "SAP", "Oracle", "Google Cloud"
    ])
    blocker_blacklist: List[str] = Field(default_factory=lambda: [
        "Direct Competitor Locked-In"
    ])
    weight_firmographics: float = 0.30
    weight_technographics: float = 0.25
    weight_qualifying: float = 0.25
    weight_readiness: float = 0.20
    tier_a1_threshold: float = 80.0
    tier_a2_threshold: float = 65.0
    tier_b1_threshold: float = 50.0


# ==========================================
# 2. Lead Form Submission (Form Tab Input)
# ==========================================
class FirmographicsForm(BaseModel):
    company_name: str = "Parveen Industries Pvt. Ltd."
    annual_revenue_usd: float = 75000000.0
    industry_sector: str = "Energy, Utilities & Renewables"
    sub_vertical: str = "Solar Power & Oilfield Infrastructure"
    employee_count: int = 1500
    hq_location: str = "United Arab Emirates (UAE)"
    operating_regions: List[str] = Field(default_factory=lambda: ["UAE", "India", "Middle East"])


class TechnographicsForm(BaseModel):
    complementary_tools: List[str] = Field(default_factory=lambda: ["SAP", "AWS"])
    blocking_competitors: List[str] = Field(default_factory=list)
    stack_sophistication: str = "Hybrid Enterprise"  # Modern Cloud-Native, Hybrid Enterprise, Legacy On-Premise, Unknown
    contract_renewal_timing: str = "Renewal in 3-6 months"  # Renewal in <3 months, Renewal in 3-6 months, Renewal in 6-12 months, Multi-year Locked, Unknown


class QualifyingForm(BaseModel):
    potential_user_seats: int = 50
    team_members_count: int = 15
    contact_name: str = "Gabriel Martinez"
    contact_email: str = "sales@parvenoilfield.com"
    contact_role_title: str = "Commercial Sales & Procurement Director"
    contact_seniority: str = "VP / Head of (+5)"  # C-Suite / Founder (+5), VP / Head of (+5), Director / Principal (+3), Manager (+1), Individual Contributor (+1), Student / Intern (-5)
    budget_line_item: str = "Approved & Allocated Budget (+5)"  # Approved & Allocated Budget (+5), Discretionary Budget Pending (+3), Exploratory / No Budget Yet (-1)
    pricing_fit: str = "Comfortable with Premium Pricing (+5)"  # Comfortable with Premium Pricing (+5), Standard Commercial Fit (+3), Discount / Budget Squeeze (-1), Price Inhibitor (-3)
    accelerators_trigger: str = "Active Business Expansion (+5)"  # Urgent Compliance (+5), Active Business Expansion (+5), Project Deadline (+3), Standard Review (+1), None (-1)


class ReadinessForm(BaseModel):
    target_deal_size_usd: float = 75000.0
    hiring_status: str = "Aggressive Hiring in Buying Dept (+5)"  # Aggressive Hiring in Buying Dept (+5), General Expansion (+3), Stable (+1), Unknown (-1), Layoffs (-5)
    funding_round: str = "Bootstrapped & Highly Profitable (+5)"  # Bootstrapped (+5), Series A/B (+5), Series C+/PE (+5), Public (+3), Pre-Seed / Unfunded (-1)
    buying_signals: str = "Executive Callback / Demo Scheduled (+5)"  # Callback / Demo Scheduled (+5), Inbound RFP (+5), Pricing Inquiry (+3), General Browsing (+1)
    growth_investments: List[str] = Field(default_factory=lambda: ["New Facility / Physical Assets (+5)", "New Product Line Expansion (+3)"])
    marketing_updates: List[str] = Field(default_factory=lambda: ["Global Geographic Expansion (+5)"])


class LeadFormSubmission(BaseModel):
    firmographics: FirmographicsForm = Field(default_factory=FirmographicsForm)
    technographics: TechnographicsForm = Field(default_factory=TechnographicsForm)
    qualifying: QualifyingForm = Field(default_factory=QualifyingForm)
    readiness: ReadinessForm = Field(default_factory=ReadinessForm)


# ==========================================
# 3. Isolated Field Receipt Model
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
    net_gtm_points: int
    normalized_score: float  # 0.0 to 100.0
    weight_pct: float
    field_receipts: List[FieldScoreReceipt] = Field(default_factory=list)


class GTMScoringResult(BaseModel):
    company_name: str
    master_icp_score: float  # 0.0 to 100.0
    priority_tier: str  # Tier A1, Tier A2, Tier B1, Tier C, Disqualified
    is_disqualified: bool
    disqualification_reason: str
    urgency_sla: str
    recommended_channel: str
    value_wedge: str
    outreach_hook: str
    firmographics_summary: PillarScoreSummary
    technographics_summary: PillarScoreSummary
    qualifying_summary: PillarScoreSummary
    readiness_summary: PillarScoreSummary
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)


# ==========================================
# 4. GTM Partners Calculation Engine
# ==========================================
class GTMScoringEngine:
    """
    Evaluates every form field independently on the {-5, -3, -1, +1, +3, +5} scale
    against the company's specific standards and thresholds.
    """

    @classmethod
    def evaluate(
        cls,
        form: LeadFormSubmission,
        config: Optional[CompanyStandardsConfig] = None
    ) -> GTMScoringResult:
        cfg = config or CompanyStandardsConfig()
        is_disqualified = False
        disq_reasons = []
        discovery_questions = []
        key_strengths = []
        key_risks = []

        # Helper to convert net sum of {-5..+5} points to normalized 0-100 scale
        def normalize_points_to_100(points: List[int]) -> float:
            if not points:
                return 50.0
            n = len(points)
            min_possible = -5.0 * n
            max_possible = 5.0 * n
            total = float(sum(points))
            norm = ((total - min_possible) / (max_possible - min_possible)) * 100.0
            return max(0.0, min(100.0, norm))

        # -------------------------------------------------------------
        # PILLAR 1: FIRMOGRAPHICS EVALUATION
        # -------------------------------------------------------------
        firmo = form.firmographics
        firmo_receipts = []

        # Field 1.1: Revenue Scale
        rev = firmo.annual_revenue_usd
        if rev >= cfg.ideal_revenue_usd:
            p_rev = 5
            r_rev = f"Annual revenue (${rev:,.0f}) exceeds ideal threshold (${cfg.ideal_revenue_usd:,.0f})"
            key_strengths.append(f"Strong Revenue Scale: ${rev:,.0f} ARR")
        elif rev >= cfg.min_company_revenue_usd:
            p_rev = 3
            r_rev = f"Annual revenue (${rev:,.0f}) meets company minimum threshold (${cfg.min_company_revenue_usd:,.0f})"
        elif rev > 0:
            p_rev = -3
            r_rev = f"Annual revenue (${rev:,.0f}) is below minimum viable threshold (${cfg.min_company_revenue_usd:,.0f})"
            key_risks.append(f"Sub-scale Revenue (${rev:,.0f}) may indicate low contract budget")
        else:
            p_rev = -1
            r_rev = "Annual revenue is unstated / unknown"
            discovery_questions.append("What is your current annual revenue or operating scale?")

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Annual Revenue", pillar="Firmographics", raw_value=f"${rev:,.0f}", gtm_points=p_rev, rationale=r_rev
        ))

        # Field 1.2: Industry Fit
        ind = firmo.industry_sector
        if ind in cfg.target_focus_industries:
            p_ind = 5
            r_ind = f"Target Focus Industry sweet-spot: {ind}"
            key_strengths.append(f"Core Target Industry: {ind} ({firmo.sub_vertical})")
        elif ind in MASTER_INDUSTRY_SECTORS:
            p_ind = 3
            r_ind = f"Legitimate Commercial Enterprise Industry: {ind}"
        else:
            p_ind = 1
            r_ind = f"General Commercial B2B Sector: {ind}"

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Industry Sector", pillar="Firmographics", raw_value=f"{ind} ({firmo.sub_vertical})", gtm_points=p_ind, rationale=r_ind
        ))

        # Field 1.3: Employee Count / Headcount
        hc = firmo.employee_count
        if hc >= cfg.ideal_headcount:
            p_hc = 5
            r_hc = f"Headcount ({hc:,} employees) meets or exceeds ideal team scale ({cfg.ideal_headcount:,})"
            key_strengths.append(f"Enterprise Headcount: {hc:,} employees")
        elif hc >= cfg.min_headcount:
            p_hc = 3
            r_hc = f"Headcount ({hc:,} employees) is within viable operating range"
        elif hc >= 5:
            p_hc = -1
            r_hc = f"Headcount ({hc:,}) is small; potential limited seat expansion"
            discovery_questions.append("How many team members will directly interact with the solution?")
        else:
            p_hc = -3
            r_hc = f"Micro-team ({hc:,} employees); high onboarding support risk"
            key_risks.append("Micro-headcount may lead to resource strain")

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Employee Headcount", pillar="Firmographics", raw_value=f"{hc:,} employees", gtm_points=p_hc, rationale=r_hc
        ))

        # Field 1.4: Location & Multi-Geographies
        hq = firmo.hq_location.strip()
        all_locs = [hq] + firmo.operating_regions
        
        # Check prohibited/sanctioned
        is_prohibited = any(any(p.lower() in loc.lower() for p in cfg.prohibited_countries) for loc in all_locs)
        if is_prohibited:
            p_loc = -5
            r_loc = f"Located in prohibited/sanctioned territory: {hq}"
            is_disqualified = True
            disq_reasons.append(r_loc)
        else:
            # Check Tier 1 match
            is_tier1 = any(any(t1.lower() in loc.lower() for t1 in cfg.tier1_territories) for loc in all_locs)
            if is_tier1:
                p_loc = 5
                r_loc = f"HQ or regional hub ({hq}) is within Tier 1 supported market"
                key_strengths.append(f"Tier 1 Geographic Presence: {hq}")
            elif hq:
                p_loc = 3
                r_loc = f"Global secondary territory: {hq}"
            else:
                p_loc = -1
                r_loc = "Geographic location unstated"
                discovery_questions.append("Where is your primary operational headquarters located?")

        firmo_receipts.append(FieldScoreReceipt(
            field_name="Geographic Locations", pillar="Firmographics", raw_value=f"HQ: {hq} | Hubs: {', '.join(firmo.operating_regions)}", gtm_points=p_loc, rationale=r_loc, is_disqualifier=is_prohibited
        ))

        firmo_pts = [r.gtm_points for r in firmo_receipts]
        firmo_summary = PillarScoreSummary(
            pillar_name="Firmographics",
            net_gtm_points=sum(firmo_pts),
            normalized_score=normalize_points_to_100(firmo_pts),
            weight_pct=cfg.weight_firmographics,
            field_receipts=firmo_receipts
        )

        # -------------------------------------------------------------
        # PILLAR 2: TECHNOGRAPHICS EVALUATION
        # -------------------------------------------------------------
        techno = form.technographics
        techno_receipts = []

        # Field 2.1: Complementary Tools
        comp = techno.complementary_tools
        comp_matched = [c for c in comp if any(w.lower() in c.lower() for w in cfg.complementary_whitelist)]
        if len(comp_matched) >= 2 or len(comp) >= 2:
            p_comp = 5
            r_comp = f"Multi-tool complementary stack ({', '.join(comp)}); seamless integration"
            key_strengths.append(f"Partner Stack Integration: {', '.join(comp)}")
        elif comp:
            p_comp = 3
            r_comp = f"Complementary tool verified: {', '.join(comp)}"
        else:
            p_comp = 1
            r_comp = "Standard standalone stack / no external tools specified"

        techno_receipts.append(FieldScoreReceipt(
            field_name="Complementary Stack", pillar="Technographics", raw_value=", ".join(comp) or "None", gtm_points=p_comp, rationale=r_comp
        ))

        # Field 2.2: Blocking Competitors
        block = techno.blocking_competitors
        if block:
            p_block = -3
            r_block = f"Competitor tool currently locked-in: {', '.join(block)}"
            key_risks.append(f"Incumbent Blocker: {', '.join(block)} may cause migration friction")
            discovery_questions.append(f"What is your contract duration and renewal timeline with {block[0]}?")
        else:
            p_block = 5
            r_block = "Zero blocking competitor lock-in"

        techno_receipts.append(FieldScoreReceipt(
            field_name="Blocking Competitors", pillar="Technographics", raw_value=", ".join(block) or "None", gtm_points=p_block, rationale=r_block
        ))

        # Field 2.3: Stack Sophistication
        soph = techno.stack_sophistication
        if "Modern" in soph:
            p_soph = 5
            r_soph = "Modern Cloud-Native stack indicates rapid deployment & high technical maturity"
        elif "Hybrid" in soph:
            p_soph = 3
            r_soph = "Hybrid Enterprise stack; standard integration lifecycle"
        elif "Legacy" in soph:
            p_soph = 1
            r_soph = "Legacy On-Premise infrastructure; may require custom connectors"
        else:
            p_soph = -1
            r_soph = "Technical architecture sophistication is unstated"
            discovery_questions.append("What is your underlying cloud or infrastructure architecture?")

        techno_receipts.append(FieldScoreReceipt(
            field_name="Stack Sophistication", pillar="Technographics", raw_value=soph, gtm_points=p_soph, rationale=r_soph
        ))

        # Field 2.4: Contract Renewal Timing
        ren = techno.contract_renewal_timing
        if "<3 months" in ren or "3-6 months" in ren:
            p_ren = 5
            r_ren = f"Active renewal window ({ren}); high buying urgency"
            key_strengths.append(f"Renewal Window: {ren}")
        elif "6-12 months" in ren:
            p_ren = 3
            r_ren = "Renewal window in 6-12 months; pipeline opportunity"
        elif "Multi-year" in ren:
            p_ren = -3
            r_ren = "Locked into multi-year competitor contract"
            key_risks.append("Multi-year lock-in may lengthen sales cycle")
        else:
            p_ren = -1
            r_ren = "Contract renewal timing unverified"

        techno_receipts.append(FieldScoreReceipt(
            field_name="Contract Timing", pillar="Technographics", raw_value=ren, gtm_points=p_ren, rationale=r_ren
        ))

        techno_pts = [r.gtm_points for r in techno_receipts]
        techno_summary = PillarScoreSummary(
            pillar_name="Technographics",
            net_gtm_points=sum(techno_pts),
            normalized_score=normalize_points_to_100(techno_pts),
            weight_pct=cfg.weight_technographics,
            field_receipts=techno_receipts
        )

        # -------------------------------------------------------------
        # PILLAR 3: QUALIFYING CHARACTERISTICS EVALUATION
        # -------------------------------------------------------------
        qual = form.qualifying
        qual_receipts = []

        # Field 3.1: Potential Users / Seats
        seats = qual.potential_user_seats
        if seats >= 25:
            p_seats = 5
            r_seats = f"High seat volume ({seats} users); strong expansion potential"
            key_strengths.append(f"Expansion Scale: {seats} user seats")
        elif seats >= 5:
            p_seats = 3
            r_seats = f"Standard team seat volume ({seats} users)"
        elif seats > 0:
            p_seats = 1
            r_seats = f"Small seat count ({seats} users)"
        else:
            p_seats = -1
            r_seats = "Potential user seat count unstated"

        qual_receipts.append(FieldScoreReceipt(
            field_name="Potential Users / Seats", pillar="Qualifying Characteristics", raw_value=f"{seats} seats", gtm_points=p_seats, rationale=r_seats
        ))

        # Field 3.2: Contact Role & Seniority
        sen = qual.contact_seniority
        email = qual.contact_email.lower().strip()
        domain = email.split("@")[-1] if "@" in email else ""

        # Freemail check
        if domain in DISPOSABLE_DOMAINS:
            p_role = -5
            r_role = f"Personal freemail address (@{domain}); non-commercial inquiry"
            is_disqualified = True
            disq_reasons.append(f"Disqualified due to personal freemail domain (@{domain})")
        elif "Student" in sen or "Intern" in sen:
            p_role = -5
            r_role = f"Academic / non-commercial role ({qual.contact_role_title})"
            is_disqualified = True
            disq_reasons.append(f"Disqualified: Non-commercial contact role ({qual.contact_role_title})")
        elif "C-Suite" in sen or "VP" in sen or "+5" in sen:
            p_role = 5
            r_role = f"Executive Economic Buyer authority: {qual.contact_role_title}"
            key_strengths.append(f"Executive Champion: {qual.contact_name} ({qual.contact_role_title})")
        elif "Director" in sen or "+3" in sen:
            p_role = 3
            r_role = f"Department decision maker / technical evaluator: {qual.contact_role_title}"
        elif "Manager" in sen or "Individual" in sen or "+1" in sen:
            p_role = 1
            r_role = f"Operational end-user role: {qual.contact_role_title}"
            discovery_questions.append("Who is the executive budget sponsor for this initiative?")
        else:
            p_role = -1
            r_role = "Contact role seniority unclear"

        qual_receipts.append(FieldScoreReceipt(
            field_name="Contact Seniority & Authority", pillar="Qualifying Characteristics", raw_value=f"{qual.contact_name} — {qual.contact_role_title} ({email})", gtm_points=p_role, rationale=r_role, is_disqualifier="Student" in sen or domain in DISPOSABLE_DOMAINS
        ))

        # Field 3.3: Budget Line Item
        bud = qual.budget_line_item
        if "+5" in bud or "Approved" in bud:
            p_bud = 5
            r_bud = "Confirmed and approved budget line item"
            key_strengths.append("Budget Allocated & Approved")
        elif "+3" in bud or "Pending" in bud:
            p_bud = 3
            r_bud = "Discretionary budget pending executive sign-off"
        else:
            p_bud = -1
            r_bud = "No budget line item allocated yet"
            discovery_questions.append("Is there an approved budget allocated for this quarter?")

        qual_receipts.append(FieldScoreReceipt(
            field_name="Budget Line Item", pillar="Qualifying Characteristics", raw_value=bud, gtm_points=p_bud, rationale=r_bud
        ))

        # Field 3.4: Pricing Fit
        price = qual.pricing_fit
        if "+5" in price:
            p_price = 5
            r_price = "Strong willingness to pay for premium value"
        elif "+3" in price:
            p_price = 3
            r_price = "Standard commercial pricing alignment"
        elif "-1" in price:
            p_price = -1
            r_price = "May require discount negotiations"
        else:
            p_price = -3
            r_price = "Severe price inhibitor; deal size expectation below budget"
            key_risks.append("Pricing friction expected")

        qual_receipts.append(FieldScoreReceipt(
            field_name="Pricing Fit", pillar="Qualifying Characteristics", raw_value=price, gtm_points=p_price, rationale=r_price
        ))

        # Field 3.5: Accelerators & Triggers
        acc = qual.accelerators_trigger
        if "+5" in acc:
            p_acc = 5
            r_acc = f"High-velocity buying trigger: {acc}"
            key_strengths.append(f"Accelerating Trigger: {acc}")
        elif "+3" in acc:
            p_acc = 3
            r_acc = f"Active project timeline trigger: {acc}"
        elif "+1" in acc:
            p_acc = 1
            r_acc = "Standard recurring evaluation"
        else:
            p_acc = -1
            r_acc = "No immediate accelerating trigger detected"

        qual_receipts.append(FieldScoreReceipt(
            field_name="Accelerators / Triggers", pillar="Qualifying Characteristics", raw_value=acc, gtm_points=p_acc, rationale=r_acc
        ))

        qual_pts = [r.gtm_points for r in qual_receipts]
        qual_summary = PillarScoreSummary(
            pillar_name="Qualifying Characteristics",
            net_gtm_points=sum(qual_pts),
            normalized_score=normalize_points_to_100(qual_pts),
            weight_pct=cfg.weight_qualifying,
            field_receipts=qual_receipts
        )

        # -------------------------------------------------------------
        # PILLAR 4: READINESS TO BUY EVALUATION
        # -------------------------------------------------------------
        ready = form.readiness
        ready_receipts = []

        # Field 4.1: Target Deal Size Fit
        deal = ready.target_deal_size_usd
        if deal >= cfg.target_deal_size_usd:
            p_deal = 5
            r_deal = f"Contract size (${deal:,.0f}) meets or exceeds target deal sweet-spot (${cfg.target_deal_size_usd:,.0f})"
            key_strengths.append(f"High-Value Deal Size: ${deal:,.0f}")
        elif deal >= cfg.min_deal_size_usd:
            p_deal = 3
            r_deal = f"Contract size (${deal:,.0f}) meets company minimum threshold (${cfg.min_deal_size_usd:,.0f})"
        else:
            p_deal = -3
            r_deal = f"Contract size (${deal:,.0f}) is below minimum viable deal margin (${cfg.min_deal_size_usd:,.0f})"
            key_risks.append("Deal size is below minimum threshold")

        ready_receipts.append(FieldScoreReceipt(
            field_name="Target Contract Size", pillar="Readiness to Buy", raw_value=f"${deal:,.0f}", gtm_points=p_deal, rationale=r_deal
        ))

        # Field 4.2: Hiring Status
        hire = ready.hiring_status
        if "+5" in hire:
            p_hire = 5
            r_hire = "Aggressive hiring in relevant department indicates operational expansion"
            key_strengths.append("Active Team Hiring & Expansion")
        elif "+3" in hire:
            p_hire = 3
            r_hire = "General company headcount expansion"
        elif "+1" in hire:
            p_hire = 1
            r_hire = "Stable headcount"
        elif "-5" in hire:
            p_hire = -5
            r_hire = "Hiring freeze or layoffs indicate severe budget restriction"
            key_risks.append("Hiring freeze/layoffs reported")
        else:
            p_hire = -1
            r_hire = "Hiring activity unverified"

        ready_receipts.append(FieldScoreReceipt(
            field_name="Hiring Status", pillar="Readiness to Buy", raw_value=hire, gtm_points=p_hire, rationale=r_hire
        ))

        # Field 4.3: Funding Round
        fund = ready.funding_round
        if "+5" in fund:
            p_fund = 5
            r_fund = f"Well-capitalized commercial entity ({fund})"
            key_strengths.append(f"Capitalization: {fund}")
        elif "+3" in fund:
            p_fund = 3
            r_fund = f"Established commercial enterprise ({fund})"
        else:
            p_fund = -1
            r_fund = "Early stage / unverified funding"

        ready_receipts.append(FieldScoreReceipt(
            field_name="Funding & Capital", pillar="Readiness to Buy", raw_value=fund, gtm_points=p_fund, rationale=r_fund
        ))

        # Field 4.4: In-Market Buying Signals
        sig = ready.buying_signals
        if "+5" in sig:
            p_sig = 5
            r_sig = f"Direct high-intent signal: {sig}"
            key_strengths.append("High Intent: Executive Callback / Demo Scheduled")
        elif "+3" in sig:
            p_sig = 3
            r_sig = f"Active commercial inquiry: {sig}"
        else:
            p_sig = 1
            r_sig = "Passive top-of-funnel browsing signal"

        ready_receipts.append(FieldScoreReceipt(
            field_name="Buying Signals", pillar="Readiness to Buy", raw_value=sig, gtm_points=p_sig, rationale=r_sig
        ))

        # Field 4.5: Growth Investments & Marketing
        grow = ready.growth_investments + ready.marketing_updates
        active_grow = [g for g in grow if g and "None" not in g]
        if len(active_grow) >= 2:
            p_grow = 5
            r_grow = f"Multiple strategic growth investments ({', '.join(active_grow)})"
            key_strengths.append(f"Strategic Growth: {', '.join(active_grow)}")
        elif active_grow:
            p_grow = 3
            r_grow = f"Active growth catalyst: {', '.join(active_grow)}"
        else:
            p_grow = 1
            r_grow = "Standard steady-state operations"

        ready_receipts.append(FieldScoreReceipt(
            field_name="Growth Investments & Updates", pillar="Readiness to Buy", raw_value=", ".join(active_grow) or "None", gtm_points=p_grow, rationale=r_grow
        ))

        ready_pts = [r.gtm_points for r in ready_receipts]
        ready_summary = PillarScoreSummary(
            pillar_name="Readiness to Buy",
            net_gtm_points=sum(ready_pts),
            normalized_score=normalize_points_to_100(ready_pts),
            weight_pct=cfg.weight_readiness,
            field_receipts=ready_receipts
        )

        # -------------------------------------------------------------
        # 5. MASTER SCORE & PRIORITY TIER COMPUTATION
        # -------------------------------------------------------------
        if is_disqualified:
            master_score = 0.0
            priority_tier = "Disqualified: Anti-ICP"
            urgency_sla = "No Outreach (Archived)"
            recommended_channel = "Do Not Contact"
            value_wedge = "Account does not meet basic eligibility compliance."
            outreach_hook = "Disqualified inquiry."
        else:
            master_score = (
                (firmo_summary.normalized_score * cfg.weight_firmographics)
                + (techno_summary.normalized_score * cfg.weight_technographics)
                + (qual_summary.normalized_score * cfg.weight_qualifying)
                + (ready_summary.normalized_score * cfg.weight_readiness)
            )

            # Priority Tier Matrix
            if master_score >= cfg.tier_a1_threshold and ready_summary.normalized_score >= 70.0:
                priority_tier = "Tier A1: Strategic Inbound"
                urgency_sla = "< 2 Hours (Priority Callback)"
                recommended_channel = "Direct Phone & Executive Bespoke Email"
            elif master_score >= cfg.tier_a2_threshold:
                priority_tier = "Tier A2: High Priority Outbound"
                urgency_sla = "< 24 Hours (SDR Dedicated Sequence)"
                recommended_channel = "Multi-Touch Email & LinkedIn InMail"
            elif master_score >= cfg.tier_b1_threshold:
                priority_tier = "Tier B1: Mid-Market Fast Track"
                urgency_sla = "Within 48 Hours"
                recommended_channel = "Inside Sales Discovery Call"
            else:
                priority_tier = "Tier C: Low Priority / Nurture"
                urgency_sla = "Standard Automated Nurture"
                recommended_channel = "Automated Marketing Email"

            # Dynamic Value Wedge & Hook
            comp_str = f" to integrate with {techno.complementary_tools[0]}" if techno.complementary_tools else ""
            value_wedge = f"Accelerate operational throughput for {firmo.sub_vertical}{comp_str} with enterprise SLA reliability."
            outreach_hook = f"Hi {qual.contact_name}, saw your initiative around {firmo.sub_vertical} at {firmo.company_name}—wanted to share how we support similar teams with tailored contract sizing."

        return GTMScoringResult(
            company_name=firmo.company_name,
            master_icp_score=round(master_score, 1),
            priority_tier=priority_tier,
            is_disqualified=is_disqualified,
            disqualification_reason="; ".join(disq_reasons),
            urgency_sla=urgency_sla,
            recommended_channel=recommended_channel,
            value_wedge=value_wedge,
            outreach_hook=outreach_hook,
            firmographics_summary=firmo_summary,
            technographics_summary=techno_summary,
            qualifying_summary=qual_summary,
            readiness_summary=ready_summary,
            discovery_questions=discovery_questions,
            key_strengths=key_strengths,
            key_risks=key_risks
        )
