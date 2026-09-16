"""
Automated Test Suite for ICP Scoring Engine & GTM Policy Layer.
Verifies deterministic compliance rules, FX currency normalization, and fail-loud error handling.
"""

import sys
from pathlib import Path

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


def test_fail_loud_on_ai_unreachable():
    """Verify P0-1 fix: When AI is unreachable, system fails loudly with analysis_mode='failed' and zero fabricated score."""
    form = StreamlinedLeadForm(
        company_name="Test Unreachable Inc",
        currency_symbol="$",
        currency_code="USD",
        revenue_entered_value=1.0,
        revenue_unit="Thousands (k)",
        deal_entered_value=1.0,
        deal_unit="Exact / Standard",
        industry_sector="Technology",
        sub_vertical="Software",
        annual_revenue_usd=1000.0,
        employee_count=1,
        location="Austin, Texas, United States",
        contact_name="Test User",
        contact_role_title="Manager",
        buying_intent="Testing",
        target_deal_size_usd=1.0
    )
    cfg = CompanyStandardsConfig()

    # Pass an invalid unreachable worker URL
    result: StreamlinedScoringResult = GTMScoringEngine.evaluate(
        form=form,
        config=cfg,
        worker_url="http://127.0.0.1:1/nonexistent"
    )

    # Must fail loud: no fake 75.2 score, no fake Tier A2
    assert result.analysis_mode == "failed"
    assert result.master_icp_score == 0.0
    assert "Offline" in result.priority_tier
    assert len(result.degraded_reasons) > 0


def test_buying_role_timeline_budget_range():
    """Verify buying_role, timeline, and budget range fields in lead form and receipts."""
    form = StreamlinedLeadForm(
        company_name="Apex Energy Solutions",
        currency_symbol="$",
        currency_code="USD",
        revenue_entered_value=50.0,
        revenue_unit="Millions (M)",
        deal_entered_value=75.0,
        deal_unit="Thousands (k)",
        deal_display_str="$75k USD",
        industry_sector="Energy & Renewables",
        sub_vertical="Grid Modernization",
        annual_revenue_usd=50_000_000.0,
        employee_count=350,
        location="Houston, Texas, United States",
        contact_name="Sarah Jenkins",
        contact_role_title="VP Energy Infrastructure",
        buying_role="Economic Buyer / Decision Maker",
        buying_intent="Active ERP integration evaluation",
        timeline="1 – 3 Months (Current Quarter)",
        target_deal_size_usd=75_000.0
    )
    assert form.buying_role == "Economic Buyer / Decision Maker"
    assert form.timeline == "1 – 3 Months (Current Quarter)"


if __name__ == "__main__":
    print("Running test_fx_conversion_inr_crores...")
    test_fx_conversion_inr_crores()
    print("[PASS] test_fx_conversion_inr_crores passed.")

    print("Running test_fx_conversion_eur_thousands...")
    test_fx_conversion_eur_thousands()
    print("[PASS] test_fx_conversion_eur_thousands passed.")

    print("Running test_deterministic_sanctions_disqualification...")
    test_deterministic_sanctions_disqualification()
    print("[PASS] test_deterministic_sanctions_disqualification passed.")

    print("Running test_deterministic_anti_icp_role...")
    test_deterministic_anti_icp_role()
    print("[PASS] test_deterministic_anti_icp_role passed.")

    print("Running test_fail_loud_on_ai_unreachable...")
    test_fail_loud_on_ai_unreachable()
    print("[PASS] test_fail_loud_on_ai_unreachable passed.")

    print("Running test_buying_role_timeline_budget_range...")
    test_buying_role_timeline_budget_range()
    print("[PASS] test_buying_role_timeline_budget_range passed.")

    print("\nALL 6 TESTS PASSED SUCCESSFULLY!")

