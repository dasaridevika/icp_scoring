"""
Enterprise ICP Intelligence Engine - Model Calibration & Win Propensity Layer.
Calibrates empirical win probability P(Win | Account Features) using logistic regression
and historical outcomes, preventing fake or uncalibrated conversion claims.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss


class ModelCalibrator:
    """
    Fits and compares an empirical Logistic Regression model against deterministic heuristic scores.
    """

    def __init__(self):
        self.model: Optional[LogisticRegression] = None
        self.is_fitted: bool = False
        self.feature_names = [
            "icp_fit_score",
            "intent_score",
            "readiness_score",
            "value_score",
            "confidence_score"
        ]

    def fit_historical_data(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Trains a calibrated model on historical opportunities.
        Each record must have feature scores (0-100) and binary 'won' outcome.
        """
        if len(dataset) < 10:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 10 historical records to calibrate ML model, got {len(dataset)}."
            }

        X = []
        y = []
        for row in dataset:
            features = [
                float(row.get("icp_fit_score", 50.0)),
                float(row.get("intent_score", 50.0)),
                float(row.get("readiness_score", 50.0)),
                float(row.get("value_score", 50.0)),
                float(row.get("confidence_score", 0.5) * 100.0 if row.get("confidence_score", 0.5) <= 1.0 else row.get("confidence_score", 50.0))
            ]
            X.append(features)
            y.append(1 if row.get("won") else 0)

        X_arr = np.array(X)
        y_arr = np.array(y)

        # Ensure we have both classes
        if len(np.unique(y_arr)) < 2:
            return {
                "status": "single_class",
                "message": "Dataset contains only won or only lost deals. Both classes required."
            }

        clf = LogisticRegression(class_weight="balanced", max_iter=200)
        clf.fit(X_arr, y_arr)
        self.model = clf
        self.is_fitted = True

        probs = clf.predict_proba(X_arr)[:, 1]
        brier = brier_score_loss(y_arr, probs)

        coefficients = {
            name: round(float(coef), 4)
            for name, coef in zip(self.feature_names, clf.coef_[0])
        }

        return {
            "status": "calibrated",
            "sample_size": len(dataset),
            "brier_score": round(float(brier), 4),
            "coefficients": coefficients,
            "intercept": round(float(clf.intercept_[0]), 4)
        }

    def predict_propensity(
        self,
        icp_fit: float,
        intent: float,
        readiness: float,
        value: float,
        confidence: float
    ) -> float:
        """
        Calculates calibrated P(Win | Account Features).
        If model is not yet fitted on sufficient data, falls back to conservative heuristic propensity.
        """
        if self.is_fitted and self.model is not None:
            features = np.array([[icp_fit, intent, readiness, value, confidence * 100.0]])
            prob = float(self.model.predict_proba(features)[0, 1])
            return round(min(0.95, max(0.02, prob)), 3)

        # Baseline Heuristic Propensity (Explicitly labeled as uncalibrated heuristic)
        # Mathematical sigmoid blend based on Fit (35%), Intent (30%), Readiness (25%), and Confidence multiplier
        composite = (icp_fit * 0.35) + (intent * 0.30) + (readiness * 0.25) + (value * 0.10)
        # Apply confidence discount: unverified/missing data lowers propensity
        conf_factor = max(0.3, confidence)
        raw_prob = (composite / 100.0) * conf_factor * 0.45  # Peak baseline win rate ~40-45% for dream deals
        return round(min(0.90, max(0.02, raw_prob)), 3)


# Global calibrator instance
global_calibrator = ModelCalibrator()
