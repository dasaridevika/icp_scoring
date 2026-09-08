"""
Data models for the Enterprise ICP Lead Qualification Engine.
Based on the Saber ICP Scoring Model Framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PillarScore:
    """Represents the evaluation score and rationale for a single ICP dimension."""
    dimension_name: str
    weight: float          # e.g., 0.30 for Firmographic
    raw_score: float       # 0 - 100
    points_contributed: float # raw_score * weight
    rationale: str


@dataclass
class PillarBreakdown:
    """The four core pillars of the Saber ICP Scoring Model."""
    firmographic: PillarScore
    technographic: PillarScore
    intent: PillarScore
    persona: PillarScore


@dataclass
class StrategyRecommendation:
    """AI-generated value wedge and customized cold outreach opener."""
    value_wedge: str
    outreach_hook: str


@dataclass
class ICPScoreResult:
    """Complete, normalized qualification evaluation for a prospect."""
    company_name: str
    contact_name: str
    job_title: str
    industry: str
    
    # Master Score & Classification
    final_icp_score: int          # 0 - 100
    saber_tier: str               # Tier 1, Tier 2, Tier 3, Disqualified
    priority_level: str           # Strategic, Standard, Nurture, Deprioritized
    sales_action: str             # SLA & response cadence instructions
    
    # Strategic Matrices
    fit_index: int                # 0 - 100 (Firmographic + Technographic)
    intent_index: int             # 0 - 100 (Intent + Persona)
    conversion_probability: int   # Estimated win probability %
    
    # Financial Impact
    estimated_deal_size: float
    quality_weighted_value: float # deal_size * (score / 100)
    
    # Disqualification / Negative Scoring
    is_disqualified: bool
    disqualification_reason: str
    
    # Granular Pillars
    pillars: PillarBreakdown
    
    # Sales Action Copy
    strategy: StrategyRecommendation
    
    # CRM Integration Mapping
    crm_payload: Dict[str, Any] = field(default_factory=dict)
