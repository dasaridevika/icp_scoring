"""
Enterprise ICP Revenue Intelligence - AI Text Intelligence Analyzer.
High-precision semantic analysis for unstructured text fields:
1. Role Title & Hierarchy Classification (Seniority + Buyer Persona + Department)
2. Sub-Vertical & Niche Fit Analyzer (Macro-Sector alignment + High-margin fit)
3. Buying Intent & Urgency Extractor (Velocity score + Timeline triggers)
4. Technographics Ecosystem Parser (Complementary stack + Legacy friction)
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Output Models for AI Analysis
# ==============================================================================

class RoleAIAnalysis(BaseModel):
    raw_title: str
    seniority_level: str  # C-Suite / Founder (+5), VP / Head of (+5), Director (+3), Manager (+1), Individual Contributor (+1), Student / Intern (-5)
    seniority_points: int  # 5, 3, 1, -5
    persona_type: str  # Economic Buyer, Technical Champion, End User / Practitioner, Non-Buyer
    department: str  # e.g., Executive, Procurement, IT & Cloud, Sales & RevOps, Engineering, Finance, etc.
    confidence: float  # 0.0 to 1.0
    rationale: str
    is_disqualifier: bool = False


class NicheAIAnalysis(BaseModel):
    raw_niche: str
    suggested_sector: str
    market_complexity: str  # High-Margin Enterprise, Mid-Market Specialized, General Commodity
    fit_points: int  # 5, 3, 1
    rationale: str


class IntentAIAnalysis(BaseModel):
    raw_intent: str
    urgency_tier: str  # Immediate Active Buying (+5), Active Evaluation (+3), Top-of-Funnel / Browsing (+1)
    intent_points: int  # 5, 3, 1
    timeline_detected: Optional[str] = None
    extracted_signals: List[str] = Field(default_factory=list)
    rationale: str


class TechStackAIAnalysis(BaseModel):
    raw_stack: str
    modern_tools: List[str] = Field(default_factory=list)
    legacy_blockers: List[str] = Field(default_factory=list)
    ecosystem_fit: str  # High Synergies (+5), Standard Modern Stack (+3), Legacy Migration Friction (-1), Outdated Incompatible (-3)
    tech_points: int  # 5, 3, 1, -1, -3
    rationale: str


# ==============================================================================
# 2. AI Semantic Text Analyzer Engine
# ==============================================================================

class AITextAnalyzer:
    """
    Intelligent semantic parser and classifier for unstructured B2B text fields.
    """

    # --- Role & Persona Classification Matrix ---
    CSUITE_PATTERNS = [
        r'\b(c[eioftmsra]o|chief\s+[a-z\s]+officer|founder|co-founder|president|managing\s+director|owner|principal\s+partner|general\s+manager)\b'
    ]
    VP_PATTERNS = [
        r'\b(evp|svp|avp|vp|vice\s+president|head\s+of\s+[a-z\s]+|global\s+head|group\s+head)\b'
    ]
    DIRECTOR_PATTERNS = [
        r'\b(director|sr\.?\s+director|senior\s+director|associate\s+director|directeur)\b'
    ]
    MANAGER_PATTERNS = [
        r'\b(manager|lead|team\s+lead|supervisor|head\b(?!\s+of)|coordinator|operations\s+lead)\b'
    ]
    IC_PATTERNS = [
        r'\b(engineer|architect|analyst|developer|consultant|specialist|strategist|executive|account\s+exec|rep|sdr|bdr|associate|specialist|practitioner|scientist|administrator)\b'
    ]
    NON_BUYER_PATTERNS = [
        r'\b(intern|internship|student|trainee|apprentice|volunteer|fellow|academic|researcher\s+student|unemployed)\b'
    ]

    DEPARTMENT_MAP = {
        "Procurement & Supply Chain": [r'procurement', r'sourcing', r'purchasing', r'supply\s+chain', r'vendor', r'logistics', r'commercial'],
        "IT, Cloud & Infrastructure": [r'\bit\b', r'information\s+tech', r'cloud', r'devops', r'infrastructure', r'security', r'ciso', r'sysadmin', r'network', r'data\s+center'],
        "Product & Engineering": [r'engineer', r'software', r'technology', r'cto', r'product', r'qa', r'architecture', r'data\s+platform', r'ai', r'ml'],
        "Sales, RevOps & GTM": [r'sales', r'cro', r'revenue', r'revops', r'account', r'business\s+development', r'growth', r'commercial', r'partnerships'],
        "Finance & Legal": [r'finance', r'cfo', r'controller', r'accounting', r'treasury', r'legal', r'general\s+counsel', r'compliance'],
        "Operations & Transformation": [r'operations', r'coo', r'transformation', r'strategy', r'operational', r'continuous\s+improvement', r'processes'],
        "Marketing": [r'marketing', r'cmo', r'brand', r'demand\s+gen', r'content', r'communications']
    }

    # --- Technographic Keyword Recognition Matrix ---
    MODERN_ECOSYSTEM_KEYWORDS = {
        "SAP": "Enterprise ERP & Supply Chain",
        "AWS": "Cloud Infrastructure",
        "Azure": "Enterprise Microsoft Cloud",
        "Google Cloud": "GCP Cloud Infrastructure",
        "Snowflake": "Data Cloud & Warehousing",
        "Databricks": "Data Lakehouse & ML",
        "Salesforce": "Enterprise CRM",
        "HubSpot": "Inbound CRM & Marketing",
        "Workday": "Enterprise HR & Finance",
        "Oracle Cloud": "Enterprise Cloud ERP",
        "PostgreSQL": "Relational Data Platform",
        "Kubernetes": "Container Orchestration",
        "Stripe": "Billing & Payments Engine",
        "PowerBI": "Enterprise BI & Analytics",
        "Tableau": "Data Visualization",
        "ServiceNow": "ITSM Enterprise Workflow"
    }

    LEGACY_BLOCKER_KEYWORDS = {
        "AS400": "Legacy IBM Mainframe Architecture",
        "On-Premises Monolith": "Air-gapped Legacy Infrastructure",
        "Custom In-House Legacy": "Proprietary Unmaintained Stack",
        "Excel Manual": "Manual Spreadsheet Workflows",
        "Legacy Mainframe": "High-friction Mainframe Core",
        "Lotus Notes": "Obsolete Collaboration Platform"
    }

    @classmethod
    def analyze_role(cls, title: str) -> RoleAIAnalysis:
        """
        AI semantic analysis of raw job title to determine seniority, persona, and department.
        """
        raw = title.strip()
        if not raw:
            return RoleAIAnalysis(
                raw_title="Unspecified Role",
                seniority_level="Individual Contributor (+1)",
                seniority_points=1,
                persona_type="End User / Practitioner",
                department="General Business",
                confidence=0.5,
                rationale="No role provided; defaulting to baseline individual contributor."
            )

        t_lower = raw.lower()

        # 1. Check Non-Buyer / Intern
        for pat in cls.NON_BUYER_PATTERNS:
            if re.search(pat, t_lower):
                return RoleAIAnalysis(
                    raw_title=raw,
                    seniority_level="Student / Intern (-5)",
                    seniority_points=-5,
                    persona_type="Non-Buyer",
                    department="Academic / Entry-level",
                    confidence=0.95,
                    rationale=f"Identified non-buyer / student role keyword in '{raw}'.",
                    is_disqualifier=True
                )

        # 2. Check C-Suite / Executive
        for pat in cls.CSUITE_PATTERNS:
            if re.search(pat, t_lower):
                dept = cls._extract_department(t_lower)
                return RoleAIAnalysis(
                    raw_title=raw,
                    seniority_level="C-Suite / Founder (+5)",
                    seniority_points=5,
                    persona_type="Economic Buyer",
                    department=dept or "Executive Leadership",
                    confidence=0.95,
                    rationale=f"Executive leadership authority identified ({raw}) with signatory power."
                )

        # 3. Check VP / Head of
        for pat in cls.VP_PATTERNS:
            if re.search(pat, t_lower):
                dept = cls._extract_department(t_lower)
                return RoleAIAnalysis(
                    raw_title=raw,
                    seniority_level="VP / Head of (+5)",
                    seniority_points=5,
                    persona_type="Economic Buyer",
                    department=dept or "Departmental Leadership",
                    confidence=0.92,
                    rationale=f"VP / Department Head authority detected in '{raw}' with budget allocation mandate."
                )

        # 4. Check Director
        for pat in cls.DIRECTOR_PATTERNS:
            if re.search(pat, t_lower):
                dept = cls._extract_department(t_lower)
                return RoleAIAnalysis(
                    raw_title=raw,
                    seniority_level="Director (+3)",
                    seniority_points=3,
                    persona_type="Technical Champion / Budget Influencer",
                    department=dept or "Operations / Management",
                    confidence=0.90,
                    rationale=f"Director-level champion identified in '{raw}' with direct project influence."
                )

        # 5. Check Manager / Lead
        for pat in cls.MANAGER_PATTERNS:
            if re.search(pat, t_lower):
                dept = cls._extract_department(t_lower)
                return RoleAIAnalysis(
                    raw_title=raw,
                    seniority_level="Manager (+1)",
                    seniority_points=1,
                    persona_type="Technical Champion / Key Evaluator",
                    department=dept or "Team Operations",
                    confidence=0.85,
                    rationale=f"Management title detected in '{raw}'—key influencer in evaluation cycle."
                )

        # 6. Default to Individual Contributor
        dept = cls._extract_department(t_lower)
        return RoleAIAnalysis(
            raw_title=raw,
            seniority_level="Individual Contributor (+1)",
            seniority_points=1,
            persona_type="End User / Practitioner",
            department=dept or "Operations",
            confidence=0.80,
            rationale=f"Professional practitioner role detected in '{raw}'."
        )

    @classmethod
    def _extract_department(cls, t_lower: str) -> str:
        for dept, patterns in cls.DEPARTMENT_MAP.items():
            for pat in patterns:
                if re.search(pat, t_lower):
                    return dept
        return "General Business"

    @classmethod
    def analyze_niche(cls, niche: str, selected_sector: Optional[str] = None) -> NicheAIAnalysis:
        """
        AI analysis of free-form sub-vertical / niche to evaluate market complexity and commercial fit.
        """
        raw = niche.strip()
        if not raw:
            return NicheAIAnalysis(
                raw_niche="General Commercial",
                suggested_sector=selected_sector or "Technology, SaaS & IT",
                market_complexity="Standard Commercial",
                fit_points=3,
                rationale="Standard industry vertical alignment."
            )

        n_lower = raw.lower()

        # High-Margin Enterprise Niches
        high_value_keywords = [
            "oilfield", "solar", "renewable", "subsea", "pipeline", "aerospace",
            "finops", "devops", "cloud infrastructure", "cybersecurity", "autonomous",
            "medical device", "biopharma", "semiconductor", "enterprise erp", "cold chain",
            "freight logistics", "industrial automation", "robotics", "cleantech"
        ]

        for kw in high_value_keywords:
            if kw in n_lower:
                return NicheAIAnalysis(
                    raw_niche=raw,
                    suggested_sector=selected_sector or "Enterprise & Industrial",
                    market_complexity="High-Margin Enterprise",
                    fit_points=5,
                    rationale=f"High-margin specialized enterprise market niche detected: '{raw}'."
                )

        return NicheAIAnalysis(
            raw_niche=raw,
            suggested_sector=selected_sector or "Commercial B2B",
            market_complexity="Mid-Market Specialized",
            fit_points=3,
            rationale=f"Established B2B market sector: '{raw}'."
        )

    @classmethod
    def analyze_intent(cls, intent_input: str) -> IntentAIAnalysis:
        """
        AI analysis of buying intent notes or signals.
        """
        raw = intent_input.strip()
        t_lower = raw.lower()

        signals = []
        timeline = None

        if any(w in t_lower for w in ["demo", "callback", "rfp", "immediate", "urgent", "asap", "q1", "q2", "q3", "q4", "next month", "scheduled"]):
            signals.append("Active buying cycle / scheduled executive interaction")
            if "demo" in t_lower or "callback" in t_lower or "+5" in t_lower:
                return IntentAIAnalysis(
                    raw_intent=raw,
                    urgency_tier="Immediate Active Buying (+5)",
                    intent_points=5,
                    timeline_detected="< 30 Days (Active Buying)",
                    extracted_signals=signals,
                    rationale="Urgent commercial intent with direct procurement/evaluation engagement."
                )

        if any(w in t_lower for w in ["pricing", "quote", "cost", "proposal", "budget", "commercial inquiry", "+3"]):
            signals.append("Active commercial pricing inquiry")
            return IntentAIAnalysis(
                raw_intent=raw,
                urgency_tier="Active Evaluation (+3)",
                intent_points=3,
                timeline_detected="30 - 60 Days",
                extracted_signals=signals,
                rationale="Prospect is actively reviewing commercial terms and budgetary line items."
            )

        return IntentAIAnalysis(
            raw_intent=raw,
            urgency_tier="Top-of-Funnel / Browsing (+1)",
            intent_points=1,
            timeline_detected="60+ Days (Exploratory)",
            extracted_signals=["Top-of-funnel information gathering"],
            rationale="Exploratory research phase; requires value-add discovery nurturing."
        )

    @classmethod
    def analyze_tech_stack(cls, stack_notes: str) -> TechStackAIAnalysis:
        """
        AI analysis of raw tech stack notes to identify synergies or legacy friction.
        """
        raw = stack_notes.strip()
        if not raw:
            return TechStackAIAnalysis(
                raw_stack="Unspecified",
                modern_tools=[],
                legacy_blockers=[],
                ecosystem_fit="Standard Cloud Baseline (+3)",
                tech_points=3,
                rationale="Baseline technology profile; zero known integration blockers."
            )

        t_lower = raw.lower()
        modern = []
        legacy = []

        for kw, desc in cls.MODERN_ECOSYSTEM_KEYWORDS.items():
            if kw.lower() in t_lower:
                modern.append(f"{kw} ({desc})")

        for kw, desc in cls.LEGACY_BLOCKER_KEYWORDS.items():
            if kw.lower() in t_lower:
                legacy.append(f"{kw} ({desc})")

        if legacy:
            return TechStackAIAnalysis(
                raw_stack=raw,
                modern_tools=modern,
                legacy_blockers=legacy,
                ecosystem_fit="Legacy Migration Friction (-1)",
                tech_points=-1,
                rationale=f"Detected legacy architecture ({', '.join(legacy)}) which may require migration support."
            )

        if len(modern) >= 2:
            return TechStackAIAnalysis(
                raw_stack=raw,
                modern_tools=modern,
                legacy_blockers=[],
                ecosystem_fit="High Synergies & Native Ecosystem (+5)",
                tech_points=5,
                rationale=f"Strong integration synergy with existing modern stack: {', '.join(modern)}."
            )
        elif len(modern) == 1:
            return TechStackAIAnalysis(
                raw_stack=raw,
                modern_tools=modern,
                legacy_blockers=[],
                ecosystem_fit="Standard Modern Stack (+3)",
                tech_points=3,
                rationale=f"Compatible enterprise infrastructure detected ({modern[0]})."
            )

        return TechStackAIAnalysis(
            raw_stack=raw,
            modern_tools=[],
            legacy_blockers=[],
            ecosystem_fit="Standard Stack (+3)",
            tech_points=3,
            rationale="Custom or standard stack noted with no severe blockers."
        )
