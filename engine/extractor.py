"""
Step 1: Dynamic Prospect Characteristics Extractor & Uncertainty Detector.
100% Dynamic - Zero Hardcoded Keyword Dictionaries.
Driven directly by semantic comprehension & AI payload.
"""

from typing import Dict, Any, Optional
from .models import ExtractedProspectData


class ProspectExtractor:
    """
    Dynamically extracts structured ICP characteristics from prospect AI payload and raw context.
    Eliminates all hardcoded keyword dictionaries.
    """

    CORE_ATTRIBUTES = [
        "Company Identity",
        "Decision Maker Persona",
        "Industry & Vertical",
        "Company Scale / Revenue",
        "Technographic Infrastructure",
        "Intent & Project Timeline"
    ]

    @classmethod
    def extract(
        cls,
        raw_text: str = "",
        ai_data: Optional[Dict[str, Any]] = None
    ) -> ExtractedProspectData:
        data = ai_data or {}
        text = raw_text.strip()

        # 1. Dynamic Extraction from AI Payload
        company = data.get("company_name")
        if not company or company in ["Target Account", "Target Prospect", "Account"]:
            # Fallback: take the first concise line of user input if clean
            first_line = text.splitlines()[0].strip() if text.splitlines() else ""
            if first_line and len(first_line) < 60 and not any(p in first_line.lower() for p in ["http", "inquiry", "hi ", "hello"]):
                company = first_line.split(":")[-1].strip() if ":" in first_line else first_line
            else:
                company = "Unspecified Company"

        contact = data.get("contact_name")
        if not contact or contact in ["Decision Maker", "Contact"]:
            contact = "Unspecified Contact"

        job_title = data.get("job_title")
        if not job_title or job_title in ["Executive", "Unknown"]:
            job_title = "Unspecified Title"

        industry = data.get("industry")
        if not industry or industry in ["Enterprise B2B", "B2B"]:
            industry = "Unspecified Industry"

        # 2. Extract Dynamic Pillar Insights & Rationales
        pillars = data.get("pillar_scores") or {}
        firmo_obj = pillars.get("firmographic") if isinstance(pillars.get("firmographic"), dict) else {}
        techno_obj = pillars.get("technographic") if isinstance(pillars.get("technographic"), dict) else {}
        intent_obj = pillars.get("intent") if isinstance(pillars.get("intent"), dict) else {}
        persona_obj = pillars.get("persona") if isinstance(pillars.get("persona"), dict) else {}

        firmo_rat = firmo_obj.get("rationale") or pillars.get("firmographic_rationale") or ""
        techno_rat = techno_obj.get("rationale") or pillars.get("technographic_rationale") or ""
        intent_rat = intent_obj.get("rationale") or pillars.get("intent_rationale") or ""
        persona_rat = persona_obj.get("rationale") or pillars.get("persona_rationale") or ""

        # 3. Dynamic Uncertainty & Gap-Filling Analysis
        verified = []
        uncertain = []
        discovery_questions = []

        # Company Identity
        if company != "Unspecified Company":
            verified.append("Company Identity")
        else:
            uncertain.append("Company Identity")
            discovery_questions.append("What is the official company name and primary operating website?")

        # Persona & Role
        if contact != "Unspecified Contact" and job_title != "Unspecified Title":
            verified.append("Decision Maker Persona")
        else:
            uncertain.append("Decision Maker Persona")
            discovery_questions.append("Who is the primary project sponsor, and what is their functional title and department?")

        # Industry & Vertical
        if industry != "Unspecified Industry":
            verified.append("Industry & Vertical")
        else:
            uncertain.append("Industry & Vertical")
            discovery_questions.append("Which core industry sector and target customer segment does your company operate within?")

        # Scale & Headcount
        if firmo_rat or "firmographic_score" in pillars or firmo_obj:
            verified.append("Company Scale / Revenue")
        else:
            uncertain.append("Company Scale / Revenue")
            discovery_questions.append("What is the current scale of your organization in terms of annual revenue (ARR) and total headcount?")

        # Technographic Stack
        if techno_rat or "technographic_score" in pillars or techno_obj:
            verified.append("Technographic Infrastructure")
        else:
            uncertain.append("Technographic Infrastructure")
            discovery_questions.append("What core CRM, data warehouse, and business software tools does your team currently integrate with?")

        # Intent & Timeline
        if intent_rat or "intent_score" in pillars or intent_obj:
            verified.append("Intent & Project Timeline")
        else:
            uncertain.append("Intent & Project Timeline")
            discovery_questions.append("What is your expected evaluation timeline and target implementation date for this initiative?")

        # Data Confidence Level
        total_attributes = len(cls.CORE_ATTRIBUTES)
        confidence_score = round((len(verified) / total_attributes) * 100)

        return ExtractedProspectData(
            company_name=company,
            contact_name=contact,
            job_title=job_title,
            industry=industry,
            scale_revenue=firmo_rat or "Dynamic Commercial Profile",
            technographics=techno_rat or "Dynamic Technology Stack",
            intent_urgency=intent_rat or "Dynamic Evaluation Timeline",
            verified_fields=verified,
            uncertain_fields=uncertain,
            confidence_score=confidence_score,
            discovery_questions=discovery_questions,
            raw_text=text,
            raw_ai_payload=data
        )
