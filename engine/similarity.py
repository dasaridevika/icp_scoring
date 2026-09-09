"""
Enterprise ICP Intelligence Engine - Dynamic Similarity & Lookalike Engine.
100% Dynamic - Eliminates static hardcoded customer lists.
Performs vector and multi-attribute similarity against dynamic customer cohorts.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from .models import SimilarCustomerMatch


class GoldenCustomerClassifier:
    """
    Classifies customer accounts into Tiers (Golden A, B, C, D) based on
    LTV, Gross Retention, Net Revenue Retention (NRR), and Support Burden.
    """

    @classmethod
    def classify(
        cls,
        arr_usd: float,
        retention_rate: float,
        nrr: float,
        support_cost_ratio: float,
        sales_cycle_days: int
    ) -> Tuple[str, float]:
        score = 0.0

        if retention_rate >= 0.95 and nrr >= 1.20:
            score += 40.0
        elif retention_rate >= 0.85 and nrr >= 1.0:
            score += 28.0
        elif retention_rate >= 0.75:
            score += 15.0
        else:
            score += 5.0

        if arr_usd >= 200000:
            score += 30.0
        elif arr_usd >= 100000:
            score += 22.0
        elif arr_usd >= 50000:
            score += 15.0
        else:
            score += 5.0

        if support_cost_ratio <= 0.05:
            score += 15.0
        elif support_cost_ratio <= 0.10:
            score += 10.0
        elif support_cost_ratio <= 0.20:
            score += 5.0

        if sales_cycle_days <= 45:
            score += 15.0
        elif sales_cycle_days <= 75:
            score += 10.0
        elif sales_cycle_days <= 100:
            score += 5.0

        if score >= 85:
            tier = "Tier A / Golden Customer"
        elif score >= 65:
            tier = "Tier B / Healthy Account"
        elif score >= 45:
            tier = "Tier C / Low Expansion"
        else:
            tier = "Tier D / High Churn Risk"

        return tier, round(score, 1)


class HistoricalSimilarityEngine:
    """
    Dynamically computes multi-attribute similarity against reference customer cohorts.
    Evaluates industry overlap, scale distance, and technographic similarity.
    """

    @classmethod
    def calculate_similarity(
        cls,
        industry: str = "",
        employee_count: Optional[int] = None,
        tech_stack_text: str = "",
        problem_use_case: str = "",
        reference_customers: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[float, List[SimilarCustomerMatch], List[str]]:
        pool = reference_customers or []
        if not pool:
            return 50.0, [], []

        matches: List[Tuple[float, Dict[str, Any], List[str]]] = []
        parsed_tech = [t.strip().lower() for t in tech_stack_text.replace(",", " ").split() if len(t.strip()) > 2]
        target_ind = industry.lower().strip()
        target_problem = problem_use_case.lower().strip()

        for cust in pool:
            sim_points = 0.0
            shared: List[str] = []

            # 1. Industry Affinity
            cust_ind = str(cust.get("industry", "")).lower()
            if target_ind and (target_ind in cust_ind or cust_ind in target_ind or any(k in cust_ind for k in target_ind.split())):
                sim_points += 35.0
                shared.append(f"Industry vertical match ({cust.get('industry')})")
            else:
                sim_points += 15.0

            # 2. Scale Distance
            cust_emp = int(cust.get("employee_count", 0))
            if employee_count and employee_count > 0 and cust_emp > 0:
                log_ratio = abs(math.log10(employee_count) - math.log10(cust_emp))
                scale_score = max(0.0, 1.0 - (log_ratio / 1.5)) * 25.0
                sim_points += scale_score
                if scale_score >= 18.0:
                    shared.append(f"Scale peer ({cust_emp:,} headcount)")
            else:
                sim_points += 12.5

            # 3. Technographic Stack Overlap
            cust_stack = [str(t).lower() for t in cust.get("tech_stack", [])]
            if parsed_tech and cust_stack:
                overlap = set(parsed_tech).intersection(set(cust_stack))
                if overlap:
                    jaccard = len(overlap) / len(set(parsed_tech).union(set(cust_stack)))
                    tech_score = min(25.0, (len(overlap) * 8.0) + (jaccard * 15.0))
                    sim_points += tech_score
                    shared.append(f"Shared technology ({', '.join(sorted(overlap))})")
                else:
                    sim_points += 8.0
            else:
                sim_points += 12.5

            # 4. Use Case Domain
            cust_use = str(cust.get("use_case", "")).lower()
            if target_problem and any(word in cust_use for word in target_problem.split() if len(word) > 3):
                sim_points += 15.0
                shared.append(f"Use case: {cust.get('use_case')}")
            else:
                sim_points += 8.0

            final_sim = min(100.0, max(0.0, round(sim_points, 1)))
            matches.append((final_sim, cust, shared))

        matches.sort(key=lambda x: x[0], reverse=True)

        top_matches: List[SimilarCustomerMatch] = []
        all_shared_traits: List[str] = []

        for sim_val, cust_data, shared_traits in matches[:3]:
            top_matches.append(
                SimilarCustomerMatch(
                    customer_id=str(cust_data.get("customer_id", "CUST-REF")),
                    company_name=str(cust_data.get("company_name", "Reference Customer")),
                    industry=str(cust_data.get("industry", "")),
                    arr_usd=float(cust_data.get("arr_usd", 0.0)),
                    retention_rate=float(cust_data.get("retention_rate", 0.90)),
                    similarity_score=sim_val,
                    shared_characteristics=shared_traits
                )
            )
            for trait in shared_traits:
                if trait not in all_shared_traits:
                    all_shared_traits.append(trait)

        overall_sim_score = matches[0][0] if matches else 50.0
        return overall_sim_score, top_matches, all_shared_traits
