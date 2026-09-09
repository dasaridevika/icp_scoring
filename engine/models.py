"""
Enterprise ICP Intelligence Engine - Canonical Assessment & Domain Models.
Defines the authoritative AccountAssessment data contract, evidence statuses,
pillar evaluations, decision structures, and metadata.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    KNOWN_POSITIVE = "KNOWN_POSITIVE"
    KNOWN_NEGATIVE = "KNOWN_NEGATIVE"
    SOURCE_BACKED = "SOURCE_BACKED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"



# Alias for backward compatibility
DataStatus = EvidenceStatus


class EvidenceField(BaseModel):
    name: str = ""
    raw_value: Any = None
    value: Any = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "Unknown"
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    rationale: str = ""


class DimensionScore(BaseModel):
    name: str
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    raw_score: float = Field(default=0.0, ge=0.0, le=100.0)
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    points_contributed: float = Field(default=0.0, ge=0.0, le=100.0)
    weighted_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    evidence: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class EvidencePillar(BaseModel):
    score: Optional[float] = None
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_points: List[str] = Field(default_factory=list)
    rationale: str = ""
    missing_points: List[str] = Field(default_factory=list)


class ICPFitScore(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: Dict[str, DimensionScore] = Field(default_factory=dict)
    rationale: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class IntentScore(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: Dict[str, DimensionScore] = Field(default_factory=dict)
    rationale: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class ReadinessScore(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    dimensions: Dict[str, DimensionScore] = Field(default_factory=dict)
    rationale: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class ValueScore(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_arr: float = 50000.0
    deal_size_usd: float = 50000.0
    expansion_potential: str = "Uncertain"
    dimensions: Dict[str, DimensionScore] = Field(default_factory=dict)
    rationale: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


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
    opportunity_propensity: float = 0.0
    deal_size_usd: float = 50000.0
    expected_arr: float = 50000.0
    p_retention: float = 0.88
    expected_lifetime_value: float = 0.0
    expected_cac: float = 8000.0
    expected_net_value: float = 0.0
    sales_effort_score: float = 5.0
    priority_rank_score: float = 0.0


class NextBestAction(BaseModel):
    priority_tier: str = "Unqualified"
    saber_tier: str = "Tier C: Long-Tail / Self-Serve"
    action: str = "Conduct discovery qualification."
    action_statement: str = "Conduct discovery qualification."
    urgency_sla: str = "Within 48 hours"
    recommended_channel: str = "Email"
    target_persona: str = ""
    reason: str = ""
    value_wedge: str = ""
    outreach_hook: str = ""
    discovery_questions: List[str] = Field(default_factory=list)
    discovery_gap_prompts: List[str] = Field(default_factory=list)


class AccountInfo(BaseModel):
    company_name: Optional[str] = None
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    scale: Optional[str] = None
    tech_stack: Optional[str] = None
    intent_timeline: Optional[str] = None


class ScoresBreakdown(BaseModel):
    icp_fit: float = Field(default=0.0, ge=0.0, le=100.0)
    intent: float = Field(default=0.0, ge=0.0, le=100.0)
    readiness: float = Field(default=0.0, ge=0.0, le=100.0)
    value: float = Field(default=0.0, ge=0.0, le=100.0)
    master_icp_score: float = Field(default=0.0, ge=0.0, le=100.0)


class ConfidenceBreakdown(BaseModel):
    overall: float = Field(default=0.0, ge=0.0, le=1.0)
    icp_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    intent: float = Field(default=0.0, ge=0.0, le=1.0)
    readiness: float = Field(default=0.0, ge=0.0, le=1.0)
    value: float = Field(default=0.0, ge=0.0, le=1.0)


class EvidenceBreakdown(BaseModel):
    firmographic: EvidencePillar = Field(default_factory=EvidencePillar)
    technographic: EvidencePillar = Field(default_factory=EvidencePillar)
    intent: EvidencePillar = Field(default_factory=EvidencePillar)
    readiness: EvidencePillar = Field(default_factory=EvidencePillar)
    value: EvidencePillar = Field(default_factory=EvidencePillar)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    discovery_questions: List[str] = Field(default_factory=list)


class DecisionInfo(BaseModel):
    tier: str = "Tier C: Low Priority"
    priority: str = "Low"
    sales_action: str = "Conduct discovery qualification."
    urgency_sla: str = "Within 48 hours"
    recommended_channel: str = "Email"
    is_disqualified: bool = False
    disqualification_reason: str = ""
    value_wedge: str = ""
    outreach_hook: str = ""


class CommercialInfo(BaseModel):
    deal_size_usd: float = 50000.0
    estimated_arr: float = 50000.0
    win_propensity_pct: float = 0.0
    expected_value_usd: float = 0.0
    expansion_potential: str = "Uncertain"


class AssessmentMetadata(BaseModel):
    request_id: str = Field(default_factory=lambda: f"req_{int(datetime.now(timezone.utc).timestamp()*1000)}")
    model_version: str = "ICP-v2.0-Production"
    prompt_version: str = "1.0.0"
    scored_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evaluation_engine: str = "Deterministic Revenue Scorer"
    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class AccountAssessment(BaseModel):
    """
    The Authoritative Canonical Assessment Model.
    Unifies Account Information, Deterministic Scores, Confidence Breakdown,
    Structured Evidence, Commercial Modeling, and Decision Output.
    """
    account: AccountInfo = Field(default_factory=AccountInfo)
    scores: ScoresBreakdown = Field(default_factory=ScoresBreakdown)
    confidence: ConfidenceBreakdown = Field(default_factory=ConfidenceBreakdown)
    evidence: EvidenceBreakdown = Field(default_factory=EvidenceBreakdown)
    decision: DecisionInfo = Field(default_factory=DecisionInfo)
    commercial: CommercialInfo = Field(default_factory=CommercialInfo)
    metadata: AssessmentMetadata = Field(default_factory=AssessmentMetadata)

    # Top-level helper properties for seamless UI & backward compatibility
    @property
    def company_name(self) -> Optional[str]:
        return self.account.company_name

    @property
    def domain(self) -> Optional[str]:
        return self.account.domain

    @property
    def contact_name(self) -> Optional[str]:
        return self.account.contact_name

    @property
    def job_title(self) -> Optional[str]:
        return self.account.job_title

    @property
    def industry(self) -> Optional[str]:
        return self.account.industry

    @property
    def location(self) -> Optional[str]:
        return self.account.location

    @property
    def scale(self) -> Optional[str]:
        return self.account.scale

    @property
    def tech_stack(self) -> Optional[str]:
        return self.account.tech_stack

    @property
    def intent_timeline(self) -> Optional[str]:
        return self.account.intent_timeline

    @property
    def icp_fit_score(self) -> float:
        return self.scores.icp_fit

    @property
    def icp_fit_rationale(self) -> str:
        return self.evidence.firmographic.rationale or "Firmographic and operational ICP fit evaluation."

    @property
    def intent_score(self) -> float:
        return self.scores.intent

    @property
    def intent_rationale(self) -> str:
        return self.evidence.intent.rationale or "Buying urgency and timeline evaluation."

    @property
    def readiness_score(self) -> float:
        return self.scores.readiness

    @property
    def readiness_rationale(self) -> str:
        return self.evidence.readiness.rationale or "Decision maker authority and procurement readiness."

    @property
    def value_score(self) -> float:
        return self.scores.value

    @property
    def expansion_potential(self) -> str:
        return self.commercial.expansion_potential

    @property
    def is_disqualified(self) -> bool:
        return self.decision.is_disqualified

    @property
    def disqualification_reason(self) -> str:
        return self.decision.disqualification_reason

    @property
    def data_confidence_pct(self) -> int:
        return int(round(self.confidence.overall * 100))

    @property
    def priority_tier(self) -> str:
        return self.decision.tier

    @property
    def sales_action(self) -> str:
        return self.decision.sales_action

    @property
    def urgency_sla(self) -> str:
        return self.decision.urgency_sla

    @property
    def recommended_channel(self) -> str:
        return self.decision.recommended_channel

    @property
    def value_wedge(self) -> str:
        return self.decision.value_wedge

    @property
    def outreach_hook(self) -> str:
        return self.decision.outreach_hook

    @property
    def discovery_questions(self) -> List[str]:
        return self.evidence.discovery_questions

    @property
    def key_strengths(self) -> List[str]:
        return self.evidence.key_strengths

    @property
    def key_risks(self) -> List[str]:
        return self.evidence.key_risks

    @property
    def success(self) -> bool:
        return self.metadata.success

    @property
    def request_id(self) -> str:
        return self.metadata.request_id

    @property
    def error_message(self) -> Optional[str]:
        return self.metadata.error_message


# Backward compatibility aliases
ComprehensiveAIWorkerResponse = AccountAssessment


class MasterAccountIntelligence(BaseModel):
    account_id: str = ""
    company_name: Optional[str] = None
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    location: str = "Commercial"
    scale: Optional[str] = None
    model_version: str = "ICP-v2.0-Production"
    scored_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    eligibility: EligibilityResult = Field(default_factory=EligibilityResult)
    icp_fit: ICPFitScore = Field(default_factory=ICPFitScore)
    intent: IntentScore = Field(default_factory=IntentScore)
    readiness: ReadinessScore = Field(default_factory=ReadinessScore)
    value: ValueScore = Field(default_factory=ValueScore)

    overall_priority: str = "Tier C: Low Priority"
    overall_confidence: float = 0.0
    expected_value: ExpectedValueResult = Field(default_factory=ExpectedValueResult)
    similar_customers: List[SimilarCustomerMatch] = Field(default_factory=list)
    next_best_action: NextBestAction = Field(default_factory=NextBestAction)
    evidence_fields: Dict[str, Any] = Field(default_factory=dict)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks_and_gaps: List[str] = Field(default_factory=list)
    audit_trail: List[str] = Field(default_factory=list)
    crm_payload: Dict[str, Any] = Field(default_factory=dict)


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



