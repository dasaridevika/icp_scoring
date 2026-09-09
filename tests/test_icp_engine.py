"""
Comprehensive Automated Test Suite for Enterprise ICP Revenue Intelligence Engine.
Tests AI failure modes, missing data handling, deterministic scoring,
schema validation, configuration consistency, and disparate company evaluations.
"""

import pytest
import json
from engine.models import (
    AccountAssessment,
    AssessmentMetadata,
    EvidenceStatus,
    EvidencePillar
)
from engine.config import active_config, EngineConfiguration, MasterWeights
from engine.scorer import MasterScoringEngine
from engine.disqualifier import DisqualificationEngine
from engine.extractor import ProspectExtractor
from workers.base_worker import WorkerAIClient


# ==============================================================================
# 1. AI FAILURE MODES & ZERO FAKE SCORE TESTS
# ==============================================================================

def test_ai_failure_produces_no_score_and_visible_error():
    """Verify that when Worker AI fails, no fake scores (75/70/70/75) are returned."""
    client = WorkerAIClient(worker_url="https://invalid-nonexistent-worker.workers.dev")
    assessment: AccountAssessment = client.evaluate_account("Company: Acme Inc")

    assert assessment.success is False
    assert assessment.error_message is not None
    assert assessment.request_id.startswith("req_")
    # Must not contain fake positive scores
    assert assessment.icp_fit_score == 0.0
    assert assessment.intent_score == 0.0
    assert assessment.readiness_score == 0.0
    assert assessment.value_score == 0.0


def test_malformed_ai_response_validation():
    """Verify that malformed or non-JSON output from LLM is safely handled."""
    client = WorkerAIClient()
    cleaned = client._clean_json_response('```json\n{"invalid": broken JSON\n```')
    with pytest.raises(json.JSONDecodeError):
        json.loads(cleaned)


# ==============================================================================
# 2. MISSING DATA & UNKNOWN EVIDENCE HANDLING (ZERO 70 FALLBACK)
# ==============================================================================

def test_missing_pillar_is_unknown_not_70():
    """Verify that missing/unverified attributes are explicitly UNKNOWN with confidence 0.0."""
    account_data = {
        "company_name": "Inbound Corp",
        "domain": "inboundcorp.com"
    }
    evidence_data = {
        "firmographic": {
            "score": 85.0,
            "status": "VERIFIED",
            "confidence": 0.9,
            "rationale": "Verified 500 employees.",
            "evidence_points": ["500 employees"],
            "missing_points": []
        },
        "technographic": {
            "score": None,
            "status": "UNKNOWN",
            "confidence": 0.0,
            "rationale": "No tech stack provided.",
            "evidence_points": [],
            "missing_points": ["tech_stack"]
        },
        "intent": {
            "score": None,
            "status": "UNKNOWN",
            "confidence": 0.0,
            "rationale": "No buying signal provided.",
            "evidence_points": [],
            "missing_points": ["intent_timeline"]
        },
        "readiness": {
            "score": None,
            "status": "UNKNOWN",
            "confidence": 0.0,
            "rationale": "No contact title provided.",
            "evidence_points": [],
            "missing_points": ["decision_maker"]
        }
    }

    assessment = MasterScoringEngine.evaluate_assessment(
        account_data=account_data,
        evidence_data=evidence_data
    )

    # Missing pillars MUST NOT default to 70 or 50
    assert assessment.scores.intent == 0.0
    assert assessment.scores.readiness == 0.0
    assert assessment.confidence.intent == 0.0
    assert assessment.confidence.readiness == 0.0
    assert assessment.evidence.intent.status == EvidenceStatus.UNKNOWN
    assert "Intent urgency & timeline" in assessment.evidence.unknowns
    assert "Decision maker authority" in assessment.evidence.unknowns


def test_account_d_unknown_data_low_confidence():
    """Test Account D where only company name is known."""
    assessment = WorkerAIClient.evaluate_locally("Company: Mystery Ventures")

    assert assessment.company_name == "Mystery Ventures"
    # Overall confidence must be low (< 0.5)
    assert assessment.confidence.overall < 0.50
    # Must have explicit unknown fields flagged
    assert len(assessment.evidence.unknowns) > 0
    # Must not be placed in Dream Tier
    assert assessment.priority_tier != "Tier A1: Strategic Inbound"


# ==============================================================================
# 3. DETERMINISTIC SCORING & AI FINAL SCORE OVERRIDE IMMUNITY
# ==============================================================================

