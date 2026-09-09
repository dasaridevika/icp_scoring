"""
Enterprise ICP Intelligence Engine - Comprehensive Worker AI Response Schema.
Defines the complete intelligence package returned when Worker AI handles the core workload.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator


class ComprehensiveAIWorkerResponse(BaseModel):
    """
    Full schema for edge-evaluated ICP Revenue Intelligence from Cloudflare Worker AI.
    """
    company_name: str = "Unspecified Company"
    domain: str = "unspecified.com"
    contact_name: str = "Unspecified Contact"
    job_title: str = "Unspecified Title"
    industry: str = "Unspecified Industry"
    scale: str = "Unspecified Scale"
    tech_stack: str = "Unspecified Stack"
    intent_timeline: str = "Unspecified Timeline"
    
    # 4 Core Engine Scores & Rationales (0-100)
    icp_fit_score: float = Field(default=50.0, ge=0.0, le=100.0)
    icp_fit_rationale: str = "Evaluated against ideal customer profile."
    
    intent_score: float = Field(default=50.0, ge=0.0, le=100.0)
    intent_rationale: str = "Evaluated for buying urgency and procurement signals."
    
    readiness_score: float = Field(default=50.0, ge=0.0, le=100.0)
    readiness_rationale: str = "Evaluated for decision-making authority and budget."
    
    value_score: float = Field(default=50.0, ge=0.0, le=100.0)
    expansion_potential: str = "Moderate"
    
    # Eligibility & Confidence
    is_disqualified: bool = False
    disqualification_reason: str = ""
    data_confidence_pct: int = Field(default=75, ge=0, le=100)
    
    # Priority & Strategic Action
    priority_tier: str = "Tier A2: High Priority Outbound"
    sales_action: str = "Initiate SDR outbound sequence."
    urgency_sla: str = "Within 24 hours"
    recommended_channel: str = "Email + LinkedIn"
    
    # Strategy Copy & Gap Analysis
    value_wedge: str = "Accelerate strategic growth initiatives."
    outreach_hook: str = "Reaching out regarding your growth roadmap."
    discovery_questions: List[str] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)

    @field_validator("icp_fit_score", "intent_score", "readiness_score", "value_score", mode="before")
    def clamp_scores(cls, v: Any) -> float:
        try:
            return max(0.0, min(100.0, float(v)))
        except Exception:
            return 50.0
