"""
Enterprise ICP Intelligence Engine - Deterministic Evidence-Aware Scorer.
100% Deterministic: Evaluates validated evidence against authoritative weights,
tier thresholds, and disqualification gates.
Missing data is explicitly UNKNOWN (confidence 0, score 0 contribution).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .models import (
    EvidenceStatus,
    EvidenceField,
    EvidencePillar,
    DimensionScore,
    ICPFitScore,
    IntentScore,
    ReadinessScore,
    ValueScore,
    EligibilityResult,
    ExpectedValueResult,
    NextBestAction,
    AccountInfo,
    ScoresBreakdown,
    ConfidenceBreakdown,
    EvidenceBreakdown,
    DecisionInfo,
    CommercialInfo,
    AssessmentMetadata,
    AccountAssessment,
    MasterAccountIntelligence,
    SimilarCustomerMatch
)
from .config import EngineConfiguration, active_config
from .disqualifier import DisqualificationEngine
from .calibration import global_calibrator


class MasterScoringEngine:
    """
    Deterministic revenue intelligence and ICP qualification engine.
    The AI extracts and interprets evidence; this engine owns the final deterministic scores and tiers.
    """

    @classmethod
    def evaluate_assessment(
        cls,
        account_data: Dict[str, Any],
        evidence_data: Dict[str, Any],
        deal_size_usd: float = 50000.0,
        strategy_data: Optional[Dict[str, Any]] = None,
        discovery_questions: Optional[List[str]] = None,
        key_strengths: Optional[List[str]] = None,
        key_risks: Optional[List[str]] = None,
        is_disqualified: bool = False,
        disqualification_reason: str = "",
        config: Optional[EngineConfiguration] = None,
        request_id: Optional[str] = None
    ) -> AccountAssessment:
        cfg = config or active_config
        strategy = strategy_data or {}
        req_id = request_id or f"req_{int(datetime.now(timezone.utc).timestamp()*1000)}"

        # 1. Parse Account Info
        company_name = account_data.get("company_name")
        domain = account_data.get("domain") or ""
        contact_name = account_data.get("contact_name")
        job_title = account_data.get("job_title")
        industry = account_data.get("industry")
        scale = account_data.get("scale")
        tech_stack = account_data.get("tech_stack")
        intent_timeline = account_data.get("intent_timeline")

        account_info = AccountInfo(
            company_name=company_name,
            domain=domain if domain else None,
            contact_name=contact_name,
            job_title=job_title,
            industry=industry,
            scale=scale,
            tech_stack=tech_stack,
            intent_timeline=intent_timeline
        )

        # 2. Hard Eligibility Check
        eligibility: EligibilityResult = DisqualificationEngine.evaluate(
            email_or_domain=domain,
            industry=industry or "",
            config=cfg
        )
        if is_disqualified and disqualification_reason:
            eligibility.eligible = False
            if disqualification_reason not in eligibility.disqualification_reasons:
                eligibility.disqualification_reasons.append(disqualification_reason)

        # 3. Helper to normalize pillar evidence
        def parse_pillar(key: str) -> EvidencePillar:
            p_data = evidence_data.get(key) or {}
            raw_score = p_data.get("score")
            raw_status = p_data.get("status")
            status = raw_status if raw_status in EvidenceStatus._value2member_map_ else (
                EvidenceStatus.UNKNOWN if raw_score is None else EvidenceStatus.INFERRED
            )
            score = float(raw_score) if (raw_score is not None and status != EvidenceStatus.UNKNOWN) else None
            confidence = 0.0 if status == EvidenceStatus.UNKNOWN else max(0.0, min(1.0, float(p_data.get("confidence", 0.5))))
            return EvidencePillar(
                score=score,
                status=status,
                confidence=round(confidence, 2),
                evidence_points=p_data.get("evidence_points") or [],
                rationale=p_data.get("rationale") or "",
                missing_points=p_data.get("missing_points") or []
            )

        p_firmo = parse_pillar("firmographic")
        p_techno = parse_pillar("technographic")
        p_intent = parse_pillar("intent")
        p_readiness = parse_pillar("readiness")
        p_value = parse_pillar("value")

        # 4. Deterministic 4-Dimensional Scoring
        # 4.1 ICP Fit Score (Firmographic & Technographic)
        fit_score_val = 0.0
        fit_weight_sum = 0.0
        if p_firmo.status != EvidenceStatus.UNKNOWN and p_firmo.score is not None:
            fit_score_val += p_firmo.score * 0.65
            fit_weight_sum += 0.65
        if p_techno.status != EvidenceStatus.UNKNOWN and p_techno.score is not None:
            fit_score_val += p_techno.score * 0.35
            fit_weight_sum += 0.35
        icp_fit_final = round(fit_score_val / fit_weight_sum, 1) if fit_weight_sum > 0 else 0.0
        icp_fit_conf = round((p_firmo.confidence * 0.65) + (p_techno.confidence * 0.35), 2)

        # 4.2 Intent Score
        intent_final = round(p_intent.score, 1) if (p_intent.status != EvidenceStatus.UNKNOWN and p_intent.score is not None) else 0.0
        intent_conf = p_intent.confidence

        # 4.3 Readiness Score
        readiness_final = round(p_readiness.score, 1) if (p_readiness.status != EvidenceStatus.UNKNOWN and p_readiness.score is not None) else 0.0
        readiness_conf = p_readiness.confidence

        # 4.4 Value Score
        value_final = round(p_value.score, 1) if (p_value.status != EvidenceStatus.UNKNOWN and p_value.score is not None) else 0.0
        value_conf = p_value.confidence

        # 4.5 Master ICP Score (Authoritative Weighted Combination)
        mw = cfg.master_weights
        if not eligibility.eligible:
            master_icp = 0.0
        else:
            master_icp = round(
                (icp_fit_final * mw.icp_fit) +
                (intent_final * mw.intent) +
                (readiness_final * mw.readiness) +
                (value_final * mw.value),
                1
            )

        overall_conf = round(
            (icp_fit_conf * mw.icp_fit) +
            (intent_conf * mw.intent) +
            (readiness_conf * mw.readiness) +
            (value_conf * mw.value),
            2
        )

        scores_breakdown = ScoresBreakdown(
            icp_fit=icp_fit_final,
            intent=intent_final,
            readiness=readiness_final,
            value=value_final,
            master_icp_score=master_icp
        )

        confidence_breakdown = ConfidenceBreakdown(
            overall=overall_conf,
            icp_fit=icp_fit_conf,
            intent=intent_conf,
            readiness=readiness_conf,
            value=value_conf
        )

        # 5. Determine Business Tier & Next Best Action
        tt = cfg.tier_thresholds
        if not eligibility.eligible:
            tier = "Disqualified / Anti-ICP"
            priority = "Disqualified"
            action = "Disqualify account and route to self-service knowledge base."
            sla = "Automated Deprioritization"
            channel = "Self-Serve Portal"
        elif icp_fit_final >= tt.tier_a1_min_fit and intent_final >= tt.tier_a1_min_intent:
            tier = "Tier A1: Strategic Inbound"
            priority = "High (Strategic)"
            action = f"Fast-track to Senior AE. Schedule discovery meeting within 2 hours."
            sla = "Immediate outreach (<2 hours)"
            channel = "Executive Phone & Video"
        elif icp_fit_final >= tt.tier_a2_min_fit:
            tier = "Tier A2: High Priority Outbound"
            priority = "High"
            action = f"Launch strategic SDR outbound sequence targeting {job_title or 'Decision Maker'}."
            sla = "SDR cadence within 24 hours"
            channel = "Multi-touch Email + LinkedIn InMail"
        elif icp_fit_final >= tt.tier_b1_min_fit and intent_final >= tt.tier_b1_min_intent:
            tier = "Tier B1: Mid-Market Fast Track"
            priority = "Medium"
            action = "Route to Inside Sales for qualification call."
            sla = "Inside Sales follow-up (<24 hours)"
            channel = "Direct Email & Discovery Call"
        elif icp_fit_final >= tt.tier_a3_min_fit:
            tier = "Tier A3: Outbound Nurture"
            priority = "Low-Medium"
            action = "Enroll account in automated product webinars and educational sequences."
            sla = "Bi-weekly marketing nurture"
            channel = "Automated Marketing Sequences"
        else:
            tier = "Tier C: Low Priority / Long-Tail"
            priority = "Low"
            action = "Preserve sales capacity. Route to marketing newsletter."
            sla = "No direct sales SLA"
            channel = "Marketing Newsletter"

        val_wedge = strategy.get("value_wedge") or (
            f"Deliver enterprise intelligence to accelerate {company_name or 'the account'}'s strategic roadmap."
        )
        outreach_hook = strategy.get("outreach_hook") or (
            f"Reaching out regarding {company_name or 'your team'}'s strategic growth initiatives."
        )

        decision_info = DecisionInfo(
            tier=tier,
            priority=priority,
            sales_action=action,
            urgency_sla=sla,
            recommended_channel=channel,
            is_disqualified=not eligibility.eligible,
            disqualification_reason="; ".join(eligibility.disqualification_reasons),
            value_wedge=val_wedge,
            outreach_hook=outreach_hook
        )

        # 6. Commercial & Win Propensity Model
        propensity = global_calibrator.predict_propensity(
            icp_fit=icp_fit_final,
            intent=intent_final,
            readiness=readiness_final,
            value=value_final,
            confidence=overall_conf
        )
        if not eligibility.eligible:
            propensity = 0.0

        expansion_potential = "High" if value_final >= 75 else ("Moderate" if value_final >= 50 else "Limited")
        expected_arr = deal_size_usd
        expected_val_usd = round(propensity * expected_arr, 2)

        commercial_info = CommercialInfo(
            deal_size_usd=deal_size_usd,
            estimated_arr=expected_arr,
            win_propensity_pct=round(propensity * 100, 1),
            expected_value_usd=expected_val_usd,
            expansion_potential=expansion_potential
        )

        # 7. Collect Evidence, Unknowns, and Discovery Questions
        unknown_fields: List[str] = []
        if p_firmo.status == EvidenceStatus.UNKNOWN:
            unknown_fields.append("Firmographic scale / Headcount")
        if p_techno.status == EvidenceStatus.UNKNOWN:
            unknown_fields.append("Technographic stack")
        if p_intent.status == EvidenceStatus.UNKNOWN:
            unknown_fields.append("Intent urgency & timeline")
        if p_readiness.status == EvidenceStatus.UNKNOWN:
            unknown_fields.append("Decision maker authority")

        evidence_breakdown = EvidenceBreakdown(
            firmographic=p_firmo,
            technographic=p_techno,
            intent=p_intent,
            readiness=p_readiness,
            value=p_value,
            key_strengths=key_strengths or [],
            key_risks=key_risks or ([f"Hard Disqualifier: {r}" for r in eligibility.disqualification_reasons] if not eligibility.eligible else []),
            unknowns=unknown_fields,
            discovery_questions=discovery_questions or []
        )

        metadata = AssessmentMetadata(
            request_id=req_id,
            model_version=cfg.model_version,
            prompt_version="1.0.0",
            scored_at=datetime.now(timezone.utc).isoformat(),
            evaluation_engine="Deterministic Revenue Scorer + Worker AI",
            success=True
        )

        return AccountAssessment(
            account=account_info,
            scores=scores_breakdown,
            confidence=confidence_breakdown,
            evidence=evidence_breakdown,
            decision=decision_info,
            commercial=commercial_info,
            metadata=metadata
        )

    @classmethod
    def evaluate_account(
        cls,
        extracted_data: Dict[str, Any],
        deal_size_usd: float = 50000.0,
        config: Optional[EngineConfiguration] = None
    ) -> MasterAccountIntelligence:
        """
        Legacy interface mapping to the MasterAccountIntelligence schema.
        """
        assessment = cls.evaluate_assessment(
            account_data={
                "company_name": extracted_data.get("company_name"),
                "domain": extracted_data.get("domain"),
                "contact_name": extracted_data.get("contact_name"),
                "job_title": extracted_data.get("job_title"),
                "industry": extracted_data.get("industry")
            },
            evidence_data=extracted_data.get("evidence_fields") or {},
            deal_size_usd=deal_size_usd,
            strategy_data={
                "value_wedge": extracted_data.get("value_wedge"),
                "outreach_hook": extracted_data.get("outreach_hook")
            },
            discovery_questions=extracted_data.get("discovery_questions"),
            config=config
        )

        return MasterAccountIntelligence(
            account_id=f"ACC-{abs(hash(assessment.company_name or 'acc')) % 10000:04d}",
            company_name=assessment.company_name,
            domain=assessment.domain,
            contact_name=assessment.contact_name,
            job_title=assessment.job_title,
            industry=assessment.industry,
            model_version=assessment.metadata.model_version,
            scored_at=assessment.metadata.scored_at,
            overall_priority=assessment.priority_tier,
            overall_confidence=assessment.confidence.overall,
            key_strengths=assessment.key_strengths,
            key_risks_and_gaps=assessment.key_risks,
            crm_payload={
                "Account_Name__c": assessment.company_name,
                "ICP_Fit_Score__c": assessment.icp_fit_score,
                "Overall_Priority_Tier__c": assessment.priority_tier,
                "Request_ID__c": assessment.request_id
            }
        )

