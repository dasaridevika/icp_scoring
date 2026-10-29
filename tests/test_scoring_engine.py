"""
Automated Test Suite for ICP Scoring Engine & GTM Policy Layer.
Verifies Section 6 Authoritative Rubric, deterministic compliance rules,
FX currency normalization, fail-loud error handling, and coverage-weighted scoring.
"""

import sys
from pathlib import Path
import pytest

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engine.fx import FXEngine
from engine.rules import PolicyEngine, PolicyCheckResult
from engine.gtm_engine import (
    CompanyStandardsConfig,
    StreamlinedLeadForm,
    GTMScoringEngine,
    StreamlinedScoringResult
)


# ==============================================================================
# 1. FX Normalization Tests
# ==============================================================================

def test_fx_conversion_inr_crores():
    """Verify INR Crores conversion to USD does not produce 80x valuation distortion."""
    native, usd = FXEngine.normalize_to_usd(amount=850.0, unit="Crores (Cr)", currency_code="INR")
    assert native == 8_500_000_000.0  # 8.5 Billion INR
    assert 100_000_000.0 <= usd <= 105_000_000.0  # ~102M USD


def test_fx_conversion_eur_thousands():
    """Verify EUR Thousands conversion to USD."""
    native, usd = FXEngine.normalize_to_usd(amount=35.0, unit="Thousands (k)", currency_code="EUR")
    assert native == 35_000.0
    assert usd == 35_000.0 * 1.08


def test_unknown_currency_raises_error():
    """Verify Bug 3.6 fix: Unknown currency is not silently treated as USD."""
    with pytest.raises(ValueError) as excinfo:
        FXEngine.normalize_to_usd(amount=100.0, unit="Exact / Standard", currency_code="ZAR")
    assert "Unsupported or unknown currency code: 'ZAR'" in str(excinfo.value)


def test_deal_currency_independent_of_revenue_currency():
    """Verify Bug 3.4 fix: Budget is converted using deal currency, not revenue currency."""
    form = StreamlinedLeadForm(
        company_name="Global Energy Ltd",
        currency_code="INR",
        deal_currency_code="EUR",
        revenue_entered_value=10.0,
        revenue_unit="Crores (Cr)",
        deal_entered_value=50.0,
        deal_unit="Thousands (k)",
        industry_sector="Energy & Renewables",
        sub_vertical="Solar Infrastructure",
        location="New Delhi, India",
        contact_role_title="Managing Director",
        buying_intent="Active Solar Procurement"
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "evidence": {
            "firmographic": {"rating": 5, "status": "VERIFIED"},
            "offering": {"rating": 5, "status": "VERIFIED"},
            "authority": {"rating": 5, "status": "VERIFIED"},
            "intent": {"rating": 4, "status": "VERIFIED"}
        }
    }
    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    # Stated deal should reflect EUR, not INR
    assert "EUR" in result.lead_summary.get("stated_deal", "")
    assert "INR" in result.lead_summary.get("stated_revenue", "")


# ==============================================================================
# 2. Compliance & Deterministic Policy Tests (Whole-word & Sanctions)
# ==============================================================================

def test_deterministic_sanctions_disqualification():
    """Verify prohibited/sanctioned territories are hard-disqualified in Python without calling AI."""
    res = PolicyEngine.evaluate_compliance(
        location="Minsk, Belarus",
        role_title="Director of Operations",
        prohibited_countries=["North Korea", "Iran", "Syria", "Cuba", "Russia", "Belarus"]
    )
    assert res.is_disqualified is True
    assert res.matched_rule == "SANCTIONED_TERRITORY"
    assert "Belarus" in res.disqualification_reason


def test_deterministic_anti_icp_role():
    """Verify non-commercial personas (e.g. students, interns) are immediately disqualified."""
    res = PolicyEngine.evaluate_compliance(
        location="San Francisco, California, US",
        role_title="Graduate Student / Academic Researcher"
    )
    assert res.is_disqualified is True
    assert res.matched_rule == "ANTI_ICP_ROLE"


def test_subword_role_matching_allows_senior_buyers():
    """Verify Bug 2.2 fix: 'intern' inside 'International' or 'Internal' does not disqualify senior buyers."""
    # International Sales Director must NOT be blocked
    res1 = PolicyEngine.evaluate_compliance(
        location="London, United Kingdom",
        role_title="International Sales Director"
    )
    assert res1.is_disqualified is False

    # Head of Internal Audit must NOT be blocked
    res2 = PolicyEngine.evaluate_compliance(
        location="New York, NY, United States",
        role_title="Head of Internal Audit"
    )
    assert res2.is_disqualified is False


