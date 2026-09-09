"""
Enterprise ICP Intelligence Engine - Model Evaluation & Dynamic Discovery.
100% Dynamic - Computes decile win rates, tier conversion lift,
and dynamic pattern mining directly from supplied dataset.
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict


class HistoricalModelEvaluator:
    """
    Evaluates scoring accuracy against historical closed-won / closed-lost opportunities.
    Computes conversion rate by tier, win rates by decile, revenue lift, and Precision@Top-K.
    """

    @classmethod
    def evaluate_cohort(cls, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not dataset:
            return {
                "total_accounts_evaluated": 0,
                "overall_baseline_win_rate": 0.0,
                "precision_top_20_pct": 0.0,
                "top_20_lift": 1.0,
                "tier_summary": {},
                "deciles": []
            }

        total_accounts = len(dataset)
        total_won = sum(1 for d in dataset if d.get("won"))
        overall_win_rate = (total_won / total_accounts) * 100.0 if total_accounts > 0 else 0.0

        # Tier Breakdown
        tier_stats: Dict[str, Dict[str, Any]] = {}
        for row in dataset:
            tier = row.get("predicted_tier") or "Tier Unspecified"
            if tier not in tier_stats:
                tier_stats[tier] = {
                    "count": 0,
                    "won": 0,
                    "total_revenue": 0.0,
                    "sales_cycle_sum": 0
                }
            tier_stats[tier]["count"] += 1
            if row.get("won"):
                tier_stats[tier]["won"] += 1
                tier_stats[tier]["total_revenue"] += float(row.get("deal_value") or 0.0)
            tier_stats[tier]["sales_cycle_sum"] += int(row.get("sales_cycle_days") or 60)

        tier_summary = {}
        for tier, stats in tier_stats.items():
            cnt = stats["count"]
            won_cnt = stats["won"]
            win_rate = (won_cnt / cnt) * 100.0 if cnt > 0 else 0.0
            avg_deal = (stats["total_revenue"] / won_cnt) if won_cnt > 0 else 0.0
            avg_cycle = stats["sales_cycle_sum"] / cnt if cnt > 0 else 0.0
            tier_summary[tier] = {
                "account_count": cnt,
                "won_count": won_cnt,
                "win_rate_pct": round(win_rate, 1),
                "total_won_arr": round(stats["total_revenue"], 2),
                "avg_deal_arr": round(avg_deal, 2),
                "avg_sales_cycle_days": round(avg_cycle, 1),
                "lift_vs_baseline": round(win_rate / overall_win_rate, 2) if overall_win_rate > 0 else 1.0
            }

        # Decile Win Rate Analysis
        sorted_records = sorted(dataset, key=lambda x: x.get("predicted_icp_score", 0), reverse=True)
        decile_size = max(1, total_accounts // 10)
        deciles: List[Dict[str, Any]] = []

        for i in range(10):
            start = i * decile_size
            end = min(total_accounts, (i + 1) * decile_size if i < 9 else total_accounts)
            bucket = sorted_records[start:end]
            if not bucket:
                continue
            b_won = sum(1 for d in bucket if d.get("won"))
            b_rate = (b_won / len(bucket)) * 100.0
            avg_score = sum(d.get("predicted_icp_score", 0) for d in bucket) / len(bucket)
            deciles.append({
                "decile": i + 1,
                "score_range": f"{bucket[-1].get('predicted_icp_score', 0):.0f} - {bucket[0].get('predicted_icp_score', 0):.0f}",
                "avg_score": round(avg_score, 1),
                "count": len(bucket),
                "won": b_won,
                "win_rate_pct": round(b_rate, 1),
                "lift": round(b_rate / overall_win_rate, 2) if overall_win_rate > 0 else 1.0
            })

        # Precision@Top-20%
        top_20_count = max(1, int(total_accounts * 0.20))
        top_20_records = sorted_records[:top_20_count]
        top_20_won = sum(1 for d in top_20_records if d.get("won"))
        precision_at_top20 = (top_20_won / top_20_count) * 100.0

        return {
            "total_accounts_evaluated": total_accounts,
            "overall_baseline_win_rate": round(overall_win_rate, 1),
            "precision_top_20_pct": round(precision_at_top20, 1),
            "top_20_lift": round(precision_at_top20 / overall_win_rate, 2) if overall_win_rate > 0 else 1.0,
            "tier_summary": tier_summary,
            "deciles": deciles
        }


class ICPDiscoveryEngine:
    """
    Dynamically mines customer datasets to discover statistical correlations
    and high-performing attributes among winning cohorts.
    """

    @classmethod
    def discover_patterns(cls, dataset: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        data = dataset or []
        if not data:
            return []

        total_count = len(data)
        base_won = sum(1 for d in data if d.get("won"))
        base_rate = (base_won / total_count) if total_count > 0 else 0.1

        # Group by Industry & Tier
        groups: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "won": 0, "total_arr": 0.0})
        for row in data:
            ind = str(row.get("industry") or row.get("predicted_tier") or "General Segment")
            groups[ind]["count"] += 1
            if row.get("won"):
                groups[ind]["won"] += 1
                groups[ind]["total_arr"] += float(row.get("deal_value") or 0.0)

        findings: List[Dict[str, Any]] = []
        for grp_name, stats in groups.items():
            cnt = stats["count"]
            if cnt >= 2:
                win_rate = stats["won"] / cnt
                lift = round(win_rate / base_rate, 2) if base_rate > 0 else 1.0
                if lift >= 1.2:
                    avg_deal = stats["total_arr"] / stats["won"] if stats["won"] > 0 else 0.0
                    findings.append({
                        "pattern_name": f"High Affinity Cluster: {grp_name}",
                        "conditions": [f"Segment / Cohort: {grp_name}", f"Cohort sample: {cnt} accounts"],
                        "sample_size": cnt,
                        "historical_win_rate": f"{win_rate*100:.1f}%",
                        "lift_multiplier": lift,
                        "avg_acv": f"${avg_deal:,.0f}",
                        "actionable_insight": f"Prioritize SDR outreach and marketing spend on {grp_name} accounts."
                    })

        return findings