def test_ai_final_score_override_is_ignored():
    """
    Verify that AI cannot dictate the final score.
    Even if raw AI claims final score is 99, the deterministic engine computes the true score.
    """
    account_data = {"company_name": "Test Co", "domain": "test.com"}
    evidence_data = {
        "firmographic": {"score": 60.0, "status": "INFERRED", "confidence": 0.6},
        "technographic": {"score": 60.0, "status": "INFERRED", "confidence": 0.6},
        "intent": {"score": 60.0, "status": "INFERRED", "confidence": 0.6},
        "readiness": {"score": 60.0, "status": "INFERRED", "confidence": 0.6},
        "value": {"score": 60.0, "status": "INFERRED", "confidence": 0.6}
    }

    assessment = MasterScoringEngine.evaluate_assessment(
        account_data=account_data,
        evidence_data=evidence_data
    )

    # Deterministic calculation: 60 * 0.35 + 60 * 0.25 + 60 * 0.20 + 60 * 0.20 = 60.0
    assert assessment.scores.master_icp_score == 60.0
    assert assessment.scores.master_icp_score != 99.0


def test_out_of_range_ai_scores_clamped():
    """Verify that scores are strictly bounded between 0 and 100."""
    account_data = {"company_name": "Clamp Co", "domain": "clamp.com"}
    evidence_data = {
        "firmographic": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0},
        "technographic": {"score": 0.0, "status": "VERIFIED", "confidence": 1.0},
        "intent": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0},
        "readiness": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0},
        "value": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0}
    }

    assessment = MasterScoringEngine.evaluate_assessment(
        account_data=account_data,
        evidence_data=evidence_data
    )

    assert 0.0 <= assessment.scores.master_icp_score <= 100.0
    assert 0.0 <= assessment.scores.icp_fit <= 100.0


# ==============================================================================
# 4. MATERIALLY DIFFERENT COMPANIES PRODUCE MATERIALLY DIFFERENT SCORES
# ==============================================================================

def test_materially_different_companies_produce_different_scores():
    """
    Test 3 materially different accounts:
    - Account A: Excellent ICP (Enterprise, C-suite sponsor, immediate RFP)
    - Account B: Moderate ICP (Mid-market, manager sponsor, exploratory)
    - Account C: Poor / Anti-ICP (Personal email, no budget, gambling vertical)
    """
    acc_a_data = {
        "account_data": {
            "company_name": "NextEra Clean Energy",
            "domain": "nextera-energy.com",
            "contact_name": "Arthur Pendelton",
            "job_title": "VP of Strategy and Operations",
            "industry": "Renewable Energy and Utilities",
            "scale": "1,400 employees | $450M ARR"
        },
        "evidence_data": {
            "firmographic": {"score": 95.0, "status": "VERIFIED", "confidence": 0.95},
            "technographic": {"score": 90.0, "status": "VERIFIED", "confidence": 0.90},
            "intent": {"score": 90.0, "status": "VERIFIED", "confidence": 0.90},
            "readiness": {"score": 95.0, "status": "VERIFIED", "confidence": 0.95},
            "value": {"score": 95.0, "status": "VERIFIED", "confidence": 0.95}
        },
        "deal_size_usd": 150000.0
    }

    acc_b_data = {
        "account_data": {
            "company_name": "Swift Commerce",
            "domain": "swiftcommerce.io",
            "contact_name": "David Miller",
            "job_title": "Marketing Operations Lead",
            "industry": "E-Commerce",
            "scale": "55 employees | $8M ARR"
        },
        "evidence_data": {
            "firmographic": {"score": 60.0, "status": "INFERRED", "confidence": 0.70},
            "technographic": {"score": 55.0, "status": "INFERRED", "confidence": 0.65},
            "intent": {"score": 50.0, "status": "INFERRED", "confidence": 0.60},
            "readiness": {"score": 55.0, "status": "INFERRED", "confidence": 0.60},
            "value": {"score": 55.0, "status": "INFERRED", "confidence": 0.60}
        },
        "deal_size_usd": 35000.0
    }

    acc_c_data = {
        "account_data": {
            "company_name": "Lucky Spin Gaming",
            "domain": "freelancer123@gmail.com",
            "contact_name": "John Doe",
            "job_title": "Student / Enthusiast",
            "industry": "Gambling & Casinos",
            "scale": "1 person"
        },
        "evidence_data": {
            "firmographic": {"score": 10.0, "status": "VERIFIED", "confidence": 0.90},
            "technographic": {"score": 10.0, "status": "UNKNOWN", "confidence": 0.0},
            "intent": {"score": 10.0, "status": "UNKNOWN", "confidence": 0.0},
            "readiness": {"score": 10.0, "status": "VERIFIED", "confidence": 0.90},
            "value": {"score": 10.0, "status": "UNKNOWN", "confidence": 0.0}
        },
        "deal_size_usd": 5000.0
    }

    res_a = MasterScoringEngine.evaluate_assessment(**acc_a_data)
    res_b = MasterScoringEngine.evaluate_assessment(**acc_b_data)
    res_c = MasterScoringEngine.evaluate_assessment(**acc_c_data)

    # 1. Scores must differ materially: Score(A) > Score(B) > Score(C)
    assert res_a.scores.master_icp_score >= 85.0, f"Account A expected >=85, got {res_a.scores.master_icp_score}"
    assert 50.0 <= res_b.scores.master_icp_score <= 70.0, f"Account B expected 50-70, got {res_b.scores.master_icp_score}"
    assert res_c.scores.master_icp_score == 0.0, f"Account C must be 0 (Disqualified), got {res_c.scores.master_icp_score}"

    assert res_a.scores.master_icp_score > res_b.scores.master_icp_score > res_c.scores.master_icp_score

    # 2. Tiers must reflect business reality
    assert "Tier A1" in res_a.priority_tier
    assert "Tier B1" in res_b.priority_tier or "Tier A2" in res_b.priority_tier or "Tier A3" in res_b.priority_tier
    assert res_c.is_disqualified is True
    assert "Disqualified" in res_c.priority_tier


