"""
Enterprise ICP Intelligence Engine - Comprehensive Domain & Worker AI Response Schemas.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class DataStatus(str, Enum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"


class EvidenceField(BaseModel):
    value: Any = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "Unknown"
    status: DataStatus = DataStatus.UNKNOWN
    rationale: str = ""


class DimensionScore(BaseModel):
    name: str
    raw_score: float = Field(default=0.0, ge=0.0, le=100.0)
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    weighted_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: str = ""
    status: DataStatus = DataStatus.UNKNOWN


class ICPFitScore(BaseModel):
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: List[DimensionScore] = Field(default_factory=list)
    rationale: str = ""


class IntentScore(BaseModel):
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: List[DimensionScore] = Field(default_factory=list)
    rationale: str = ""


class ReadinessScore(BaseModel):
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: List[DimensionScore] = Field(default_factory=list)
    rationale: str = ""


class ValueScore(BaseModel):
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: List[DimensionScore] = Field(default_factory=list)
    expansion_potential: str = "Uncertain"
    rationale: str = ""


class EligibilityResult(BaseModel):
    eligible: bool = True
    disqualification_reasons: List[str] = Field(default_factory=list)


class SimilarCustomerMatch(BaseModel):
    customer_name: str
    industry: str
    similarity_score: float
    deal_size_arr: float
    sales_cycle_days: int
    retention_health: str


class ExpectedValueResult(BaseModel):
    deal_size_usd: float = 50000.0
    win_probability_pct: float = 0.0
    expected_arr_usd: float = 0.0
    expansion_arr_forecast_usd: float = 0.0


class NextBestAction(BaseModel):
    priority_tier: str = "Unqualified"
    saber_tier: str = "Tier C: Long-Tail / Self-Serve"
    recommended_channel: str = "Email"
    urgency_sla: str = "Within 48 hours"
    action_statement: str = "Conduct discovery qualification."
    value_wedge: str = ""
    outreach_hook: str = ""
    discovery_questions: List[str] = Field(default_factory=list)


class MasterAccountIntelligence(BaseModel):
    company_name: Optional[str] = None
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    scale: Optional[str] = None
    overall_confidence: float = 0.0
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    eligibility: EligibilityResult = Field(default_factory=EligibilityResult)
    fit_engine: ICPFitScore = Field(default_factory=ICPFitScore)
    intent_engine: IntentScore = Field(default_factory=IntentScore)
    readiness_engine: ReadinessScore = Field(default_factory=ReadinessScore)
    value_engine: ValueScore = Field(default_factory=ValueScore)

    master_icp_score: float = 0.0
    calibrated_win_probability_pct: float = 0.0
    expected_value: ExpectedValueResult = Field(default_factory=ExpectedValueResult)
    similar_golden_customers: List[SimilarCustomerMatch] = Field(default_factory=list)
    next_best_action: NextBestAction = Field(default_factory=NextBestAction)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)


class AccountRecord(BaseModel):
    account_id: str
    company_name: str
    domain: str
    industry: str
    headcount: int
    annual_revenue_usd: float
    tech_stack: List[str] = Field(default_factory=list)
    status: str = "Active"


class OpportunityRecord(BaseModel):
    opportunity_id: str
    account_id: str
    stage: str
    amount_usd: float
    close_date: Optional[str] = None
    is_won: bool = False


class SalesActivityRecord(BaseModel):
    activity_id: str
    account_id: str
    activity_type: str
    timestamp: str
    notes: str = ""


class FeedbackPredictionRecord(BaseModel):
    account_name: str
    domain: str
    predicted_score: float
    predicted_tier: str
    predicted_win_prob: float
    actual_outcome: str
    actual_revenue: float
    feedback_notes: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ComprehensiveAIWorkerResponse(BaseModel):
    """
    Full schema for edge-evaluated ICP Revenue Intelligence from Cloudflare Worker AI.
    """
    company_name: Optional[str] = None
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    scale: Optional[str] = None
    tech_stack: Optional[str] = None
    intent_timeline: Optional[str] = None
    
    # 4 Core Engine Scores & Rationales (0-100)
    icp_fit_score: float = Field(default=0.0, ge=0.0, le=100.0)
    icp_fit_rationale: str = "Pillar evaluation pending or unverified."
    
    intent_score: float = Field(default=0.0, ge=0.0, le=100.0)
    intent_rationale: str = "Pillar evaluation pending or unverified."
    
    readiness_score: float = Field(default=0.0, ge=0.0, le=100.0)
    readiness_rationale: str = "Pillar evaluation pending or unverified."
    
    value_score: float = Field(default=0.0, ge=0.0, le=100.0)
    expansion_potential: str = "Uncertain"
    
    # Eligibility & Confidence
    is_disqualified: bool = False
    disqualification_reason: str = ""
    data_confidence_pct: int = Field(default=0, ge=0, le=100)
    
    # Priority & Strategic Action
    priority_tier: str = "Unqualified"
    sales_action: str = "Execute discovery qualification."
    urgency_sla: str = "Within 48 hours"
    recommended_channel: str = "Email"
    
    # Strategy Copy & Gap Analysis
    value_wedge: str = ""
    outreach_hook: str = ""
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)

    @field_validator("icp_fit_score", "intent_score", "readiness_score", "value_score", mode="before")
    def clamp_scores(cls, v: Any) -> float:
        try:
            return max(0.0, min(100.0, float(v)))
        except Exception:
            return 0.0


