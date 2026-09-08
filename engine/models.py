"""
Data models for the Enterprise ICP Qualification Engine.
Step 1: Extracted Characteristics & Uncertainty.
Step 2: Polarized Scoring Scale (-5 to +5) & 4-Pillar Breakdown.
Step 3: Master ICP Score, Qualification Tiers & Deal Forecaster.
Step 4: Sales Cadence SLAs, Fit vs Intent Matrix & CRM Sync.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ExtractedProspectData:
    """Step 1 Model: Parsed characteristics, confidence metrics, and discovery questions."""
    company_name: str
    contact_name: str
    job_title: str
    industry: str
    scale_revenue: str
    technographics: str
    intent_urgency: str
    
    # Uncertainty Tracking & Data Quality
    verified_fields: List[str] = field(default_factory=list)
    uncertain_fields: List[str] = field(default_factory=list)
    confidence_score: int = 0  # 0% - 100%
    
    # Gap-Filling Prompts for Sales Discovery (GTM Partners Step 4)
    discovery_questions: List[str] = field(default_factory=list)
    
    # Raw context for downstream scoring steps
    raw_text: str = ""
    raw_ai_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PillarEvaluation:
    """Step 2 Model: GTM Partners Polarized Rating & Saber Pillar Score."""
    name: str
    weight: float            # 0.30, 0.25, 0.25, 0.20
    gtm_scale: int           # -5, -3, -1, +1, +3, +5
    gtm_label: str           # e.g., "+5: High LTV & Rapid Expansion"
    score_100: float         # Normalized 0 - 100
    points_contributed: float # score_100 * weight
    rationale: str
    is_uncertain: bool = False


@dataclass
class FourPillarBreakdown:
    """Step 2 Container for the 4 Evaluation Pillars."""
    firmographic: PillarEvaluation
    technographic: PillarEvaluation
    intent: PillarEvaluation
    persona: PillarEvaluation


@dataclass
class StrategyRecommendation:
    """Step 4 Model: Tailored strategic value wedge and cold outreach opener."""
    value_wedge: str
    outreach_hook: str


@dataclass
class MasterScoreResult:
    """Step 3 & 4 Model: Complete Operational Qualification Result."""
    final_score: int                 # 0 - 100
    tier_name: str                   # Tier 1, Tier 2, Tier 3, Out of ICP
    priority_level: str              # Strategic, Standard, Nurture, Disqualified
    sales_action: str                # SLA response cadence
    
    # 2D Matrix Indices (6sense / MadKudu)
    fit_index: int                   # 0 - 100 (Firmographic + Technographic)
    intent_index: int                # 0 - 100 (Intent + Persona)
    conversion_probability: int      # Win probability %
    
    # Financial Impact
    estimated_deal_size: float
    quality_weighted_value: float    # Deal Size * (final_score / 100)
    
    # Disqualification & Negative Scoring
    is_disqualified: bool
    disqualification_reason: str
    
    # Granular Pillars & Strategy
    pillars: FourPillarBreakdown
    strategy: StrategyRecommendation
    
    # CRM Integration Mapping
    crm_payload: Dict[str, Any] = field(default_factory=dict)
