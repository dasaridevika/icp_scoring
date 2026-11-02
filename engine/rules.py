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

# Authoritative prohibited / sanctioned territories, aliases, and demonyms
DEFAULT_PROHIBITED_COUNTRIES: List[str] = [
    # Russia & Belarus
    "Russia",
    "Russian",
    "Russian Federation",
    "Belarus",
    "Belarusian",
    "Belorussia",
    "Bielorussia",
    # North Korea
    "North Korea",
    "North Korean",
    "DPRK",
    "D.P.R.K.",
    "Democratic People's Republic of Korea",
    # Syria
    "Syria",
    "Syrian",
    "Syrian Arab Republic",
    # Iran
    "Iran",
    "Iranian",
    "Islamic Republic of Iran",
    # Cuba
    "Cuba",
    "Cuban"
]

# Major sanctioned administrative capitals, cities, or disputed regions
SANCTIONED_CITIES_OR_REGIONS: List[str] = [
    "Tehran",
    "Moscow",
    "Saint Petersburg",
    "St. Petersburg",
    "St Petersburg",
    "Minsk",
    "Damascus",
    "Pyongyang",
    "Havana",
    "Crimea",
    "Sevastopol",
    "Donetsk",
    "Luhansk"
]

# Exemption keywords: Leadership or administrative staff in student-facing departments
# (e.g., 'Director of Student Affairs', 'Dean of Students', 'Student Affairs Coordinator')
# are real enterprise buyers and university staff, not students.
STAFF_LEADERSHIP_EXEMPTIONS: List[str] = [
    "director",
    "dean",
    "head",
    "vp",
    "vice president",
    "chief",
    "president",
    "manager",
    "administrator",
    "coordinator",
    "officer"
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
        prohibited_set = set(DEFAULT_PROHIBITED_COUNTRIES)
        if prohibited_countries:
            prohibited_set.update(prohibited_countries)
        all_prohibited_terms = list(prohibited_set) + SANCTIONED_CITIES_OR_REGIONS

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
                # Exemption: Leadership and staff in student affairs/services are real buyers, not students
                if disq_role == "student" and any(matches_whole_word(exempt, role_title or "") for exempt in STAFF_LEADERSHIP_EXEMPTIONS):
                    continue
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
