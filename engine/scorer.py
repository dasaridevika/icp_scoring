"""
Step 2, 3 & 4: Four-Pillar Scoring Engine, Master ICP Aggregator & Operational Sales Activation.
Framework: GTM Partners & Saber ICP Model.
Supports 100% Dynamic Cloudflare Worker AI Evaluation + High-Precision Entity Evaluation.
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
    Evaluates extracted prospect data across the 4 core pillars using the
    GTM Partners forced-choice scale: {-5, -3, -1, +1, +3, +5}, aggregates the Master ICP Score,
    and operationalizes sales cadences, 2D Fit vs Intent matrices, and CRM payloads.
    """

    # Weights defined by the Saber ICP model
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
        -5: "-5: High Churn Risk / Academic or Non-Commercial"
    }

    # Normalized 0-100 conversion from GTM scale
    GTM_TO_SCORE_100 = {
        5: 95.0,
        3: 75.0,
        1: 55.0,
        -1: 45.0,
        -3: 25.0,
        -5: 5.0
    }

    # Generic worker fallback markers to detect when AI needs rich local refinement
    GENERIC_FALLBACK_RATIONALES = [
        "Evaluated enterprise profile against ICP target scale.",
        "Evaluated tech stack readiness and analytics maturity.",
        "Active commercial evaluation and procurement interest.",
        "Executive persona with decision-making capability.",
        "Position tailored enterprise intelligence to accelerate core business objectives."
    ]

    @classmethod
    def score_to_gtm_scale(cls, raw_score: float, is_uncertain: bool = False, is_disqualified: bool = False) -> Tuple[int, float]:
        """Maps any dynamic 0-100 score from Worker AI to the GTM Partners {-5, -3, -1, +1, +3, +5} scale."""
        if is_disqualified or raw_score <= 15:
            return -5, 5.0
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
        Evaluates the 4 core dimensions on the GTM scale and returns a structured breakdown.
        """
        firmo_eval = cls.evaluate_firmographic(prospect)
        techno_eval = cls.evaluate_technographic(prospect)
        intent_eval = cls.evaluate_intent(prospect)
        persona_eval = cls.evaluate_persona(prospect)

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
        enforces negative scoring / disqualification guardrails, and operationalizes
        Sales SLAs, Fit vs Intent 2D matrices, personalized sales copy, and CRM sync payloads.
        """
        f = breakdown.firmographic
        t = breakdown.technographic
        i = breakdown.intent
        p = breakdown.persona

        # Sum of weighted contribution points
        calculated_points = round(f.points_contributed + t.points_contributed + i.points_contributed + p.points_contributed)
        calculated_points = max(0, min(100, calculated_points))

        # Check Disqualification (Students, Interns, Non-commercial leads)
        is_disqualified = False
        disqualify_reason = ""

        # Check AI disqualification flag or persona disqualification
        ai_data = prospect.raw_ai_payload or {}
        if ai_data.get("is_disqualified") or p.gtm_scale == -5 or "student" in prospect.job_title.lower() or "intern" in prospect.job_title.lower():
            is_disqualified = True
            disqualify_reason = ai_data.get("disqualification_reason") or "Academic / Non-Commercial Inquiry (Zero commercial budget authority)"
            final_score = 12
            tier_name = "Out of ICP / Disqualified (<40)"
            priority_level = "Disqualified / Deprioritized"
            sales_action = "Route to public self-serve documentation / open whitepapers. Preserve AE and sales calling bandwidth."
            conversion_prob = 2
            val_wedge = "Direct non-commercial inquiries to public self-serve research documentation."
            first_name = prospect.contact_name.split()[0] if prospect.contact_name else "there"
            outreach_hook = f"Hi {first_name}, for coursework and academic research please check our open research library."
        else:
            final_score = calculated_points
            first_name = prospect.contact_name.split()[0] if prospect.contact_name else "there"
            ai_strategy = ai_data.get("strategy") or {}
            raw_wedge = ai_strategy.get("value_wedge") or ""
            raw_hook = ai_strategy.get("outreach_hook") or ""
            
            is_generic_strat = any(g in raw_wedge for g in cls.GENERIC_FALLBACK_RATIONALES)

            if final_score >= 80:
                tier_name = "Tier 1: Dream ICP (80-100)"
                priority_level = "High Priority / Strategic Account"
                sales_action = "Immediate outreach (<2h) by Senior AE & Research Director. Deliver bespoke proposal & schedule technical scoping call."
                conversion_prob = min(98, max(5, round(final_score * 0.94)))
                val_wedge = (raw_wedge if not is_generic_strat and raw_wedge else f"Deliver bespoke intelligence feeds and analyst advisory to de-risk {prospect.company_name}'s strategic investments.")
                outreach_hook = (raw_hook if not is_generic_strat and raw_hook else f"Hi {first_name}, saw {prospect.company_name}'s strategic roadmap in the sector and wanted to share our latest intelligence benchmark relevant to your project timeline.")
            elif final_score >= 60:
                tier_name = "Tier 2: Strong Fit (60-79)"
                priority_level = "Standard Sales Pipeline"
                sales_action = "Standard SDR outbound cadence within 24h. Schedule discovery qualification call and conduct product demonstration."
                conversion_prob = min(98, max(5, round(final_score * 0.90)))
                val_wedge = (raw_wedge if not is_generic_strat and raw_wedge else f"Equip {prospect.company_name}'s team with actionable market benchmarking to accelerate pipeline efficiency.")
                outreach_hook = (raw_hook if not is_generic_strat and raw_hook else f"Hi {first_name}, noticed your focus on benchmarking growth at {prospect.company_name} and thought our data feeds would be timely for your team.")
            elif final_score >= 40:
                tier_name = "Tier 3: Moderate Fit (40-59)"
                priority_level = "Inside Sales / Automated Nurture"
                sales_action = "Enroll in automated product nurture drip sequences, invite to bi-weekly webinars, and track expansion triggers."
                conversion_prob = min(98, max(5, round(final_score * 0.85)))
                val_wedge = (raw_wedge if not is_generic_strat and raw_wedge else f"Provide self-serve intelligence modules and flexible pricing options aligned with {prospect.company_name}'s growth.")
                outreach_hook = (raw_hook if not is_generic_strat and raw_hook else f"Hi {first_name}, glad to see your team's work in {prospect.industry}. Sharing our latest industry benchmark as you plan upcoming milestones.")
            else:
                tier_name = "Out of ICP / Disqualified (<40)"
                priority_level = "Deprioritized / Low Priority"
                sales_action = "Route to marketing newsletter / self-serve knowledge base. Preserve direct sales capacity."
                conversion_prob = 15
                val_wedge = "Direct to open knowledge base."
                outreach_hook = f"Hi {first_name}, please check our open knowledge base for resources."

        # Step 4: 2D Fit vs Intent Matrices (6sense & MadKudu)
        fit_index = round((f.score_100 * 0.55) + (t.score_100 * 0.45))
        intent_index = round((i.score_100 * 0.55) + (p.score_100 * 0.45))

        # Step 3 & 4 Revenue Forecasting
        quality_weighted_val = round(deal_size_usd * (final_score / 100.0))

        # Step 4: Strategy Object
        strategy = StrategyRecommendation(
            value_wedge=val_wedge,
            outreach_hook=outreach_hook
        )

        # Step 4: CRM Sync Payload
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

    @classmethod
    def evaluate_firmographic(cls, p: ExtractedProspectData) -> PillarEvaluation:
        ai_pillars = (p.raw_ai_payload or {}).get("pillar_scores") or {}
        ai_rat = ai_pillars.get("firmographic_rationale") or (ai_pillars.get("firmographic") or {}).get("rationale") or ""
        
        # Check if AI returned a custom bespoke rationale (not generic fallback)
        is_generic_ai = not ai_rat or any(g in ai_rat for g in cls.GENERIC_FALLBACK_RATIONALES)
        
        if not is_generic_ai and ("firmographic_score" in ai_pillars or "firmographic" in ai_pillars):
            ai_score = float(ai_pillars.get("firmographic_score") or ai_pillars.get("firmographic", {}).get("score", 70))
            is_unc = "Company Scale / Revenue" in p.uncertain_fields and "Industry & Vertical" in p.uncertain_fields
            scale_val, score_100 = cls.score_to_gtm_scale(ai_score, is_uncertain=is_unc)
            return PillarEvaluation(
                name="Firmographics Fit",
                weight=cls.WEIGHT_FIRMO,
                gtm_scale=scale_val,
                gtm_label=cls.GTM_SCALE_LABELS[scale_val],
                score_100=score_100,
                points_contributed=round(score_100 * cls.WEIGHT_FIRMO, 1),
                rationale=ai_rat,
                is_uncertain=is_unc
            )

        # High-Precision Entity Evaluation
        text_l = (p.scale_revenue + " " + p.industry + " " + p.raw_text).lower()
        is_uncertain = "Company Scale / Revenue" in p.uncertain_fields and "Industry & Vertical" in p.uncertain_fields

        if is_uncertain:
            scale_val = -1
            rat = "Company scale and industry unspecified in inbound lead. Assigned neutral uncertainty baseline."
        elif any(k in text_l for k in ["student", "university", "thesis", "assignment", "intern"]):
            scale_val = -5
            rat = "Academic/non-commercial institution profile. Lacks commercial enterprise budget scale."
        elif any(k in text_l for k in ["billion", "$1b", "$10b", "$38b", "$500m", "$450m", "$600m", "10,000", "enterprise", "fortune 500", "1,200", "3,000"]):
            scale_val = 5
            rat = f"Enterprise-scale commercial footprint for {p.company_name}. Massive revenue scale and ideal market vertical."
        elif any(k in text_l for k in ["$65m", "$50m", "$100m", "220 employees", "500 employees", "mid-market", "growth stage"]):
            scale_val = 3
            rat = f"Established mid-market growth profile ({p.company_name}). Solid revenue scale and strong departmental budgets."
        elif any(k in text_l for k in ["seed", "pre-revenue", "12 employees", "early-stage", "startup", "bootstrapped"]):
            scale_val = 1
            rat = f"Early-stage profile for {p.company_name}. Operating capital is serviceable but near-term expansion is limited."
        else:
            scale_val = 3
            rat = f"Commercial B2B profile evaluated for {p.company_name}."

        score_100 = cls.GTM_TO_SCORE_100[scale_val]
        return PillarEvaluation(
            name="Firmographics Fit",
            weight=cls.WEIGHT_FIRMO,
            gtm_scale=scale_val,
            gtm_label=cls.GTM_SCALE_LABELS[scale_val],
            score_100=score_100,
            points_contributed=round(score_100 * cls.WEIGHT_FIRMO, 1),
            rationale=rat,
            is_uncertain=(scale_val == -1)
        )

    @classmethod
    def evaluate_technographic(cls, p: ExtractedProspectData) -> PillarEvaluation:
        ai_pillars = (p.raw_ai_payload or {}).get("pillar_scores") or {}
        ai_rat = ai_pillars.get("technographic_rationale") or (ai_pillars.get("technographic") or {}).get("rationale") or ""
        
        is_generic_ai = not ai_rat or any(g in ai_rat for g in cls.GENERIC_FALLBACK_RATIONALES)

        if not is_generic_ai and ("technographic_score" in ai_pillars or "technographic" in ai_pillars):
            ai_score = float(ai_pillars.get("technographic_score") or ai_pillars.get("technographic", {}).get("score", 70))
            is_unc = "Technographic Infrastructure" in p.uncertain_fields
            scale_val, score_100 = cls.score_to_gtm_scale(ai_score, is_uncertain=is_unc)
            return PillarEvaluation(
                name="Technographics Fit",
                weight=cls.WEIGHT_TECHNO,
                gtm_scale=scale_val,
                gtm_label=cls.GTM_SCALE_LABELS[scale_val],
                score_100=score_100,
                points_contributed=round(score_100 * cls.WEIGHT_TECHNO, 1),
                rationale=ai_rat,
                is_uncertain=is_unc
            )

        # High-Precision Entity Evaluation
        text_l = (p.technographics + " " + p.raw_text).lower()
        is_uncertain = "Technographic Infrastructure" in p.uncertain_fields

        if is_uncertain:
            scale_val = -1
            rat = "No technology stack disclosed in initial inquiry. Assigned neutral uncertainty baseline."
        elif any(k in text_l for k in ["student", "thesis", "assignment"]):
            scale_val = -5
            rat = "Educational tooling environment without enterprise CRM/data infrastructure."
        elif any(k in text_l for k in ["sap", "oracle", "snowflake", "salesforce", "enterprise erp", "powerbi", "databricks"]):
            scale_val = 5
            rat = f"Advanced enterprise technology stack ({p.technographics}). High data maturity and seamless API integration readiness."
        elif any(k in text_l for k in ["hubspot", "tableau", "google workspace", "aws", "azure", "gcp"]):
            scale_val = 3
            rat = f"Modern cloud stack ({p.technographics}). Strong digital readiness for intelligence dashboards and CRM sync."
        elif any(k in text_l for k in ["notion", "slack", "sheets", "excel"]):
            scale_val = 1
            rat = "Lightweight productivity tooling. Serviceable for basic workflows, but limited data warehouse maturity."
        else:
            scale_val = 3
            rat = "Standard technology infrastructure evaluated."

        score_100 = cls.GTM_TO_SCORE_100[scale_val]
        return PillarEvaluation(
            name="Technographics Fit",
            weight=cls.WEIGHT_TECHNO,
            gtm_scale=scale_val,
            gtm_label=cls.GTM_SCALE_LABELS[scale_val],
            score_100=score_100,
            points_contributed=round(score_100 * cls.WEIGHT_TECHNO, 1),
            rationale=rat,
            is_uncertain=(scale_val == -1)
        )

    @classmethod
    def evaluate_intent(cls, p: ExtractedProspectData) -> PillarEvaluation:
        ai_pillars = (p.raw_ai_payload or {}).get("pillar_scores") or {}
        ai_rat = ai_pillars.get("intent_rationale") or (ai_pillars.get("intent") or {}).get("rationale") or ""
        
        is_generic_ai = not ai_rat or any(g in ai_rat for g in cls.GENERIC_FALLBACK_RATIONALES)

        if not is_generic_ai and ("intent_score" in ai_pillars or "intent" in ai_pillars):
            ai_score = float(ai_pillars.get("intent_score") or ai_pillars.get("intent", {}).get("score", 70))
            is_unc = "Intent & Project Timeline" in p.uncertain_fields
            scale_val, score_100 = cls.score_to_gtm_scale(ai_score, is_uncertain=is_unc)
            return PillarEvaluation(
                name="Intent & Timing Signals",
                weight=cls.WEIGHT_INTENT,
                gtm_scale=scale_val,
                gtm_label=cls.GTM_SCALE_LABELS[scale_val],
                score_100=score_100,
                points_contributed=round(score_100 * cls.WEIGHT_INTENT, 1),
                rationale=ai_rat,
                is_uncertain=is_unc
            )

        # High-Precision Entity Evaluation
        text_l = (p.intent_urgency + " " + p.raw_text).lower()
        is_uncertain = "Intent & Project Timeline" in p.uncertain_fields

        if is_uncertain:
            scale_val = -1
            rat = "Procurement timeline and budget urgency not stated. Assigned neutral uncertainty baseline."
        elif any(k in text_l for k in ["student", "thesis", "class assignment"]):
            scale_val = -5
            rat = "Academic coursework inquiry without commercial buying intent."
        elif any(k in text_l for k in ["active rfp", "3 weeks", "2 weeks", "q3/q4 capex", "procurement budget", "actively preparing", "immediate", "urgent", "end of q3"]):
            scale_val = 5
            rat = "Immediate buying urgency. Active RFP/CapEx mandate with strict evaluation timeline."
        elif any(k in text_l for k in ["demo", "next quarter", "evaluating", "team license", "benchmark", "q2", "q3"]):
            scale_val = 3
            rat = "Clear near-term evaluation window. Looking to deploy intelligence before the next fiscal quarter."
        elif any(k in text_l for k in ["6-9 months", "series a", "no budget yet", "exploring", "future"]):
            scale_val = 1
            rat = "Delayed purchasing cycle. Budget contingent on future milestones or subsequent funding."
        else:
            scale_val = 3
            rat = "Active inquiry with standard quarterly evaluation cycle."

        score_100 = cls.GTM_TO_SCORE_100[scale_val]
        return PillarEvaluation(
            name="Intent & Timing Signals",
            weight=cls.WEIGHT_INTENT,
            gtm_scale=scale_val,
            gtm_label=cls.GTM_SCALE_LABELS[scale_val],
            score_100=score_100,
            points_contributed=round(score_100 * cls.WEIGHT_INTENT, 1),
            rationale=rat,
            is_uncertain=(scale_val == -1)
        )

    @classmethod
    def evaluate_persona(cls, p: ExtractedProspectData) -> PillarEvaluation:
        ai_pillars = (p.raw_ai_payload or {}).get("pillar_scores") or {}
        ai_rat = ai_pillars.get("persona_rationale") or (ai_pillars.get("persona") or {}).get("rationale") or ""
        
        is_generic_ai = not ai_rat or any(g in ai_rat for g in cls.GENERIC_FALLBACK_RATIONALES)

        if not is_generic_ai and ("persona_score" in ai_pillars or "persona" in ai_pillars):
            ai_score = float(ai_pillars.get("persona_score") or ai_pillars.get("persona", {}).get("score", 70))
            is_unc = "Decision Maker Persona" in p.uncertain_fields
            scale_val, score_100 = cls.score_to_gtm_scale(ai_score, is_uncertain=is_unc)
            return PillarEvaluation(
                name="Persona & Buying Authority",
                weight=cls.WEIGHT_PERSONA,
                gtm_scale=scale_val,
                gtm_label=cls.GTM_SCALE_LABELS[scale_val],
                score_100=score_100,
                points_contributed=round(score_100 * cls.WEIGHT_PERSONA, 1),
                rationale=ai_rat,
                is_uncertain=is_unc
            )

        # High-Precision Entity Evaluation
        text_l = (p.job_title + " " + p.contact_name + " " + p.raw_text).lower()
        title_l = p.job_title.lower()
        is_uncertain = "Decision Maker Persona" in p.uncertain_fields

        if any(k in title_l for k in ["student", "intern", "researcher", "job seeker", "applicant"]):
            scale_val = -5
            rat = f"{p.contact_name} ({p.job_title}) holds zero commercial budget authority (Disqualified Lead)."
        elif is_uncertain:
            scale_val = -1
            rat = "Job title and decision maker role unverified. Assigned neutral uncertainty baseline."
        elif any(k in title_l for k in ["chief", "c-suite", "cto", "cfo", "cro", "cso", "vp", "vice president", "partner"]):
            scale_val = 5
            rat = f"{p.contact_name} ({p.job_title}) holds direct executive mandate and budget signing authority."
        elif any(k in title_l for k in ["director", "head of", "lead", "general manager"]):
            scale_val = 3
            rat = f"{p.contact_name} ({p.job_title}) is a key departmental decision maker with direct project budget allocation."
        elif any(k in title_l for k in ["manager", "product manager", "analyst", "specialist"]):
            scale_val = 1
            rat = f"{p.contact_name} ({p.job_title}) represents an evaluator who must secure executive sponsor sign-off."
        else:
            scale_val = 3
            rat = f"{p.contact_name} ({p.job_title}) holds standard evaluation capacity."

        score_100 = cls.GTM_TO_SCORE_100[scale_val]
        return PillarEvaluation(
            name="Persona & Buying Authority",
            weight=cls.WEIGHT_PERSONA,
            gtm_scale=scale_val,
            gtm_label=cls.GTM_SCALE_LABELS[scale_val],
            score_100=score_100,
            points_contributed=round(score_100 * cls.WEIGHT_PERSONA, 1),
            rationale=rat,
            is_uncertain=(scale_val == -1)
        )