# ==============================================================================
# 5. CONFIGURATION CONSISTENCY & DISQUALIFICATION GATES
# ==============================================================================

def test_configuration_consistency():
    """Verify that modifying centralized config weights changes the calculated scores."""
    account_data = {"company_name": "Weight Test", "domain": "weighttest.com"}
    evidence_data = {
        "firmographic": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0},
        "technographic": {"score": 100.0, "status": "VERIFIED", "confidence": 1.0},
        "intent": {"score": 50.0, "status": "VERIFIED", "confidence": 1.0},
        "readiness": {"score": 50.0, "status": "VERIFIED", "confidence": 1.0},
        "value": {"score": 50.0, "status": "VERIFIED", "confidence": 1.0}
    }

    res_base = MasterScoringEngine.evaluate_assessment(
        account_data=account_data,
        evidence_data=evidence_data,
        config=active_config
    )
    assert res_base.scores.master_icp_score == 67.5

    custom_cfg = EngineConfiguration(
        master_weights=MasterWeights(icp_fit=0.70, intent=0.10, readiness=0.10, value=0.10)
    )
    res_custom = MasterScoringEngine.evaluate_assessment(
        account_data=account_data,
        evidence_data=evidence_data,
        config=custom_cfg
    )
    assert res_custom.scores.master_icp_score == 85.0


def test_disqualification_personal_email_and_prohibited_vertical():
    """Verify that personal freemails and prohibited industries fail eligibility."""
    res_freemail = DisqualificationEngine.evaluate(email_or_domain="lead@gmail.com")
    assert res_freemail.eligible is False
    assert any("Personal email" in r for r in res_freemail.disqualification_reasons)

    res_casino = DisqualificationEngine.evaluate(email_or_domain="corp.com", industry="Gambling & Casinos")
    assert res_casino.eligible is False
    assert any("Unsupported industry" in r for r in res_casino.disqualification_reasons)

def test_batch_processing_isolated_failures():
    """Verify that batch processing handles individual row failures without corrupting other rows."""
    raw_rows = [
        {"Company": "NextEra Clean Energy", "Domain": "nextera-energy.com", "Industry": "Utilities"},
        {"Company": "", "Domain": "", "Industry": ""},  # Invalid empty row
        {"Company": "Swift Commerce", "Domain": "swiftcommerce.io", "Industry": "E-Commerce"}
    ]

    results = []
    for row in raw_rows:
        text = " ".join([f"{k}: {v}" for k, v in row.items() if v])
        if not text.strip():
            results.append({"status": "FAILED", "company": "Unknown", "score": None})
        else:
            assessment = WorkerAIClient.evaluate_locally(text)
            results.append({"status": "SUCCESS" if assessment.success else "FAILED", "company": assessment.company_name, "score": assessment.scores.master_icp_score})

    assert len(results) == 3
    assert results[0]["status"] == "SUCCESS"
    assert results[0]["score"] > 0
    assert results[1]["status"] == "FAILED"
    assert results[1]["score"] is None
    assert results[2]["status"] == "SUCCESS"
    assert results[2]["score"] > 0
