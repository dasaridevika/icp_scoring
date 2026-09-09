"""
Enterprise ICP Intelligence Engine - Model Calibration & Win Propensity Layer.
Calibrates empirical win probability P(Win | Account Features) using logistic regression
and historical outcomes, preventing fake or uncalibrated conversion claims.
"""

from typing import List, Dict, Any, Tuple, Optional
import math


class ModelCalibrator:
    """
    Fits and compares an empirical Logistic Regression model against deterministic heuristic scores.
    """

    def __init__(self):
        self.weights: Optional[List[float]] = None
        self.intercept: float = 0.0
        self.is_fitted: bool = False
        self.feature_names = [
            "icp_fit_score",
            "intent_score",
            "readiness_score",
            "value_score",
            "confidence_score"
        ]

    def _sigmoid(self, z: float) -> float:
        z = max(-500.0, min(500.0, z))
        return 1.0 / (1.0 + math.exp(-z))

    def fit_historical_data(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Trains a calibrated model on historical opportunities using pure-Python logistic regression.
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
                float(row.get("icp_fit_score", 50.0)) / 100.0,
                float(row.get("intent_score", 50.0)) / 100.0,
                float(row.get("readiness_score", 50.0)) / 100.0,
                float(row.get("value_score", 50.0)) / 100.0,
                float(row.get("confidence_score", 0.5) if row.get("confidence_score", 0.5) <= 1.0 else row.get("confidence_score", 50.0) / 100.0)
            ]
            X.append(features)
            y.append(1.0 if row.get("won") else 0.0)

        won_count = sum(1 for label in y if label == 1.0)
        if won_count == 0 or won_count == len(y):
            return {
                "status": "single_class",
                "message": "Dataset contains only won or only lost deals. Both classes required."
            }

        # Pure Python Gradient Descent
        n_features = len(self.feature_names)
        n_samples = len(X)
        weights = [0.0] * n_features
        intercept = 0.0
        learning_rate = 0.1
        epochs = 300

        for _ in range(epochs):
            dw = [0.0] * n_features
            db = 0.0
            for i in range(n_samples):
                z = intercept + sum(weights[j] * X[i][j] for j in range(n_features))
                p = self._sigmoid(z)
                err = p - y[i]
                for j in range(n_features):
                    dw[j] += err * X[i][j]
                db += err
            for j in range(n_features):
                weights[j] -= (learning_rate / n_samples) * dw[j]
            intercept -= (learning_rate / n_samples) * db

        self.weights = weights
        self.intercept = intercept
        self.is_fitted = True

        # Compute Brier Score in pure Python
        brier = 0.0
        for i in range(n_samples):
            z = intercept + sum(weights[j] * X[i][j] for j in range(n_features))
            p = self._sigmoid(z)
            brier += (p - y[i]) ** 2
        brier /= n_samples

        coefficients = {
            name: round(w, 4)
            for name, w in zip(self.feature_names, weights)
        }

        return {
            "status": "calibrated",
            "sample_size": n_samples,
            "brier_score": round(brier, 4),
            "coefficients": coefficients,
            "intercept": round(intercept, 4)
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
        if self.is_fitted and self.weights is not None:
            norm_features = [
                icp_fit / 100.0,
                intent / 100.0,
                readiness / 100.0,
                value / 100.0,
                confidence if confidence <= 1.0 else confidence / 100.0
            ]
            z = self.intercept + sum(w * x for w, x in zip(self.weights, norm_features))
            prob = self._sigmoid(z)
            return round(min(0.95, max(0.02, prob)), 3)

        # Baseline Heuristic Propensity (Mathematical sigmoid blend based on Fit, Intent, Readiness, Value)
        composite = (icp_fit * 0.35) + (intent * 0.30) + (readiness * 0.25) + (value * 0.10)
        conf_factor = max(0.3, confidence if confidence <= 1.0 else confidence / 100.0)
        raw_prob = (composite / 100.0) * conf_factor * 0.45
        return round(min(0.90, max(0.02, raw_prob)), 3)


# Global calibrator instance
global_calibrator = ModelCalibrator()
