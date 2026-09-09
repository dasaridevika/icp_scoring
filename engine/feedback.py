"""
Enterprise ICP Intelligence Engine - Dynamic Feedback Loop & Outcome Store.
100% Dynamic - Eliminates hardcoded mock datasets.
Persists and retrieves real logged predictions and sales outcomes.
"""

from typing import List, Dict, Any, Optional
import json
import os
from .models import FeedbackPredictionRecord

FEEDBACK_STORE_PATH = os.path.join(os.path.dirname(__file__), "feedback_records.json")


class FeedbackStore:
    """
    Manages persistence and retrieval of real historical predictions and closed outcomes.
    """

    @classmethod
    def get_all_records(cls) -> List[Dict[str, Any]]:
        if os.path.exists(FEEDBACK_STORE_PATH):
            try:
                with open(FEEDBACK_STORE_PATH, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    if isinstance(stored, list):
                        return stored
            except Exception:
                pass
        return []

    @classmethod
    def record_prediction(cls, prediction_dict: Dict[str, Any]) -> None:
        records = cls.get_all_records()
        records.append(prediction_dict)
        try:
            with open(FEEDBACK_STORE_PATH, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            print(f"[FeedbackStore Error]: {e}")

    @classmethod
    def update_outcome(
        cls,
        account_id: str,
        won: bool,
        deal_value: float,
        sales_cycle_days: int
    ) -> bool:
        records = cls.get_all_records()
        found = False
        for rec in records:
            if rec.get("account_id") == account_id or str(rec.get("company_name", "")).lower() == account_id.lower():
                rec["won"] = won
                rec["deal_value"] = deal_value
                rec["sales_cycle_days"] = sales_cycle_days
                found = True
        if found:
            try:
                with open(FEEDBACK_STORE_PATH, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2)
            except Exception:
                pass
        return found
