"""
Enterprise ICP Intelligence Engine - Eligibility & Disqualification Layer.
Implements hard eligibility gates (Anti-ICP rules) before continuous scoring.
"""

from typing import Dict, Any, List, Optional
from .models import EligibilityResult, DataStatus, EvidenceField
from .config import EngineConfiguration, active_config


class DisqualificationEngine:
    """
    Evaluates hard constraints. If an account is disqualified, it fails eligibility
    with concrete reasons rather than just losing a few arbitrary points.
    """

    @classmethod
    def evaluate(
        cls,
        email_or_domain: str = "",
        industry: str = "",
        country_or_region: str = "",
        employee_count: Optional[int] = None,
        annual_revenue: Optional[float] = None,
        config: Optional[EngineConfiguration] = None
    ) -> EligibilityResult:
        cfg = config or active_config
        rules = cfg.disqualification
        reasons: List[str] = []

        clean_domain = email_or_domain.lower().strip()
        if "@" in clean_domain:
            clean_domain = clean_domain.split("@")[-1]

        # 1. Blocked / Freemail Domains
        for blocked_dom in rules.blocked_email_domains:
            if clean_domain == blocked_dom.lower() or clean_domain.endswith("." + blocked_dom.lower()):
                reasons.append(
                    f"Non-commercial / Personal email domain detected (@{clean_domain}). Enterprise qualification requires corporate business email domain."
                )
                break

        # 2. Blocked Industries
        clean_ind = industry.lower().strip()
        for blocked_ind in rules.blocked_industries:
            if blocked_ind.lower() in clean_ind:
                reasons.append(
                    f"Unsupported industry vertical: '{industry}'. Excluded by GTM compliance and product eligibility policy."
                )
                break

        # 3. Unsupported / Sanctioned Geographies
        clean_geo = country_or_region.lower().strip()
        for unsupp_geo in rules.unsupported_countries:
            if unsupp_geo.lower() in clean_geo:
                reasons.append(
                    f"Operating jurisdiction '{country_or_region}' is in an unsupported/restricted regulatory geography."
                )
                break

        # 4. Hard Sub-Scale Economic Disqualifier (if verified)
        if employee_count is not None and employee_count > 0:
            if employee_count < rules.min_employee_count:
                reasons.append(
                    f"Verified headcount ({employee_count}) is below minimum enterprise viability threshold ({rules.min_employee_count} employees)."
                )

        if annual_revenue is not None and annual_revenue > 0:
            if annual_revenue < rules.min_annual_revenue_usd:
                reasons.append(
                    f"Verified annual revenue (${annual_revenue:,.0f}) is below commercial contract viability threshold (${rules.min_annual_revenue_usd:,.0f})."
                )

        is_eligible = len(reasons) == 0
        return EligibilityResult(
            eligible=is_eligible,
            disqualification_reasons=reasons
        )
