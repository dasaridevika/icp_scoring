"""
Enterprise ICP Intelligence Engine - Configuration & Versioning Layer.
Defines version tracking, weight configuration with validation (sum == 1.0),
hard disqualifiers, and scoring thresholds.
"""

from typing import Dict, Any, List, Optional
import os
try:
    import yaml
except ImportError:
    yaml = None
from pydantic import BaseModel, Field, field_validator


CURRENT_MODEL_VERSION = "ICP-v2.0-Production"
MODEL_CHANGELOG = {
    "ICP-v1.0": "Initial prototype: single 1-100 score, combined intent & fit, default unknown=70.",
    "ICP-v2.0-Production": (
        "Separated ICP Fit, Intent, Readiness, and Value. Added explicit Unknown data status, "
        "confidence modeling, hard eligibility gates, Golden customer similarity, expected value (EV), "
        "versioning, and historical outcome feedback loop."
    )
}


class ICPFitWeights(BaseModel):
    firmographic: float = Field(default=0.25, description="Headcount, revenue scale, operating model")
    industry_vertical: float = Field(default=0.25, description="Industry alignment and over-indexing")
    problem_use_case: float = Field(default=0.20, description="Pain point match & workflow suitability")
    technographic: float = Field(default=0.15, description="Tech stack compatibility & data maturity")
    geographic_market: float = Field(default=0.05, description="Region and regulatory environment")
    historical_similarity: float = Field(default=0.10, description="Similarity to Golden Customers")

    @field_validator("*", mode="after")
    def check_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Weights cannot be negative")
        return v

    def validate_sum(self, tolerance: float = 1e-4) -> bool:
        total = (
            self.firmographic
            + self.industry_vertical
            + self.problem_use_case
            + self.technographic
            + self.geographic_market
            + self.historical_similarity
        )
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"ICP Fit weights must sum to 1.0, got {total:.4f}")
        return True


class IntentWeights(BaseModel):
    active_search_research: float = Field(default=0.30, description="RFP, solution search, content consumption")
    project_timeline: float = Field(default=0.35, description="Immediate buying timeline (0-3 months)")
    hiring_and_expansion: float = Field(default=0.20, description="Hiring in relevant roles, funding, expansion")
    competitor_evaluation: float = Field(default=0.15, description="Comparing against competitors")

    def validate_sum(self, tolerance: float = 1e-4) -> bool:
        total = self.active_search_research + self.project_timeline + self.hiring_and_expansion + self.competitor_evaluation
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Intent weights must sum to 1.0, got {total:.4f}")
        return True


class ReadinessWeights(BaseModel):
    decision_maker_authority: float = Field(default=0.35, description="VP/C-Level budget authority")
    budget_allocated: float = Field(default=0.30, description="Confirmed budget or purchasing capacity")
    implementation_capability: float = Field(default=0.20, description="Internal technical/ops team ready to deploy")
    procurement_simplicity: float = Field(default=0.15, description="Standard procurement vs complex red tape")

    def validate_sum(self, tolerance: float = 1e-4) -> bool:
        total = self.decision_maker_authority + self.budget_allocated + self.implementation_capability + self.procurement_simplicity
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Readiness weights must sum to 1.0, got {total:.4f}")
        return True


class MasterWeights(BaseModel):
    icp_fit: float = Field(default=0.35, description="Weight for ICP Fit engine in Master Score")
    intent: float = Field(default=0.25, description="Weight for Intent engine in Master Score")
    readiness: float = Field(default=0.20, description="Weight for Readiness engine in Master Score")
    value: float = Field(default=0.20, description="Weight for Value engine in Master Score")

    def validate_sum(self, tolerance: float = 1e-4) -> bool:
        total = self.icp_fit + self.intent + self.readiness + self.value
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Master weights must sum to 1.0, got {total:.4f}")
        return True


class TierThresholds(BaseModel):
    tier_a1_min_fit: float = 80.0
    tier_a1_min_intent: float = 70.0
    tier_a2_min_fit: float = 65.0
    tier_b1_min_fit: float = 50.0
    tier_b1_min_intent: float = 50.0
    tier_a3_min_fit: float = 40.0


class DisqualificationRuleConfig(BaseModel):
    blocked_email_domains: List[str] = Field(
        default_factory=lambda: [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "icloud.com", "protonmail.com", "mail.ru", "163.com"
        ]
    )
    blocked_industries: List[str] = Field(
        default_factory=lambda: [
            "Gambling & Casinos", "Adult Entertainment", "Tobacco & Vaping"
        ]
    )
    unsupported_countries: List[str] = Field(
        default_factory=lambda: [
            "North Korea", "Iran", "Syria", "Cuba", "Crimea"
        ]
    )
    min_employee_count: int = Field(default=10, description="Minimum headcount for commercial viability")
    min_annual_revenue_usd: float = Field(default=100000.0, description="Minimum ARR for enterprise tier")


class EngineConfiguration(BaseModel):
    model_version: str = Field(default=CURRENT_MODEL_VERSION)
    master_weights: MasterWeights = Field(default_factory=MasterWeights)
    icp_fit_weights: ICPFitWeights = Field(default_factory=ICPFitWeights)
    intent_weights: IntentWeights = Field(default_factory=IntentWeights)
    readiness_weights: ReadinessWeights = Field(default_factory=ReadinessWeights)
    tier_thresholds: TierThresholds = Field(default_factory=TierThresholds)
    disqualification: DisqualificationRuleConfig = Field(default_factory=DisqualificationRuleConfig)
    
    # Financial Calibration Defaults (heuristic baseline before regression calibration)
    default_base_cac: float = Field(default=8000.0, description="Average sales & marketing cost to acquire")
    default_retention_rate: float = Field(default=0.88, description="Baseline 1-yr gross retention rate")

    def validate_all_weights(self) -> None:
        self.master_weights.validate_sum()
        self.icp_fit_weights.validate_sum()
        self.intent_weights.validate_sum()
        self.readiness_weights.validate_sum()

    @classmethod
    def load_from_yaml(cls, yaml_path: str) -> "EngineConfiguration":
        if not os.path.exists(yaml_path):
            config = cls()
            config.validate_all_weights()
            return config
        if yaml is None:
            raise ImportError("PyYAML is required to load configuration from YAML files. Install pyyaml.")
        with open(yaml_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
        config = cls(**raw_data)
        config.validate_all_weights()
        return config


# Global active configuration instance
active_config = EngineConfiguration()
active_config.validate_all_weights()

