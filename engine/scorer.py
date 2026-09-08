"""
Core ICP Qualification & Scoring Engine.
Implements the Saber ICP Scoring Model Framework:
- 4 Weighted Pillars (30% Firmo, 25% Techno, 25% Intent, 20% Persona)
- Negative Scoring & Automatic Disqualification
- Dynamic Tier Segmentation & Sales SLAs
- 2D Fit vs. Intent Matrices (6sense / MadKudu)
- Quality-Weighted Revenue Forecasting
- Ready-to-Sync CRM JSON Payloads
"""

import re
from typing import Dict, Any, Optional
from .models import (
    PillarScore,
    PillarBreakdown,
    StrategyRecommendation,
    ICPScoreResult
)


class ICPScoringEngine:
    # Mathematical Weights defined by Saber ICP Model
    WEIGHT_FIRMOGRAPHIC = 0.30
    WEIGHT_TECHNOGRAPHIC = 0.25
    WEIGHT_INTENT = 0.25
    WEIGHT_PERSONA = 0.20

    # Disqualification Triggers (Negative Scoring)
    DISQUALIFYING_KEYWORDS = [
        "student", "university student", "class assignment", "thesis",
        "intern", "internship", "job application", "seeking job",
        "resume", "unemployed", "high school", "personal research"
    ]

    @staticmethod
    def clamp_score(value: Any, default: float = 50.0) -> float:
        """Sanitizes and clamps scores between 0 and 100."""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return max(0.0, min(100.0, float(value)))
        if isinstance(value, str):
            digits = re.findall(r"\d+", value)
            if digits:
                return max(0.0, min(100.0, float(digits[0])))
        return default

    @classmethod
    def evaluate(
        cls,
        raw_ai_data: Optional[Dict[str, Any]] = None,
        raw_text: str = "",
        deal_size_usd: float = 50000.0
    ) -> ICPScoreResult:
        """
        Evaluates lead data and produces a complete, normalized ICPScoreResult.
        """
        data = raw_ai_data or {}
        text = raw_text.strip()
        text_lower = text.lower()

        # 1. Entity Extraction & Normalization
        company = data.get("company_name") or "Target Account"
        contact = data.get("contact_name") or "Decision Maker"
        job_title = data.get("job_title") or "Executive"
        industry = data.get("industry") or "Enterprise B2B"

        # Heuristic entity recovery if defaults were returned
        if company in ["Target Account", "Target Prospect", "Account", ""] and text:
            for line in text.splitlines():
                clean = line.strip()
                if clean.lower().startswith(("company:", "company name:", "account:", "organization:")):
                    company = clean.split(":", 1)[1].strip()
                    break
            if company in ["Target Account", "Target Prospect", "Account", ""]:
                first_line = text.splitlines()[0].strip()
                if ":" not in first_line and 2 < len(first_line) < 60:
                    company = first_line

        if contact in ["Decision Maker", "Contact", ""] and text:
            for line in text.splitlines():
                clean = line.strip()
                if clean.lower().startswith(("contact:", "name:", "lead name:", "decision maker:")):
                    val = clean.split(":", 1)[1].strip()
                    contact = val.split("(")[0].strip() if "(" in val else val
                    break

        if job_title in ["Executive", "Unknown", ""] and text:
            for line in text.splitlines():
                clean = line.strip()
                if clean.lower().startswith(("title:", "job title:", "role:", "designation:")):
                    job_title = clean.split(":", 1)[1].strip()
                    break

        # 2. Extract Pillar Scores & Rationales
        pillars_raw = data.get("pillar_scores") or {}
        
        # Firmographic
        f_raw = pillars_raw.get("firmographic_score") or (pillars_raw.get("firmographic") or {}).get("score")
        f_rat = (pillars_raw.get("firmographic") or {}).get("rationale") or pillars_raw.get("firmographic_rationale") or data.get("firmo_insights") or "Evaluated firmographic vertical and company scale."
        f_score = cls.clamp_score(f_raw, 65.0)

        # Technographic
        t_raw = pillars_raw.get("technographic_score") or (pillars_raw.get("technographic") or {}).get("score")
        t_rat = (pillars_raw.get("technographic") or {}).get("rationale") or pillars_raw.get("technographic_rationale") or data.get("techno_insights") or "Evaluated technology stack infrastructure and data maturity."
        t_score = cls.clamp_score(t_raw, 60.0)

        # Intent
        i_raw = pillars_raw.get("intent_score") or (pillars_raw.get("intent") or {}).get("score") or pillars_raw.get("intent_timing_score")
        i_rat = (pillars_raw.get("intent") or {}).get("rationale") or pillars_raw.get("intent_rationale") or data.get("intent_insights") or "Evaluated buyer urgency and project procurement timeline."
        i_score = cls.clamp_score(i_raw, 60.0)

        # Persona
        p_raw = pillars_raw.get("persona_score") or (pillars_raw.get("persona") or {}).get("score") or pillars_raw.get("persona_authority_score")
        p_rat = (pillars_raw.get("persona") or {}).get("rationale") or pillars_raw.get("persona_rationale") or data.get("persona_insights") or f"Evaluated decision-making authority for {contact} ({job_title})."
        p_score = cls.clamp_score(p_raw, 60.0)

        # 3. Disqualification / Negative Scoring Check
        title_lower = job_title.lower()
        has_disqualifying_keyword = any(k in text_lower or k in title_lower for k in cls.DISQUALIFYING_KEYWORDS)
        
        is_disqualified = bool(data.get("is_disqualified")) or has_disqualifying_keyword or (p_score == 0)
        disqualification_reason = data.get("disqualification_reason") or ""
        
        if is_disqualified and not disqualification_reason:
            if has_disqualifying_keyword or "student" in title_lower or "intern" in title_lower:
                disqualification_reason = "Academic / Student Inquiry (No commercial enterprise budget authority)"
                p_score = 0.0
                i_score = min(i_score, 10.0)
                f_score = min(f_score, 15.0)
                t_score = min(t_score, 20.0)
            elif p_score == 0:
                disqualification_reason = "Lead lacks purchasing / budget approval authority"

        # 4. Master ICP Score Calculation (Saber Mathematical Formula)
        if is_disqualified:
            final_icp_score = 12
            saber_tier = "Out of ICP / Disqualified (<40)"
            priority_level = "Disqualified / Deprioritized"
            sales_action = "Route to public open documentation / self-serve whitepapers. Preserve AE and sales bandwidth."
            conversion_prob = 2
        else:
            # Mathematical calculation: 30% Firmo + 25% Techno + 25% Intent + 20% Persona
            final_icp_score = round(
                (f_score * cls.WEIGHT_FIRMOGRAPHIC) +
                (t_score * cls.WEIGHT_TECHNOGRAPHIC) +
                (i_score * cls.WEIGHT_INTENT) +
                (p_score * cls.WEIGHT_PERSONA)
            )
            final_icp_score = max(0, min(100, final_icp_score))

            # Saber Tiers & SLA Cadence Rules
            if final_icp_score >= 80:
                saber_tier = "Tier 1: Dream ICP (80-100)"
                priority_level = "High Priority / Strategic Account"
                sales_action = "Immediate outreach (<2h) by Senior AE & Research Director. Deliver bespoke proposal & schedule technical scoping call."
            elif final_icp_score >= 60:
                saber_tier = "Tier 2: Strong Fit (60-79)"
                priority_level = "Standard Sales Pipeline"
                sales_action = "Standard SDR outbound cadence within 24h. Schedule discovery qualification call and conduct product walkthrough."
            elif final_icp_score >= 40:
                saber_tier = "Tier 3: Moderate Fit (40-59)"
                priority_level = "Inside Sales / Automated Nurture"
                sales_action = "Enroll in automated product nurture drip sequences, invite to bi-weekly webinars, and track corporate expansion milestones."
            else:
                saber_tier = "Out of ICP / Disqualified (<40)"
                priority_level = "Deprioritized / Low Priority"
                sales_action = "Route to marketing newsletter / self-serve knowledge base. Preserve direct sales capacity."

            conversion_prob = min(98, max(5, round(final_icp_score * 0.92)))

        # 5. Strategic 2D Matrices (6sense & MadKudu Best Practice)
        fit_index = round((f_score * 0.55) + (t_score * 0.45))
        intent_index = round((i_score * 0.55) + (p_score * 0.45))

        # 6. Quality-Weighted Pipeline Valuation
        quality_weighted_value = round(deal_size_usd * (final_icp_score / 100.0))

        # 7. Granular Pillar Objects
        pillars = PillarBreakdown(
            firmographic=PillarScore(
                dimension_name="Firmographics Fit",
                weight=cls.WEIGHT_FIRMOGRAPHIC,
                raw_score=f_score,
                points_contributed=round(f_score * cls.WEIGHT_FIRMOGRAPHIC, 1),
                rationale=f_rat
            ),
            technographic=PillarScore(
                dimension_name="Technographics Fit",
                weight=cls.WEIGHT_TECHNOGRAPHIC,
                raw_score=t_score,
                points_contributed=round(t_score * cls.WEIGHT_TECHNOGRAPHIC, 1),
                rationale=t_rat
            ),
            intent=PillarScore(
                dimension_name="Intent & Timing Signals",
                weight=cls.WEIGHT_INTENT,
                raw_score=i_score,
                points_contributed=round(i_score * cls.WEIGHT_INTENT, 1),
                rationale=i_rat
            ),
            persona=PillarScore(
                dimension_name="Persona & Buying Authority",
                weight=cls.WEIGHT_PERSONA,
                raw_score=p_score,
                points_contributed=round(p_score * cls.WEIGHT_PERSONA, 1),
                rationale=p_rat
            )
        )

        # 8. Sales Pitch Strategy & Personalized Copy
        strat_data = data.get("strategy") or {}
        val_wedge = strat_data.get("value_wedge")
        outreach_hook = strat_data.get("outreach_hook")

        if not val_wedge:
            if is_disqualified:
                val_wedge = "Direct non-commercial inquiries to public self-serve resources and knowledge base."
            elif final_icp_score >= 80:
                val_wedge = f"Deliver bespoke intelligence feeds and analyst advisory to de-risk {company}'s strategic CapEx investments."
            else:
                val_wedge = f"Equip {company}'s team with actionable market benchmarking to accelerate pipeline efficiency."

        if not outreach_hook:
            first_name = contact.split()[0] if contact else "there"
            if is_disqualified:
                outreach_hook = f"Hi {first_name}, for coursework and research please access our open whitepapers library."
            elif final_icp_score >= 80:
                outreach_hook = f"Hi {first_name}, saw {company}'s strategic expansion in the market and wanted to share our latest intelligence benchmark relevant to your project roadmap."
            else:
                outreach_hook = f"Hi {first_name}, noticed your focus on benchmarking growth at {company} and thought our data feeds would be timely for your team."

        strategy = StrategyRecommendation(
            value_wedge=val_wedge,
            outreach_hook=outreach_hook
        )

        # 9. CRM Sync Payload (Salesforce / HubSpot schema)
        crm_payload = {
            "ICP_Score_Total__c": final_icp_score,
            "ICP_Fit_Tier__c": saber_tier,
            "ICP_Priority_Level__c": priority_level,
            "ICP_Firmographic_Score__c": int(f_score),
            "ICP_Technographic_Score__c": int(t_score),
            "ICP_Intent_Score__c": int(i_score),
            "ICP_Persona_Score__c": int(p_score),
            "ICP_Account_Fit_Index__c": fit_index,
            "ICP_Intent_Surge_Index__c": intent_index,
            "ICP_Win_Probability__c": conversion_prob,
            "ICP_Weighted_Pipeline_USD__c": quality_weighted_value,
            "ICP_Disqualified__c": is_disqualified,
            "ICP_Disqualification_Reason__c": disqualification_reason,
            "SLA_Cadence_Action__c": sales_action,
            "Strategy_Value_Wedge__c": val_wedge,
            "Strategy_Outreach_Hook__c": outreach_hook
        }

        return ICPScoreResult(
            company_name=company,
            contact_name=contact,
            job_title=job_title,
            industry=industry,
            final_icp_score=final_icp_score,
            saber_tier=saber_tier,
            priority_level=priority_level,
            sales_action=sales_action,
            fit_index=fit_index,
            intent_index=intent_index,
            conversion_probability=conversion_prob,
            estimated_deal_size=deal_size_usd,
            quality_weighted_value=quality_weighted_value,
            is_disqualified=is_disqualified,
            disqualification_reason=disqualification_reason,
            pillars=pillars,
            strategy=strategy,
            crm_payload=crm_payload
        )


def evaluate_prospect(
    raw_ai_data: Optional[Dict[str, Any]] = None,
    raw_text: str = "",
    deal_size_usd: float = 50000.0
) -> ICPScoreResult:
    """Convenience functional wrapper around ICPScoringEngine.evaluate."""
    return ICPScoringEngine.evaluate(raw_ai_data, raw_text, deal_size_usd)