def test_anti_icp_roles_disqualify_intern_and_trainees():
    """Verify Bug 2.2 and 4.2 fix: whole word matching blocks interns, trainees, apprentices, PhD candidates."""
    roles_to_block = [
        "Summer Intern",
        "Marketing Intern",
        "Graduate Trainee",
        "Procurement Apprentice",
        "PhD Candidate"
    ]
    for role in roles_to_block:
        res = PolicyEngine.evaluate_compliance(
            location="Chicago, IL, United States",
            role_title=role
        )
        assert res.is_disqualified is True, f"Expected {role} to be disqualified"
        assert res.matched_rule == "ANTI_ICP_ROLE"


def test_subword_sanctions_allows_legitimate_territories():
    """Verify Bug 2.3 fix: 'iran' in 'Miranda, Chile' and 'cuba' in 'Cubatão, Brazil' do NOT block leads."""
    res_chile = PolicyEngine.evaluate_compliance(
        location="Miranda, Chile",
        role_title="VP Procurement"
    )
    assert res_chile.is_disqualified is False

    res_brazil = PolicyEngine.evaluate_compliance(
        location="Cubatão, Brazil",
        role_title="Chief Technology Officer"
    )
    assert res_brazil.is_disqualified is False


def test_sanctions_blocks_sanctioned_cities_and_branches():
    """Verify Bug 2.3 fix: Tehran, Moscow, and branch locations in sanctioned cities are blocked."""
    # Tehran without country name specified
    res_tehran = PolicyEngine.evaluate_compliance(
        location="Tehran",
        role_title="Procurement Director"
    )
    assert res_tehran.is_disqualified is True
    assert res_tehran.matched_rule == "SANCTIONED_TERRITORY"

    # Moscow office
    res_moscow = PolicyEngine.evaluate_compliance(
        location="Moscow Corporate Office",
        role_title="VP Supply Chain"
    )
    assert res_moscow.is_disqualified is True

    # Branch location in Minsk
    res_branch = PolicyEngine.evaluate_compliance(
        location="Warsaw, Poland",
        branch_locations=["Minsk", "Berlin"],
        role_title="VP Operations"
    )
    assert res_branch.is_disqualified is True
    assert res_branch.matched_rule == "SANCTIONED_TERRITORY"


# ==============================================================================
# 3. Section 6 Scoring Rubric & Coverage Tests
# ==============================================================================

def test_section_6_worked_example_lead_1():
    """
    Verify Section 6.6 Worked Example Lead 1:
    Firmographic 4 (35%), Offering fit 5 (25%), Buyer authority 4 (25%), Intent unknown (15%).
    Known weights = 85.
    Score = (35*4 + 25*5 + 25*4) / 85 * 20 = 365 / 85 * 20 = 85.9 (~86).
    Coverage = 85%, Tier A.
    """
    form = StreamlinedLeadForm(
        company_name="Apex Energy Solutions",
        industry_sector="Energy & Renewables",
        sub_vertical="Grid Modernization",
        annual_revenue_usd=50_000_000.0,
        employee_count=350,
        location="Houston, Texas, United States",
        contact_role_title="VP Energy Infrastructure",
        buying_intent="Active ERP integration evaluation"
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "evidence": {
            "firmographic": {"rating": 4, "status": "VERIFIED", "rationale": "Strong enterprise scale"},
            "offering": {"rating": 5, "status": "VERIFIED", "rationale": "Direct Blackridge alignment"},
            "authority": {"rating": 4, "status": "VERIFIED", "rationale": "VP level authority"},
            "intent": {"rating": None, "status": "UNKNOWN", "rationale": "No timeline stated"}
        }
    }

    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    assert result.coverage_pct == 85.0
    assert 85.8 <= result.master_icp_score <= 86.0
    assert result.priority_tier == "Tier A: Contact First"
    assert result.is_disqualified is False


def test_section_6_worked_example_lead_2_low_coverage_needs_review():
    """
    Verify Section 6.6 Worked Example Lead 2:
    Only Intent known rated 5 (15%).
    Score = 100, but Coverage = 15% (< 60%).
    Tier must be 'Tier: Needs review', NOT Tier A.
    """
    form = StreamlinedLeadForm(
        company_name="Mystery Lead Corp",
        buying_intent="Urgent RFP Quote needed by tomorrow"
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "evidence": {
            "firmographic": {"rating": None, "status": "UNKNOWN"},
            "offering": {"rating": None, "status": "UNKNOWN"},
            "authority": {"rating": None, "status": "UNKNOWN"},
            "intent": {"rating": 5, "status": "VERIFIED", "rationale": "Immediate RFP request"}
        }
    }

    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    assert result.master_icp_score == 100.0
    assert result.coverage_pct == 15.0
    assert result.priority_tier == "Tier: Needs review"


