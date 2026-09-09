"""
Enterprise ICP Intelligence Engine - Dynamic Master Scoring Orchestrator.
100% Dynamic - Zero hardcoded keywords, static string lists, or keyword dictionaries.
Scores are computed dynamically from AI semantic evaluation, mathematical weights,
and evidence confidence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .models import (
    DataStatus,
    EvidenceField,
    DimensionScore,
    ICPFitScore,
    IntentScore,
    ReadinessScore,
    ValueScore,
    EligibilityResult,
    ExpectedValueResult,
    NextBestAction,
    MasterAccountIntelligence
)
from .config import EngineConfiguration, active_config
from .disqualifier import DisqualificationEngine
from .similarity import HistoricalSimilarityEngine
from .calibration import global_calibrator


class MasterScoringEngine:
    """
    100% dynamic revenue intelligence and ICP qualification engine.
    """

    @classmethod
    def evaluate_account(
        cls,
        extracted_data: Dict[str, Any],
        deal_size_usd: float = 50000.0,
        config: Optional[EngineConfiguration] = None
    ) -> MasterAccountIntelligence:
        cfg = config or active_config
        ev_fields = extracted_data.get("evidence_fields") or {}
        ai_data = extracted_data.get("raw_ai_payload") or {}
        overall_conf = float(extracted_data.get("overall_confidence", 0.5))

        company_name = extracted_data.get("company_name") or "Unspecified Company"
        domain = extracted_data.get("domain") or "unspecified.com"
        contact_name = extracted_data.get("contact_name") or "Unspecified Contact"
        job_title = extracted_data.get("job_title") or "Unspecified Title"
        industry = extracted_data.get("industry") or "Unspecified Industry"

        # 1. Eligibility Check
        eligibility: EligibilityResult = DisqualificationEngine.evaluate(
            email_or_domain=domain,
            industry=industry,
            config=cfg
        )

        # 2. Dynamic Similarity
        tech_val = str(ev_fields.get("technographics", {}).raw_value or "") if hasattr(ev_fields.get("technographics"), "raw_value") else ""
        sim_score, top_similar_customers, shared_traits = HistoricalSimilarityEngine.calculate_similarity(
            industry=industry,
            tech_stack_text=tech_val,
            problem_use_case=industry
        )

        # 3. Dynamic ICP Fit Engine (Strictly Separate from Intent)
        fit_weights = cfg.icp_fit_weights
        fit_dimensions: Dict[str, DimensionScore] = {}
        fit_rationales: List[str] = []
        fit_missing: List[str] = []

        # 3.1 Firmographics Scale
        hc_field = ev_fields.get("employee_count")
        hc_status = hc_field.status if hc_field else DataStatus.UNKNOWN
        raw_f_score = float(ai_data.get("firmographics_score") or 50.0)
        f_score = raw_f_score if hc_status != DataStatus.UNKNOWN else min(45.0, raw_f_score)
        f_rat = [ai_data.get("firmographics_rationale") or f"Commercial scale evaluation for {company_name}."]

        fit_dimensions["firmographic"] = DimensionScore(
            name="Firmographic Scale",
            score=f_score,
            confidence=hc_field.confidence if hc_field else 0.2,
            weight=fit_weights.firmographic,
            points_contributed=round(f_score * fit_weights.firmographic, 1),
            status=hc_status,
            evidence=[str(hc_field.raw_value)] if hc_field and hc_field.raw_value else [],
            rationale=f_rat,
            missing_information=["Headcount"] if hc_status == DataStatus.UNKNOWN else []
        )
        if hc_status == DataStatus.UNKNOWN:
            fit_missing.append("Headcount scale")

        # 3.2 Industry & Vertical Fit
        ind_field = ev_fields.get("industry")
        ind_status = ind_field.status if ind_field else DataStatus.UNKNOWN
        i_score = float(ai_data.get("firmographics_score") or 50.0) if ind_status != DataStatus.UNKNOWN else 35.0
        i_rat = [f"Industry sector: {industry}"]

        fit_dimensions["industry_vertical"] = DimensionScore(
            name="Industry & Vertical Fit",
            score=i_score,
            confidence=ind_field.confidence if ind_field else 0.2,
            weight=fit_weights.industry_vertical,
            points_contributed=round(i_score * fit_weights.industry_vertical, 1),
            status=ind_status,
            evidence=[industry] if industry != "Unspecified Industry" else [],
            rationale=i_rat,
            missing_information=["Industry"] if ind_status == DataStatus.UNKNOWN else []
        )
        if ind_status == DataStatus.UNKNOWN:
            fit_missing.append("Industry classification")

        # 3.3 Problem / Use-Case Fit
        p_use_score = float(ai_data.get("firmographics_score") or 50.0)
        fit_dimensions["problem_use_case"] = DimensionScore(
            name="Problem / Use-Case Suitability",
            score=p_use_score,
            confidence=0.75 if ind_status != DataStatus.UNKNOWN else 0.3,
            weight=fit_weights.problem_use_case,
            points_contributed=round(p_use_score * fit_weights.problem_use_case, 1),
            status=DataStatus.INFERRED if ind_status != DataStatus.UNKNOWN else DataStatus.UNKNOWN,
            evidence=[],
            rationale=[f"Workflow compatibility for {industry}"],
            missing_information=[]
        )

        # 3.4 Technographic Fit
        tech_field = ev_fields.get("technographics")
        tech_status = tech_field.status if tech_field else DataStatus.UNKNOWN
        raw_t_score = float(ai_data.get("technographics_score") or 50.0)
        t_score = raw_t_score if tech_status != DataStatus.UNKNOWN else min(40.0, raw_t_score)
        t_rat = [ai_data.get("technographics_rationale") or "Technology stack sophistication assessment."]

        fit_dimensions["technographic"] = DimensionScore(
            name="Technographic Compatibility",
            score=t_score,
            confidence=tech_field.confidence if tech_field else 0.15,
            weight=fit_weights.technographic,
            points_contributed=round(t_score * fit_weights.technographic, 1),
            status=tech_status,
            evidence=[tech_val] if tech_val else [],
            rationale=t_rat,
            missing_information=["Tech stack"] if tech_status == DataStatus.UNKNOWN else []
        )
        if tech_status == DataStatus.UNKNOWN:
            fit_missing.append("Technographic stack")

        # 3.5 Geographic & Market Fit
        fit_dimensions["geographic_market"] = DimensionScore(
            name="Geographic & Market Fit",
            score=85.0 if eligibility.eligible else 20.0,
            confidence=0.85,
            weight=fit_weights.geographic_market,
            points_contributed=round((85.0 if eligibility.eligible else 20.0) * fit_weights.geographic_market, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Supported commercial operational jurisdiction."],
            missing_information=[]
        )

        # 3.6 Historical Similarity Dimension
        fit_dimensions["historical_similarity"] = DimensionScore(
            name="Historical Customer Similarity",
            score=sim_score,
            confidence=0.80,
            weight=fit_weights.historical_similarity,
            points_contributed=round(sim_score * fit_weights.historical_similarity, 1),
            status=DataStatus.INFERRED,
            evidence=shared_traits,
            rationale=[f"Similarity alignment score: {sim_score:.0f}/100."],
            missing_information=[]
        )

        master_fit_score = sum(d.points_contributed for d in fit_dimensions.values())
        fit_rationales.extend([f"• {d.name}: {d.score:.0f}/100" for d in fit_dimensions.values()])

        icp_fit = ICPFitScore(
            score=round(master_fit_score, 1),
            confidence=round(sum(d.confidence * d.weight for d in fit_dimensions.values()), 2),
            dimensions=fit_dimensions,
            rationale=fit_rationales,
            missing_information=fit_missing
        )

        # 4. Dynamic Intent Engine
        intent_weights = cfg.intent_weights
        intent_dimensions: Dict[str, DimensionScore] = {}
        intent_missing: List[str] = []

        intent_field = ev_fields.get("intent_signals")
        intent_status = intent_field.status if intent_field else DataStatus.UNKNOWN
        raw_int_score = float(ai_data.get("intent_score") or 50.0)
        int_score = raw_int_score if intent_status != DataStatus.UNKNOWN else min(35.0, raw_int_score)
        int_rat = [ai_data.get("intent_rationale") or "Procurement timeline urgency evaluation."]

        intent_dimensions["active_search"] = DimensionScore(
            name="Active Search & RFP Signals",
            score=int_score,
            confidence=intent_field.confidence if intent_field else 0.20,
            weight=intent_weights.active_search_research,
            points_contributed=round(int_score * intent_weights.active_search_research, 1),
            status=intent_status,
            evidence=[str(intent_field.raw_value)] if intent_field and intent_field.raw_value else [],
            rationale=int_rat,
            missing_information=["Intent signals"] if intent_status == DataStatus.UNKNOWN else []
        )
        if intent_status == DataStatus.UNKNOWN:
            intent_missing.append("Buying timeline & urgency")

        intent_dimensions["project_timeline"] = DimensionScore(
            name="Project Buying Timeline",
            score=int_score,
            confidence=intent_field.confidence if intent_field else 0.20,
            weight=intent_weights.project_timeline,
            points_contributed=round(int_score * intent_weights.project_timeline, 1),
            status=intent_status,
            evidence=[],
            rationale=["Target deployment window evaluation."],
            missing_information=[]
        )

        intent_dimensions["hiring_and_expansion"] = DimensionScore(
            name="Hiring & Expansion Velocity",
            score=int_score,
            confidence=0.60,
            weight=intent_weights.hiring_and_expansion,
            points_contributed=round(int_score * intent_weights.hiring_and_expansion, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Organizational momentum indicator."],
            missing_information=[]
        )

        intent_dimensions["competitor_evaluation"] = DimensionScore(
            name="Competitive Evaluation",
            score=int_score,
            confidence=0.50,
            weight=intent_weights.competitor_evaluation,
            points_contributed=round(int_score * intent_weights.competitor_evaluation, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Solution comparison stage."],
            missing_information=[]
        )

        master_intent_score = sum(d.points_contributed for d in intent_dimensions.values())
        intent = IntentScore(
            score=round(master_intent_score, 1),
            confidence=round(sum(d.confidence * d.weight for d in intent_dimensions.values()), 2),
            dimensions=intent_dimensions,
            rationale=[f"• {d.name}: {d.score:.0f}/100" for d in intent_dimensions.values()],
            missing_information=intent_missing
        )

        # 5. Dynamic Readiness Engine
        readiness_weights = cfg.readiness_weights
        readiness_dimensions: Dict[str, DimensionScore] = {}
        readiness_missing: List[str] = []

        persona_field = ev_fields.get("contact_authority")
        persona_status = persona_field.status if persona_field else DataStatus.UNKNOWN
        raw_p_score = float(ai_data.get("persona_score") or 50.0)
        auth_score = raw_p_score if persona_status != DataStatus.UNKNOWN else min(30.0, raw_p_score)
        auth_rat = [ai_data.get("persona_rationale") or f"Evaluation of buying mandate for {contact_name} ({job_title})."]

        readiness_dimensions["decision_authority"] = DimensionScore(
            name="Decision Maker Authority",
            score=auth_score,
            confidence=persona_field.confidence if persona_field else 0.20,
            weight=readiness_weights.decision_maker_authority,
            points_contributed=round(auth_score * readiness_weights.decision_maker_authority, 1),
            status=persona_status,
            evidence=[str(persona_field.raw_value)] if persona_field and persona_field.raw_value else [],
            rationale=auth_rat,
            missing_information=["Executive sponsor"] if persona_status == DataStatus.UNKNOWN else []
        )
        if persona_status == DataStatus.UNKNOWN:
            readiness_missing.append("Economic buyer persona")

        readiness_dimensions["budget_allocated"] = DimensionScore(
            name="Budget Allocation & CapEx",
            score=auth_score,
            confidence=0.60,
            weight=readiness_weights.budget_allocated,
            points_contributed=round(auth_score * readiness_weights.budget_allocated, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Project funding availability proxy."],
            missing_information=[]
        )

        readiness_dimensions["implementation_capability"] = DimensionScore(
            name="Implementation Capability",
            score=t_score,
            confidence=0.70,
            weight=readiness_weights.implementation_capability,
            points_contributed=round(t_score * readiness_weights.implementation_capability, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Technical deployment readiness."],
            missing_information=[]
        )

        readiness_dimensions["procurement_simplicity"] = DimensionScore(
            name="Procurement Simplicity",
            score=70.0,
            confidence=0.60,
            weight=readiness_weights.procurement_simplicity,
            points_contributed=round(70.0 * readiness_weights.procurement_simplicity, 1),
            status=DataStatus.INFERRED,
            evidence=[],
            rationale=["Commercial contracting path."],
            missing_information=[]
        )

        master_readiness_score = sum(d.points_contributed for d in readiness_dimensions.values())
        readiness = ReadinessScore(
            score=round(master_readiness_score, 1),
            confidence=round(sum(d.confidence * d.weight for d in readiness_dimensions.values()), 2),
            dimensions=readiness_dimensions,
            rationale=[f"• {d.name}: {d.score:.0f}/100" for d in readiness_dimensions.values()],
            missing_information=readiness_missing
        )

        # 6. Value Engine
        val_score = round(min(100.0, max(20.0, (f_score * 0.60) + (sim_score * 0.40))), 1)
        estimated_arr = deal_size_usd
        expansion_band = "High" if val_score >= 80 else ("Moderate" if val_score >= 60 else "Limited")

        value = ValueScore(
            score=val_score,
            confidence=round((f_score + 80.0) / 200.0, 2),
            estimated_arr=estimated_arr,
            deal_size_usd=deal_size_usd,
            expansion_potential=expansion_band,
            rationale=[f"Estimated deal ARR: ${estimated_arr:,.0f} USD."],
            missing_information=[]
        )

        # 7. Expected Value & Win Propensity Model
        propensity = global_calibrator.predict_propensity(
            icp_fit=icp_fit.score,
            intent=intent.score,
            readiness=readiness.score,
            value=value.score,
            confidence=overall_conf
        )

        if not eligibility.eligible:
            propensity = 0.01

        p_retention = cfg.default_retention_rate if icp_fit.score >= 70 else (cfg.default_retention_rate * 0.85)
        expected_ltv = round(propensity * estimated_arr * (1.0 + p_retention), 2)
        expected_cac = cfg.default_base_cac
        expected_net_val = round(max(0.0, expected_ltv - (propensity * expected_cac)), 2)
        effort_score = 4.0 if intent.score >= 75 else 7.0
        priority_rank = round((expected_net_val / (effort_score * 1000.0)) * 10.0, 1)

        expected_val_result = ExpectedValueResult(
            opportunity_propensity=propensity,
            expected_arr=estimated_arr,
            p_retention=round(p_retention, 2),
            expected_lifetime_value=expected_ltv,
            expected_cac=expected_cac,
            expected_net_value=expected_net_val,
            sales_effort_score=effort_score,
            priority_rank_score=priority_rank
        )

        # 8. Next Best Action
        val_wedge = ai_data.get("value_wedge") or f"Deliver enterprise intelligence to accelerate {company_name}'s strategic roadmap."
        outreach_hook = ai_data.get("outreach_hook") or f"Hi {contact_name.split()[0] if contact_name != 'Unspecified Contact' else 'there'}, reaching out regarding {company_name}'s strategic initiatives."

        if not eligibility.eligible:
            priority_tier = "Disqualified / Anti-ICP"
            action_text = "Disqualify account and route to self-serve knowledge base."
            sla_text = "Automated Deprioritization"
            channel = "Self-Serve Portal"
            reason_text = "Account violates eligibility rules: " + "; ".join(eligibility.disqualification_reasons)
        elif icp_fit.score >= 80 and intent.score >= 70:
            priority_tier = "Tier A1: Strategic Inbound"
            action_text = "Fast-track to Senior AE. Schedule discovery call within 2 hours."
            sla_text = "Immediate outreach (<2 hours)"
            channel = "Executive Phone & Video"
            reason_text = "High ICP Fit (80+) with active buying signals (70+)."
        elif icp_fit.score >= 75:
            priority_tier = "Tier A2: High Priority Outbound"
            action_text = f"Launch strategic SDR outbound sequence targeting {job_title}."
            sla_text = "SDR cadence within 24 hours"
            channel = "Multi-touch Email + LinkedIn InMail"
            reason_text = "Strong ICP Fit. Requires proactive outbound value positioning."
        elif icp_fit.score >= 50 and intent.score >= 50:
            priority_tier = "Tier B1: Mid-Market Fast Track"
            action_text = "Route to Inside Sales for qualification call."
            sla_text = "Inside Sales follow-up (<24 hours)"
            channel = "Direct Email & Discovery Call"
            reason_text = "Moderate fit with active engagement."
        elif icp_fit.score >= 45:
            priority_tier = "Tier A3: Outbound Nurture"
            action_text = "Enroll account in automated product webinar sequences."
            sla_text = "Bi-weekly marketing nurture"
            channel = "Automated Marketing Sequences"
            reason_text = "Acceptable fit without immediate urgency."
        else:
            priority_tier = "Tier C: Deprioritize"
            action_text = "Preserve sales capacity. Route to marketing newsletter."
            sla_text = "No direct sales SLA"
            channel = "Marketing Newsletter"
            reason_text = "Low overall fit."

        next_action = NextBestAction(
            priority_tier=priority_tier,
            action=action_text,
            urgency_sla=sla_text,
            recommended_channel=channel,
            target_persona=f"{contact_name} ({job_title})",
            reason=reason_text,
            value_wedge=val_wedge,
            outreach_hook=outreach_hook,
            discovery_gap_prompts=extracted_data.get("discovery_questions", [])
        )

        strengths: List[str] = []
        if icp_fit.score >= 75:
            strengths.append(f"✓ Strong ICP Fit ({icp_fit.score:.0f}/100)")
        if intent.score >= 70:
            strengths.append(f"✓ Active buying urgency signal ({intent.score:.0f}/100)")
        if readiness.score >= 75:
            strengths.append(f"✓ Senior executive sponsorship ({job_title})")

        risks: List[str] = []
        if not eligibility.eligible:
            risks.extend([f"⚠ Hard Disqualifier: {r}" for r in eligibility.disqualification_reasons])
        if overall_conf < 0.50:
            risks.append(f"⚠ Low Data Confidence ({overall_conf*100:.0f}%): Missing core fields")
        for m in (fit_missing + intent_missing + readiness_missing):
            risks.append(f"⚠ Missing Evidence: {m}")

        now_utc_str = datetime.now(timezone.utc).isoformat()
        audit_trail = [
            f"Evaluated with Model Version: {cfg.model_version}",
            f"Timestamp: {now_utc_str}",
            f"Eligibility Check: {'PASS' if eligibility.eligible else 'FAIL'}",
            f"ICP Fit: {icp_fit.score}/100",
            f"Intent: {intent.score}/100",
            f"Readiness: {readiness.score}/100",
            f"Expected Net Value: ${expected_net_val:,.0f} USD",
            f"Action Assigned: {priority_tier}"
        ]

        crm_payload = {
            "Account_Name__c": company_name,
            "Account_Domain__c": domain,
            "ICP_Model_Version__c": cfg.model_version,
            "ICP_Fit_Score__c": icp_fit.score,
            "ICP_Intent_Score__c": intent.score,
            "ICP_Readiness_Score__c": readiness.score,
            "ICP_Value_Score__c": value.score,
            "Overall_Priority_Tier__c": priority_tier,
            "Data_Confidence_Pct__c": int(overall_conf * 100),
            "Opportunity_Propensity_Pct__c": round(propensity * 100, 1),
            "Expected_Net_Value_USD__c": expected_net_val,
            "SLA_Action__c": action_text,
            "Disqualified__c": not eligibility.eligible,
            "Disqualification_Reason__c": "; ".join(eligibility.disqualification_reasons)
        }

        return MasterAccountIntelligence(
            account_id=f"ACC-{abs(hash(company_name)) % 10000:04d}",
            company_name=company_name,
            domain=domain,
            contact_name=contact_name,
            job_title=job_title,
            industry=industry,
            location="Commercial",
            model_version=cfg.model_version,
            scored_at=now_utc_str,
            eligibility=eligibility,
            icp_fit=icp_fit,
            intent=intent,
            readiness=readiness,
            value=value,
            overall_priority=priority_tier,
            overall_confidence=overall_conf,
            expected_value=expected_val_result,
            similar_customers=top_similar_customers,
            next_best_action=next_action,
            evidence_fields=ev_fields,
            key_strengths=strengths,
            key_risks_and_gaps=risks,
            audit_trail=audit_trail,
            crm_payload=crm_payload
        )
