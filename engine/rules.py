"""
Deterministic Policy & Compliance Layer.
Short-circuits scoring before calling any LLM if hard constraints or sanctions are triggered.
"""

import re
from typing import List, Optional, Tuple

try:
    from pydantic import BaseModel, Field
except (ImportError, ModuleNotFoundError):
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
        def model_dump(self):
            return self.__dict__
    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory()
        return default


# Non-commercial personas that are hard-disqualified from B2B enterprise outreach
DISQUALIFYING_ROLES: List[str] = [
    "student",
    "intern",
    "summer intern",
    "graduate student",
    "phd candidate",
    "trainee",
    "graduate trainee",
    "apprentice",
    "fresher",
    "unemployed",
    "job seeker",
    "hobbyist",
    "academic research only",
    "academic researcher"
]

# Authoritative prohibited / sanctioned territories
DEFAULT_PROHIBITED_COUNTRIES: List[str] = [
    "North Korea",
    "Iran",
    "Syria",
    "Cuba",
    "Russia",
    "Belarus"
]

# Major sanctioned administrative capitals, cities, or disputed regions
SANCTIONED_CITIES_OR_REGIONS: List[str] = [
    "Tehran",
    "Moscow",
    "Minsk",
    "Damascus",
    "Pyongyang",
    "Havana",
    "Crimea",
    "Sevastopol",
    "Donetsk",
    "Luhansk"
]


def matches_whole_word(phrase: str, text: str) -> bool:
    """
    Checks if `phrase` matches in `text` with whole-word boundaries at start and end.
    Avoids false positives like 'intern' in 'International Sales Director'
    or 'iran' in 'Miranda, Chile'.
    """
    if not phrase or not text:
        return False
    pattern = r"\b" + re.escape(phrase.strip()) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


class PolicyCheckResult(BaseModel):
    is_disqualified: bool = False
    disqualification_reason: str = ""
    matched_rule: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class PolicyEngine:
    """
    Evaluates hard deterministic compliance rules before external AI calls.
    """

    @classmethod
    def evaluate_compliance(
        cls,
        location: str,
        role_title: str,
        branch_locations: Optional[List[str]] = None,
        prohibited_countries: Optional[List[str]] = None,
        min_deal_size_usd: float = 0.0,
        target_deal_size_usd: float = 0.0
    ) -> PolicyCheckResult:
        result = PolicyCheckResult()

        # 1. Sanctions / Prohibited Territories & Sanctioned Cities Check
        prohibited = prohibited_countries or DEFAULT_PROHIBITED_COUNTRIES
        all_prohibited_terms = list(prohibited) + SANCTIONED_CITIES_OR_REGIONS

        # Check primary location and all branch locations
        locations_to_check = [location or ""]
        if branch_locations:
            locations_to_check.extend([b for b in branch_locations if b])

        for loc in locations_to_check:
            for term in all_prohibited_terms:
                if term and matches_whole_word(term, loc):
                    result.is_disqualified = True
                    result.matched_rule = "SANCTIONED_TERRITORY"
                    result.disqualification_reason = (
                        f"Prohibited / Sanctioned territory detected: '{term}' "
                        f"in '{loc}' is blocked by corporate compliance policy."
                    )
                    return result

        # 2. Anti-ICP Persona / Disqualifier Roles Check (Whole-word matching)
        for disq_role in DISQUALIFYING_ROLES:
            if matches_whole_word(disq_role, role_title or ""):
                result.is_disqualified = True
                result.matched_rule = "ANTI_ICP_ROLE"
                result.disqualification_reason = (
                    f"Non-commercial persona detected: '{role_title}' "
                    f"does not have enterprise buying authority."
                )
                return result

        # 3. Commercial Margin Check (Warning)
        if min_deal_size_usd > 0 and target_deal_size_usd > 0 and target_deal_size_usd < min_deal_size_usd:
            result.warnings.append(
                f"Deal size (${target_deal_size_usd:,.0f} USD) is below organizational minimum viable deal floor (${min_deal_size_usd:,.0f} USD)."
            )

        return result