def test_buyer_authority_unknown_forces_needs_review():
    """Verify Section 6.5: Buyer authority unknown forces 'Tier: Needs review' even if score is high."""
    form = StreamlinedLeadForm(
        company_name="Mega Enterprise Inc",
        industry_sector="Oil & Gas",
        annual_revenue_usd=200_000_000.0,
        buying_intent="Active project study procurement"
        # contact_role_title is omitted / blank
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "evidence": {
            "firmographic": {"rating": 5, "status": "VERIFIED"},
            "offering": {"rating": 5, "status": "VERIFIED"},
            "authority": {"rating": None, "status": "UNKNOWN"},
            "intent": {"rating": 5, "status": "VERIFIED"}
        }
    }

    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    # Coverage is 35 + 25 + 15 = 75% (>= 60%), but authority is unknown
    assert result.coverage_pct == 75.0
    assert result.priority_tier == "Tier: Needs review"


def test_ai_disqualified_propagates_to_zero_score_and_disqualified_tier():
    """Verify Bug 2.4 fix: AI worker returning is_disqualified results in score 0 and Disqualified tier."""
    form = StreamlinedLeadForm(
        company_name="Candidate Research",
        location="Boston, MA, US",
        contact_role_title="Researcher"
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "is_disqualified": True,
        "disqualification_reason": "Non-commercial hobbyist research inquiry",
        "evidence": {
            "firmographic": {"rating": 1, "status": "VERIFIED"},
            "authority": {"rating": 1, "status": "VERIFIED"}
        }
    }

    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    assert result.is_disqualified is True
    assert result.master_icp_score == 0.0
    assert "Disqualified" in result.priority_tier
    assert result.disqualification_reason == "Non-commercial hobbyist research inquiry"


def test_worker_api_ingestion_preserves_revenue_and_deal_usd():
    """Verify Bug 3.3 fix: annual_revenue_usd and target_deal_size_usd passed via worker API are preserved."""
    form = StreamlinedLeadForm(
        company_name="Direct USD Prospect",
        annual_revenue_usd=25_000_000.0,
        target_deal_size_usd=50_000.0,
        employee_count=120,
        location="Chicago, IL, United States",
        contact_role_title="Director of Market Strategy",
        industry_sector="Energy & Renewables",
        buying_intent="Evaluating syndicated reports"
    )
    cfg = CompanyStandardsConfig()

    mock_resp = {
        "evidence": {
            "firmographic": {"rating": 4, "status": "VERIFIED"},
            "offering": {"rating": 4, "status": "VERIFIED"},
            "authority": {"rating": 4, "status": "VERIFIED"},
            "intent": {"rating": 3, "status": "VERIFIED"}
        }
    }

    result = GTMScoringEngine.evaluate(form, cfg, mock_ai_response=mock_resp)

    assert "$25,000,000 USD" in result.lead_summary["stated_revenue"]
    assert "$50,000 USD" in result.lead_summary["stated_deal"]
    assert result.master_icp_score == 77.0  # (35*4 + 25*4 + 25*4 + 15*3)/100 * 20 = (140+100+100+45)/100 * 20 = 77.0
    assert result.priority_tier == "Tier B: Follow Up"


def test_fail_loud_on_ai_unreachable():
    """Verify P0-1 fix: When AI is unreachable, system fails loudly with analysis_mode='failed' and zero score."""
    form = StreamlinedLeadForm(
        company_name="Test Unreachable Inc",
        location="Austin, Texas, United States",
        contact_role_title="Manager",
        buying_intent="Testing"
    )
    cfg = CompanyStandardsConfig()

    result = GTMScoringEngine.evaluate(
        form=form,
        config=cfg,
        worker_url="http://127.0.0.1:1/nonexistent"
    )

    assert result.analysis_mode == "failed"
    assert result.master_icp_score == 0.0
    assert "Offline" in result.priority_tier
    assert len(result.degraded_reasons) > 0


def test_buying_role_timeline_budget_range():
    """Verify buying_role, timeline, and platform fields in lead form."""
    form = StreamlinedLeadForm(
        company_name="Apex Energy Solutions",
        annual_revenue_usd=50_000_000.0,
        employee_count=350,
        location="Houston, Texas, United States",
        contact_name="Sarah Jenkins",
        contact_role_title="VP Energy Infrastructure",
        buying_role="Economic Buyer / Decision Maker",
        buying_intent="Active ERP integration evaluation",
        timeline="1 – 3 Months (Current Quarter)",
        existing_platform="Bloomberg Terminal",
        target_deal_size_usd=75_000.0
    )
    assert form.buying_role == "Economic Buyer / Decision Maker"
    assert form.timeline == "1 – 3 Months (Current Quarter)"
    assert form.existing_platform == "Bloomberg Terminal"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
