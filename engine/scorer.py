"""
Steps 2, 3 & 4: Pure Mathematical Qualification & Operational Scoring Engine.
100% Dynamic - Zero Hardcoded Keyword Dictionaries.
Driven purely by mathematical weights, AI evaluation scores, and GTM scale mapping.
"""

from typing import Dict, Any, Tuple
from .models import (
    ExtractedProspectData,
    PillarEvaluation,
    FourPillarBreakdown,
    StrategyRecommendation,
    MasterScoreResult
)


class PillarScorer:
    """
    Pure mathematical qualification engine implementing the Saber ICP model
    and GTM Partners forced-choice scale. Operates 100% dynamically on continuous scores.
    """

    # Exact mathematical weights defined by Saber ICP framework
    WEIGHT_FIRMO = 0.30
    WEIGHT_TECHNO = 0.25
    WEIGHT_INTENT = 0.25
    WEIGHT_PERSONA = 0.20

    GTM_SCALE_LABELS = {
        5: "+5: High Potential for Growth / Rapid Expansion",
        3: "+3: Clear Advantages / Strong Product-Market Fit",
        1: "+1: Serviceable / Limited Expansion Potential",
        -1: "-1: Uncertainty / Unspecified in Inbound Data",
        -3: "-3: High Resource Drain / Sub-Scale Economics",
        -5: "-5: High Churn Risk / Non-Commercial or Disqualified"
    }

    @classmethod
    def score_to_gtm_scale(cls, raw_score: float, is_uncertain: bool = False, is_disqualified: bool = False) -> Tuple[int, float]:
        """
        Dynamically maps continuous 0-100 score to the GTM Partners {-5, -3, -1, +1, +3, +5} scale.
        """
        if is_disqualified or raw_score <= 15:
            return -5, max(0.0, raw_score)
        if is_uncertain:
            return -1, 45.0
        if raw_score >= 85:
            return 5, raw_score
        if raw_score >= 65:
            return 3, raw_score
        if raw_score >= 45:
            return 1, raw_score
        if raw_score >= 25:
            return -3, raw_score
        return -5, raw_score

    @classmethod
    def evaluate_all_pillars(
        cls,
        prospect: ExtractedProspectData
    ) -> FourPillarBreakdown:
        """
        Extracts dimensional scores dynamically and maps them into structured PillarEvaluation objects.
        """
        ai_data = prospect.raw_ai_payload or {}
        pillars_raw = ai_data.get("pillar_scores") or {}

        # 1. Firmographic Fit (30% Weight)
        f_score_val = float(pillars_raw.get("firmographic_score") or (pillars_raw.get("firmographic") or {}).get("score", 70.0))
        f_rat = (pillars_raw.get("firmographic") or {}).get("rationale") or pillars_raw.get("firmographic_rationale") or f"Commercial scale and market vertical evaluation for {prospect.company_name}."
        f_unc = "Company Scale / Revenue" in prospect.uncertain_fields and "Industry & Vertical" in prospect.uncertain_fields
        f_scale, f_norm_score = cls.score_to_gtm_scale(f_score_val, is_uncertain=f_unc)

        firmo_eval = PillarEvaluation(
            name="Firmographics Fit",
            weight=cls.WEIGHT_FIRMO,
            gtm_scale=f_scale,
            gtm_label=cls.GTM_SCALE_LABELS[f_scale],
            score_100=f_norm_score,
            points_contributed=round(f_norm_score * cls.WEIGHT_FIRMO, 1),
            rationale=f_rat,
            is_uncertain=f_unc
        )

        # 2. Technographic Fit (25% Weight)
        t_score_val = float(pillars_raw.get("technographic_score") or (pillars_raw.get("technographic") or {}).get("score", 70.0))
        t_rat = (pillars_raw.get("technographic") or {}).get("rationale") or pillars_raw.get("technographic_rationale") or "Technology stack sophistication and data maturity assessment."
        t_unc = "Technographic Infrastructure" in prospect.uncertain_fields
        t_scale, t_norm_score = cls.score_to_gtm_scale(t_score_val, is_uncertain=t_unc)

        techno_eval = PillarEvaluation(
            name="Technographics Fit",
            weight=cls.WEIGHT_TECHNO,
            gtm_scale=t_scale,
            gtm_label=cls.GTM_SCALE_LABELS[t_scale],
            score_100=t_norm_score,
            points_contributed=round(t_norm_score * cls.WEIGHT_TECHNO, 1),
            rationale=t_rat,
            is_uncertain=t_unc
        )

        # 3. Intent & Timing (25% Weight)
        i_score_val = float(pillars_raw.get("intent_score") or (pillars_raw.get("intent") or {}).get("score", 70.0))
        i_rat = (pillars_raw.get("intent") or {}).get("rationale") or pillars_raw.get("intent_rationale") or "Procurement timeline urgency and active project budget evaluation."
        i_unc = "Intent & Project Timeline" in prospect.uncertain_fields
        i_scale, i_norm_score = cls.score_to_gtm_scale(i_score_val, is_uncertain=i_unc)

        intent_eval = PillarEvaluation(
            name="Intent & Timing Signals",
            weight=cls.WEIGHT_INTENT,
            gtm_scale=i_scale,
            gtm_label=cls.GTM_SCALE_LABELS[i_scale],
            score_100=i_norm_score,
            points_contributed=round(i_norm_score * cls.WEIGHT_INTENT, 1),
            rationale=i_rat,
            is_uncertain=i_unc
        )

        # 4. Persona & Authority (20% Weight)
        p_score_val = float(pillars_raw.get("persona_score") or (pillars_raw.get("persona") or {}).get("score", 70.0))
        p_rat = (pillars_raw.get("persona") or {}).get("rationale") or pillars_raw.get("persona_rationale") or f"Evaluation of buying mandate and decision-making oversight for {prospect.contact_name} ({prospect.job_title})."
        p_unc = "Decision Maker Persona" in prospect.uncertain_fields
        is_disq = bool(ai_data.get("is_disqualified")) or p_score_val == 0
        p_scale, p_norm_score = cls.score_to_gtm_scale(p_score_val, is_uncertain=p_unc, is_disqualified=is_disq)

        persona_eval = PillarEvaluation(
            name="Persona & Buying Authority",
            weight=cls.WEIGHT_PERSONA,
            gtm_scale=p_scale,
            gtm_label=cls.GTM_SCALE_LABELS[p_scale],
            score_100=p_norm_score,
            points_contributed=round(p_norm_score * cls.WEIGHT_PERSONA, 1),
            rationale=p_rat,
            is_uncertain=p_unc
        )

        return FourPillarBreakdown(
            firmographic=firmo_eval,
            technographic=techno_eval,
            intent=intent_eval,
            persona=persona_eval
        )

    @classmethod
    def compute_master_score(
        cls,
        prospect: ExtractedProspectData,
        breakdown: FourPillarBreakdown,
        deal_size_usd: float = 50000.0
    ) -> MasterScoreResult:
        """
        Step 3 & 4: Aggregates weighted pillar points into a Master Score (0-100),
        assigns Saber Tiers, Sales SLAs, 2D Fit vs Intent matrices, and CRM sync payload.
        """
        f = breakdown.firmographic
        t = breakdown.technographic
        i = breakdown.intent
        p = breakdown.persona

        ai_data = prospect.raw_ai_payload or {}
        is_disqualified = bool(ai_data.get("is_disqualified")) or p.gtm_scale == -5
        disqualify_reason = ai_data.get("disqualification_reason") or ("Academic / Non-Commercial inquiry without commercial budget authority" if is_disqualified else "")

        if is_disqualified:
            final_score = int(ai_data.get("final_icp_score", 12))
            tier_name = "Out of ICP / Disqualified (<40)"
            priority_level = "Disqualified / Deprioritized"
            sales_action = ai_data.get("sales_action") or "Route to public self-serve documentation / open whitepapers. Preserve AE and sales calling bandwidth."
            conversion_prob = 2
        else:
            # Mathematical Saber Weighted Formula: (0.30*F) + (0.25*T) + (0.25*I) + (0.20*P)
            calculated_points = round(f.points_contributed + t.points_contributed + i.points_contributed + p.points_contributed)
            final_score = int(ai_data.get("final_icp_score") or max(0, min(100, calculated_points)))

            if final_score >= 80:
                tier_name = "Tier 1: Dream ICP (80-100)"
                priority_level = "High Priority / Strategic Account"
                sales_action = ai_data.get("sales_action") or "Immediate outreach (<2h) by Senior AE & Research Director. Deliver bespoke proposal & schedule technical scoping call."
                conversion_prob = min(98, max(5, round(final_score * 0.94)))
            elif final_score >= 60:
                tier_name = "Tier 2: Strong Fit (60-79)"
                priority_level = "Standard Sales Pipeline"
                sales_action = ai_data.get("sales_action") or "Standard SDR outbound cadence within 24h. Schedule discovery qualification call and conduct product demonstration."
                conversion_prob = min(98, max(5, round(final_score * 0.90)))
            elif final_score >= 40:
                tier_name = "Tier 3: Moderate Fit (40-59)"
                priority_level = "Inside Sales / Automated Nurture"
                sales_action = ai_data.get("sales_action") or "Enroll in automated product nurture drip sequences, invite to bi-weekly webinars, and track expansion triggers."
                conversion_prob = min(98, max(5, round(final_score * 0.85)))
            else:
                tier_name = "Out of ICP / Disqualified (<40)"
                priority_level = "Deprioritized / Low Priority"
                sales_action = ai_data.get("sales_action") or "Route to marketing newsletter / self-serve knowledge base. Preserve direct sales capacity."
                conversion_prob = 15

        # 2D Matrix (Fit Index vs Intent Surge Index)
        fit_index = round((f.score_100 * 0.55) + (t.score_100 * 0.45))
        intent_index = round((i.score_100 * 0.55) + (p.score_100 * 0.45))

        # Quality Weighted Pipeline Valuation
        quality_weighted_val = round(deal_size_usd * (final_score / 100.0))

        # Strategy & Copy
        ai_strat = ai_data.get("strategy") or {}
        first_name = prospect.contact_name.split()[0] if prospect.contact_name and prospect.contact_name != "Unspecified Contact" else "there"
        
        val_wedge = ai_strat.get("value_wedge") or f"Deliver tailored intelligence and advisory to accelerate {prospect.company_name}'s strategic roadmap."
        outreach_hook = ai_strat.get("outreach_hook") or f"Hi {first_name}, reaching out regarding {prospect.company_name}'s strategic growth initiatives."

        strategy = StrategyRecommendation(
            value_wedge=val_wedge,
            outreach_hook=outreach_hook
        )

        # CRM Sync Payload
        crm_payload = {
            "ICP_Score_Total__c": final_score,
            "ICP_Fit_Tier__c": tier_name,
            "ICP_Priority_Level__c": priority_level,
            "ICP_Firmographic_Score__c": int(f.score_100),
            "ICP_Technographic_Score__c": int(t.score_100),
            "ICP_Intent_Score__c": int(i.score_100),
            "ICP_Persona_Score__c": int(p.score_100),
            "ICP_Account_Fit_Index__c": fit_index,
            "ICP_Intent_Surge_Index__c": intent_index,
            "ICP_Win_Probability__c": conversion_prob,
            "ICP_Weighted_Pipeline_USD__c": quality_weighted_val,
            "ICP_Disqualified__c": is_disqualified,
            "ICP_Disqualification_Reason__c": disqualify_reason,
            "SLA_Cadence_Action__c": sales_action,
            "Strategy_Value_Wedge__c": val_wedge,
            "Strategy_Outreach_Hook__c": outreach_hook
        }

        return MasterScoreResult(
            final_score=final_score,
            tier_name=tier_name,
            priority_level=priority_level,
            sales_action=sales_action,
            fit_index=fit_index,
            intent_index=intent_index,
            conversion_probability=conversion_prob,
            estimated_deal_size=deal_size_usd,
            quality_weighted_value=quality_weighted_val,
            is_disqualified=is_disqualified,
            disqualification_reason=disqualify_reason,
            pillars=breakdown,
            strategy=strategy,
            crm_payload=crm_payload
        )
