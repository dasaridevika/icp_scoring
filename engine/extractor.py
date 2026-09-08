"""
Step 1: Prospect Characteristics Extractor & Uncertainty Detector.
Implements GTM Partners' -1 Uncertainty Baseline & Sales Discovery Gap Analysis.
"""

import re
from typing import Dict, Any, Optional
from .models import ExtractedProspectData


class ProspectExtractor:
    """
    Extracts structured ICP characteristics from prospect text or AI payload,
    detects uncertain/missing fields, and generates targeted sales discovery questions.
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
        text_lower = text.lower()

        # 1. Company Name
        company = data.get("company_name")
        if not company or company in ["Target Account", "Target Prospect", "Account"]:
            company = cls._extract_field(text, ["company:", "company name:", "account:", "organization:"])
            if not company and text.splitlines():
                first_line = text.splitlines()[0].strip()
                if ":" not in first_line and 2 < len(first_line) < 60:
                    company = first_line
        company = company or "Unspecified Company"

        # 2. Contact Name & Parenthesized Title Extraction
        contact = data.get("contact_name")
        parenthesized_title = ""
        raw_contact_line = cls._extract_field(text, ["contact:", "name:", "lead name:", "decision maker:"])
        if raw_contact_line and "(" in raw_contact_line and ")" in raw_contact_line:
            parenthesized_title = raw_contact_line[raw_contact_line.find("(")+1 : raw_contact_line.find(")")].strip()
            contact = raw_contact_line.split("(")[0].strip()
        elif raw_contact_line:
            contact = raw_contact_line.strip()

        contact = contact or "Unspecified Contact"

        # 3. Job Title
        job_title = data.get("job_title")
        if not job_title or job_title in ["Executive", "Unknown"]:
            job_title = cls._extract_field(text, ["title:", "job title:", "role:", "designation:"]) or parenthesized_title
        job_title = job_title or "Unspecified Title"

        # 4. Industry
        industry = data.get("industry")
        if not industry or industry in ["Enterprise B2B", "B2B"]:
            industry = cls._extract_field(text, ["industry:", "vertical:", "sector:"])
        industry = industry or "Unspecified Industry"

        # 5. Scale / Revenue
        scale_revenue = ""
        for line in text.splitlines():
            line_l = line.lower()
            if any(k in line_l for k in ["arr", "revenue", "employees", "headcount", "scale", "$"]):
                scale_revenue = line.strip()
                break
        if not scale_revenue:
            scale_revenue = "Unspecified Scale (Need Discovery)"

        # 6. Technographics
        techno = ""
        techno_keywords = ["salesforce", "hubspot", "sap", "oracle", "snowflake", "aws", "gcp", "azure", "tableau", "powerbi", "postgres"]
        found_tech = [t.capitalize() for t in techno_keywords if t in text_lower]
        if found_tech:
            techno = ", ".join(found_tech)
        else:
            techno = "Unspecified Tech Stack (Need Discovery)"

        # 7. Intent / Urgency
        intent = ""
        for line in text.splitlines():
            line_l = line.lower()
            if any(k in line_l for k in ["rfp", "timeline", "inquiry", "quarter", "q1", "q2", "q3", "q4", "weeks", "months", "budget", "capex"]):
                intent = line.strip()
                break
        if not intent:
            intent = "Unspecified Timeline (Need Discovery)"

        # Determine Verified vs. Uncertain / Missing Fields
        verified = []
        uncertain = []
        discovery_questions = []

        # Check Company
        if company != "Unspecified Company":
            verified.append("Company Identity")
        else:
            uncertain.append("Company Identity")
            discovery_questions.append("What is the legal name and website of your organization?")

        # Check Persona
        if contact != "Unspecified Contact" and job_title != "Unspecified Title":
            verified.append("Decision Maker Persona")
        else:
            uncertain.append("Decision Maker Persona")
            discovery_questions.append("Who is the primary project lead, and what other executives are involved in budget sign-off?")

        # Check Industry
        if industry != "Unspecified Industry":
            verified.append("Industry & Vertical")
        else:
            uncertain.append("Industry & Vertical")
            discovery_questions.append("Which core industry vertical or sub-sector does your company operate within?")

        # Check Scale
        if "Unspecified" not in scale_revenue:
            verified.append("Company Scale / Revenue")
        else:
            uncertain.append("Company Scale / Revenue")
            discovery_questions.append("What is your current company scale in terms of total employee count and annual revenue (ARR)?")

        # Check Tech
        if "Unspecified" not in techno:
            verified.append("Technographic Infrastructure")
        else:
            uncertain.append("Technographic Infrastructure")
            discovery_questions.append("What CRM, ERP, and data analytics tools does your team currently integrate with?")

        # Check Intent
        if "Unspecified" not in intent:
            verified.append("Intent & Project Timeline")
        else:
            uncertain.append("Intent & Project Timeline")
            discovery_questions.append("What is your expected timeline and key milestone deadlines for this evaluation?")

        # Confidence Score calculation
        total_possible = len(cls.CORE_ATTRIBUTES)
        confidence_score = round((len(verified) / total_possible) * 100)

        return ExtractedProspectData(
            company_name=company,
            contact_name=contact,
            job_title=job_title,
            industry=industry,
            scale_revenue=scale_revenue,
            technographics=techno,
            intent_urgency=intent,
            verified_fields=verified,
            uncertain_fields=uncertain,
            confidence_score=confidence_score,
            discovery_questions=discovery_questions,
            raw_text=text,
            raw_ai_payload=data
        )

    @staticmethod
    def _extract_field(text: str, prefixes: list[str]) -> Optional[str]:
        for line in text.splitlines():
            clean = line.strip()
            for prefix in prefixes:
                if clean.lower().startswith(prefix):
                    val = clean.split(":", 1)[1].strip()
                    if val:
                        return val
        return None
