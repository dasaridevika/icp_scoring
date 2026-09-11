"""
Enterprise ICP Intelligence Engine - Pure Python Evidence & Signal Extractor.
100% Deterministic & Self-Contained. Extracts entity details, classifies evidence
status (VERIFIED, INFERRED, UNKNOWN), detects anti-ICP triggers, and generates
bespoke sales enablement copy without requiring external AI workers or network APIs.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .models import EvidenceStatus, EvidencePillar


class LeadEvidenceExtractor:
    """
    Extracts structured revenue intelligence directly from raw text, emails,
    form submissions, or webhook payloads in pure Python.
    """

    PHONE_COUNTRY_MAP = {
        "+971": "United Arab Emirates (UAE)",
        "+1": "United States / Canada",
        "+44": "United Kingdom",
        "+91": "India",
        "+49": "Germany",
        "+33": "France",
        "+61": "Australia",
        "+65": "Singapore",
        "+81": "Japan",
        "+41": "Switzerland",
        "+31": "Netherlands",
        "+966": "Saudi Arabia",
        "+974": "Qatar",
        "+965": "Kuwait"
    }

    TECH_KEYWORDS = [
        "Snowflake", "Salesforce", "AWS", "Databricks", "HubSpot", "Outreach",
        "GCP", "Google Cloud", "Azure", "Kubernetes", "Segment", "PostgreSQL",
        "SAP", "Oracle", "Workday", "Stripe", "Marketo", "Zendesk", "Mixpanel",
        "BigQuery", "Redshift", "Docker", "Kafka", "Tableau", "PowerBI"
    ]

    DISPOSABLE_DOMAINS = {
        "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com",
        "outlook.com", "live.com", "msn.com", "icloud.com", "protonmail.com",
        "proton.me", "pm.me", "mail.ru", "163.com", "tempmail.com", "mailinator.com",
        "yopmail.com", "guerrillamail.com", "10minutemail.com"
    }

    FORM_HOST_DOMAINS = {
        "typeform.com", "calendly.com", "hubspot.com", "zoom.us", "linkedin.com",
        "github.com", "google.com", "youtube.com", "twitter.com", "x.com"
    }

    @classmethod
    def clean_str(cls, val: Optional[str]) -> Optional[str]:
        if not val:
            return None
        s = str(val).strip()
        if s.lower() in ("null", "none", "undefined", "n/a", "", "unspecified"):
            return None
        return s

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts structured entities from prospect lead text."""
        t = text.strip()

        # 1. Email Extraction
        email_match = re.search(r'[\w\.-]+@([\w\.-]+\.[a-zA-Z]{2,})', t)
        email = email_match.group(0) if email_match else None
        email_domain = email_match.group(1).lower() if email_match else None

        # Determine domain (ignoring freemail or generic host domains)
        domain = None
        if email_domain and email_domain not in cls.DISPOSABLE_DOMAINS and email_domain not in cls.FORM_HOST_DOMAINS:
            domain = email_domain
        else:
            # Look for Website/Domain field
            web_match = re.search(r'(?:Website|Domain|Site|URL|Web)[:\s]+(?:https?:\/\/)?([a-zA-Z0-9\.-]+\.[a-zA-Z]{2,})', t, re.IGNORECASE)
            if web_match:
                cand = web_match.group(1).lower().replace("www.", "")
                if cand not in cls.FORM_HOST_DOMAINS:
                    domain = cand

        # 2. Company Name
        company_name = None
        comp_match = re.search(r'(?:Company|🏢|Account|Organization|Org)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if comp_match:
            company_name = comp_match.group(1).strip()
        elif "from " in t:
            from_match = re.search(r'from\s+([A-Z][A-Za-z0-9\s\.\,\&]+?)(?:\.|\,|\s+We|\s+I|\n|$)', t)
            if from_match:
                company_name = from_match.group(1).strip()

        if not company_name and domain:
            # Infer company from domain name (e.g. parvenoilfield.com -> Parvenoilfield)
            company_name = domain.split('.')[0].replace("-", " ").title()

        # 3. Contact Name
        contact_name = None
        name_match = re.search(r'(?:Name|👤|Contact|Lead)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if name_match:
            contact_name = name_match.group(1).strip()
        else:
            greet_match = re.search(r'(?:My name is|I am|I\'m|This is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', t)
            if greet_match:
                contact_name = greet_match.group(1).strip()

        # 4. Job Title & Seniority
        job_title = None
        title_match = re.search(r'(?:Title|Role|Position|Job)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if title_match:
            job_title = title_match.group(1).strip()
        else:
            # Check for embedded role patterns in text
            role_patterns = [
                r'((?:VP|Vice President|Director|Head|Chief|Lead|Manager|Senior Director|Architect|Procurement|Buyer)\s+of\s+[A-Za-z\s]+)',
                r'((?:Commercial Sales|Procurement|Revenue Operations|RevOps|Architecture|Engineering|Enterprise Sales|GTM)\s+(?:Leader|Director|Lead|Manager|Specialist|Representative)?)'
            ]
            for pat in role_patterns:
                rm = re.search(pat, t, re.IGNORECASE)
                if rm:
                    job_title = rm.group(1).strip().title()
                    break

        # 5. Location & Country
        location = None
        loc_match = re.search(r'(?:Location|Country|🌍|HQ|City|State|Region)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if loc_match:
            raw_loc = loc_match.group(1).strip()
            # Expand ISO codes (e.g. 'ae' -> 'United Arab Emirates (UAE)')
            if raw_loc.lower() == 'ae':
                location = "United Arab Emirates (UAE)"
            elif raw_loc.lower() == 'us' or raw_loc.lower() == 'usa':
                location = "United States"
            elif raw_loc.lower() == 'uk':
                location = "United Kingdom"
            elif raw_loc.lower() == 'in':
                location = "India"
            else:
                location = raw_loc

        # Check phone prefix if location not found
        if not location:
            for prefix, country_name in cls.PHONE_COUNTRY_MAP.items():
                if prefix in t:
                    location = country_name
                    break

        # Check timezone mentions
        if not location:
            tz_match = re.search(r'Timezone[:\s]+([^\n\r,]+)', t, re.IGNORECASE)
            if tz_match:
                tz = tz_match.group(1).strip()
                if "Kolkata" in tz or "IST" in tz:
                    location = "India / APAC"
                elif "Dubai" in tz or "GST" in tz:
                    location = "United Arab Emirates (UAE)"

        # 6. Scale & Headcount
        scale = None
        scale_match = re.search(r'(?:Scale|Headcount|Team Size|Size|Employees)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if scale_match:
            scale = scale_match.group(1).strip()
        else:
            num_emp_match = re.search(r'(\d+[\d,]*\+?\s*(?:employees|reps|people|staff|headcount))', t, re.IGNORECASE)
            arr_match = re.search(r'(\$\d+[\d,]*M?\s*(?:ARR|revenue|budget))', t, re.IGNORECASE)
            parts = []
            if num_emp_match:
                parts.append(num_emp_match.group(1))
            if arr_match:
                parts.append(arr_match.group(1))
            if parts:
                scale = ", ".join(parts)

        # 7. Tech Stack
        tech_found = []
        for kw in cls.TECH_KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', t, re.IGNORECASE):
                tech_found.append(kw)
        tech_stack = ", ".join(tech_found) if tech_found else None

        # 8. Industry
        industry = None
        ind_match = re.search(r'(?:Industry|Vertical|Sector)[:\s]+([^\n\r,\|]+)', t, re.IGNORECASE)
        if ind_match:
            industry = ind_match.group(1).strip()
        else:
            # Infer industry keywords
            ind_cues = {
                "Solar Energy & Renewable Infrastructure": ["solar", "renewable", "photovoltaic", "clean energy"],
                "Industrial Manufacturing & Oilfield": ["oilfield", "manufacturing", "industrial", "machinery", "fabrication"],
                "Enterprise Software & SaaS": ["saas", "software", "cloud platform", "analytics", "b2b platform"],
                "Financial Technology (FinTech)": ["fintech", "banking", "payments", "financial", "trading"],
                "Healthcare & Life Sciences": ["health", "medical", "hospital", "pharma", "biotech"],
                "E-Commerce & Retail": ["ecommerce", "retail", "marketplace", "dtc", "store"]
            }
            for ind_name, cues in ind_cues.items():
                if any(re.search(r'\b' + re.escape(c) + r'\b', t, re.IGNORECASE) for c in cues):
                    industry = ind_name
                    break

        # 9. Intent Timeline & Booking Signals
        intent_timeline = None
        time_match = re.search(r'(?:Date|Time|Schedule|Timeline|Deadline|When)[:\s]+([^\n\r\|]+)', t, re.IGNORECASE)
        callback_match = re.search(r'(callback request|meeting scheduled|scheduled.*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}-\d{2}-\d{2}))', t, re.IGNORECASE)
        q_match = re.search(r'(Q[1-4]|immediately|within \d+ weeks|end of this month|urgent|RFP)', t, re.IGNORECASE)

        if callback_match:
            intent_timeline = f"Immediate Callback / Meeting ({callback_match.group(0)})"
        elif time_match:
            intent_timeline = f"Scheduled Timeline ({time_match.group(1).strip()})"
        elif q_match:
            intent_timeline = f"Active Buying Initiative ({q_match.group(1)})"

        return {
            "company_name": cls.clean_str(company_name),
            "domain": cls.clean_str(domain),
            "contact_name": cls.clean_str(contact_name),
            "job_title": cls.clean_str(job_title),
            "industry": cls.clean_str(industry),
            "location": cls.clean_str(location),
            "scale": cls.clean_str(scale),
            "tech_stack": cls.clean_str(tech_stack),
            "intent_timeline": cls.clean_str(intent_timeline),
            "raw_email": email,
            "email_domain": email_domain
        }

    @classmethod
    def evaluate_evidence(cls, text: str, entities: Dict[str, Any], deal_size_usd: float = 50000.0) -> Dict[str, Any]:
        """Evaluates 5-pillar structured evidence and copywriting."""
        t = text.lower()
        email_dom = entities.get("email_domain") or ""
        is_freemail = email_dom in cls.DISPOSABLE_DOMAINS or "gmail.com" in email_dom or "yahoo.com" in email_dom
        is_personal_query = any(k in t for k in ["personal blog", "affiliate marketing", "my personal website", "student", "freelance project"])

        # Check Disqualification
        is_disqualified = False
        disq_reason = ""
        if is_freemail and is_personal_query:
            is_disqualified = True
            disq_reason = f"Non-commercial / Personal email domain detected (@{email_dom}). Enterprise qualification requires corporate business email domain."
        elif is_freemail and not entities.get("company_name"):
            is_disqualified = True
            disq_reason = f"Personal freemail address (@{email_dom}) provided without corporate company verification."

        # 1. Firmographic Pillar
        firmo_points = []
        firmo_missing = []
        if is_disqualified:
            firmo = EvidencePillar(score=0.0, status=EvidenceStatus.KNOWN_NEGATIVE, confidence=0.90, rationale="Personal / non-commercial profile outside B2B firmographics.", evidence_points=["Personal lead detected."])
        elif entities.get("scale"):
            firmo_points.append(f"Verified scale: {entities['scale']}")
            if entities.get("industry"):
                firmo_points.append(f"Industry: {entities['industry']}")
            firmo = EvidencePillar(score=85.0, status=EvidenceStatus.VERIFIED, confidence=0.88, rationale="Verified firmographic headcount and enterprise operational scale.", evidence_points=firmo_points)
        elif entities.get("domain") and entities.get("company_name"):
            firmo_points.append(f"Established B2B enterprise: {entities['company_name']} ({entities['domain']})")
            if entities.get("industry"):
                firmo_points.append(f"Industry: {entities['industry']}")
            firmo = EvidencePillar(score=68.0, status=EvidenceStatus.INFERRED, confidence=0.75, rationale="Established corporate business domain and recognized industry alignment.", evidence_points=firmo_points, missing_points=["Specific employee headcount verification needed."])
        else:
            firmo = EvidencePillar(score=None, status=EvidenceStatus.UNKNOWN, confidence=0.0, rationale="Missing corporate company and domain evidence.", missing_points=["Company name", "Headcount"])

        # 2. Technographic Pillar
        techno_points = []
        if is_disqualified:
            techno = EvidencePillar(score=0.0, status=EvidenceStatus.KNOWN_NEGATIVE, confidence=0.90, rationale="No enterprise software stack present.")
        elif entities.get("tech_stack"):
            techno_points.append(f"Active infrastructure: {entities['tech_stack']}")
            techno = EvidencePillar(score=85.0, status=EvidenceStatus.VERIFIED, confidence=0.85, rationale=f"Modern enterprise data infrastructure: {entities['tech_stack']}.", evidence_points=techno_points)
        elif entities.get("domain"):
            techno = EvidencePillar(score=60.0, status=EvidenceStatus.INFERRED, confidence=0.65, rationale="Standard cloud/enterprise infrastructure inferred for commercial domain.", evidence_points=["Commercial domain active"], missing_points=["Specific cloud warehouse & CRM stack"])
        else:
            techno = EvidencePillar(score=None, status=EvidenceStatus.UNKNOWN, confidence=0.0, rationale="No technographic stack data provided.", missing_points=["CRM / Data warehouse stack"])

        # 3. Intent & Timing Pillar
        intent_points = []
        if is_disqualified:
            intent = EvidencePillar(score=0.0, status=EvidenceStatus.KNOWN_NEGATIVE, confidence=0.90, rationale="Zero enterprise commercial buying intent.")
        elif "callback" in t or "scheduled" in t or "time:" in t or "date:" in t:
            intent_points.append("Direct inbound callback request with scheduled calendar appointment.")
            if entities.get("intent_timeline"):
                intent_points.append(entities["intent_timeline"])
            intent = EvidencePillar(score=95.0, status=EvidenceStatus.VERIFIED, confidence=0.95, rationale="Immediate commercial urgency with confirmed callback/meeting request.", evidence_points=intent_points)
        elif any(k in t for k in ["rfp", "q3", "q4", "budget allocated", "evaluating vendors", "3 weeks", "month"]):
            intent_points.append("Active evaluation timeline or designated procurement window.")
            intent = EvidencePillar(score=85.0, status=EvidenceStatus.VERIFIED, confidence=0.85, rationale="Active commercial procurement timeline and stated buying milestone.", evidence_points=intent_points)
        elif any(k in t for k in ["interested", "pricing", "demo", "learn more", "discuss"]):
            intent_points.append("Inbound product inquiry requesting discussion.")
            intent = EvidencePillar(score=75.0, status=EvidenceStatus.INFERRED, confidence=0.75, rationale="Inbound product inquiry requesting commercial discovery call.", evidence_points=intent_points)
        else:
            intent = EvidencePillar(score=None, status=EvidenceStatus.UNKNOWN, confidence=0.0, rationale="No active buying timeline or urgency indicated.", missing_points=["Project timeline", "Budget allocation"])

        # 4. Readiness & Authority Pillar
        readiness_points = []
        if is_disqualified:
            readiness = EvidencePillar(score=0.0, status=EvidenceStatus.KNOWN_NEGATIVE, confidence=0.90, rationale="No commercial budget or corporate decision authority.")
        elif entities.get("job_title"):
            title = entities["job_title"]
            if any(k in title.lower() for k in ["vp", "vice president", "director", "head", "chief", "executive"]):
                readiness_points.append(f"Executive decision-maker: {title}")
                readiness = EvidencePillar(score=90.0, status=EvidenceStatus.VERIFIED, confidence=0.90, rationale=f"High authority decision-maker with executive mandate ({title}).", evidence_points=readiness_points)
            else:
                readiness_points.append(f"Commercial stakeholder: {title}")
                readiness = EvidencePillar(score=70.0, status=EvidenceStatus.INFERRED, confidence=0.75, rationale=f"Commercial stakeholder with procurement representation ({title}).", evidence_points=readiness_points)
        elif entities.get("domain"):
            readiness = EvidencePillar(score=60.0, status=EvidenceStatus.INFERRED, confidence=0.65, rationale="Authenticated corporate business email domain.", evidence_points=["Corporate domain verified"], missing_points=["Specific buyer job title"])
        else:
            readiness = EvidencePillar(score=None, status=EvidenceStatus.UNKNOWN, confidence=0.0, rationale="Missing decision maker authority evidence.", missing_points=["Job title / Authority level"])

        # 5. Commercial Value Pillar
        if is_disqualified:
            value = EvidencePillar(score=0.0, status=EvidenceStatus.KNOWN_NEGATIVE, confidence=0.90, rationale="Non-commercial lead with zero enterprise contract value.")
        elif deal_size_usd >= 100000 or (entities.get("scale") and "ARR" in entities.get("scale", "")):
            value = EvidencePillar(score=85.0, status=EvidenceStatus.VERIFIED, confidence=0.85, rationale=f"High enterprise contract expansion opportunity (${deal_size_usd:,.0f}).", evidence_points=[f"Target deal size: ${deal_size_usd:,.0f}"])
        elif entities.get("domain") or entities.get("company_name"):
            value = EvidencePillar(score=65.0, status=EvidenceStatus.INFERRED, confidence=0.75, rationale=f"Mid-market commercial opportunity with recurring expansion potential (${deal_size_usd:,.0f}).", evidence_points=[f"Target contract size: ${deal_size_usd:,.0f}"])
        else:
            value = EvidencePillar(score=None, status=EvidenceStatus.UNKNOWN, confidence=0.0, rationale="Unspecified commercial contract scale.", missing_points=["Contract size / Budget"])

        # Copywriting Strategy
        contact_name = entities.get("contact_name") or "there"
        company_name = entities.get("company_name") or "your team"
        industry_name = entities.get("industry") or "enterprise growth"
        first_name = contact_name.split()[0] if contact_name != "there" else "there"

        # Bespoke Cold Outreach Opener
        if is_disqualified:
            outreach_hook = f"Hi {first_name}, thank you for reaching out regarding our platform."
            val_wedge = "Self-service resources and documentation for individual users."
        elif entities.get("intent_timeline") and "callback" in str(entities.get("intent_timeline")).lower():
            outreach_hook = f"Hi {first_name}, following up on your callback request regarding {company_name}'s {industry_name} initiatives—I'd be glad to share how our platform integrates with your infrastructure ahead of our discussion."
            val_wedge = f"Deliver scalable revenue intelligence and automated workflow analytics to accelerate {company_name}'s market expansion."
        elif entities.get("tech_stack"):
            outreach_hook = f"Hi {first_name}, with {company_name} utilizing {entities['tech_stack']}, I wanted to share how we integrate directly to eliminate pipeline data silos without workflow disruption."
            val_wedge = f"Consolidate revenue data pipelines and accelerate operational forecasting for {company_name}'s revenue team."
        else:
            outreach_hook = f"Hi {first_name}, with {company_name} actively expanding in {industry_name}, I wanted to share how our intelligence platform can help streamline operations and improve forecasting accuracy."
            val_wedge = f"Drive scalable operational efficiency and predictable revenue growth across {company_name}'s organization."

        # Key Strengths
        key_strengths = []
        if entities.get("company_name"):
            key_strengths.append(f"Established B2B enterprise: {entities['company_name']}")
        if entities.get("industry"):
            key_strengths.append(f"Aligned industry vertical: {entities['industry']}")
        if entities.get("location"):
            key_strengths.append(f"Operating geography: {entities['location']}")
        if entities.get("tech_stack"):
            key_strengths.append(f"Compatible tech stack: {entities['tech_stack']}")
        if entities.get("intent_timeline"):
            key_strengths.append(f"Active timing signal: {entities['intent_timeline']}")

        # Key Risks
        key_risks = []
        if is_disqualified:
            key_risks.append(f"Hard Disqualification: {disq_reason}")
        if not entities.get("scale"):
            key_risks.append("Employee headcount & ARR scale unverified; requires discovery validation.")
        if not entities.get("tech_stack"):
            key_risks.append("Current tech stack and CRM infrastructure not explicitly stated.")
        if not entities.get("job_title"):
            key_risks.append("Decision maker buying authority not confirmed.")

        # Discovery Questions
        discovery_questions = []
        if not entities.get("scale"):
            discovery_questions.append(f"What is the current team size and operational scale at {company_name}?")
        if not entities.get("tech_stack"):
            discovery_questions.append(f"What CRM and data analytics tools is {company_name} currently using?")
        if entities.get("industry"):
            discovery_questions.append(f"What are the primary challenges your team is encountering with your {entities['industry']} roadmap?")
        else:
            discovery_questions.append(f"What are the top operational priorities for {company_name} over the next two quarters?")

        return {
            "account": {
                "company_name": entities.get("company_name"),
                "domain": entities.get("domain"),
                "contact_name": entities.get("contact_name"),
                "job_title": entities.get("job_title"),
                "industry": entities.get("industry"),
                "location": entities.get("location"),
                "scale": entities.get("scale"),
                "tech_stack": entities.get("tech_stack"),
                "intent_timeline": entities.get("intent_timeline")
            },
            "evidence": {
                "firmographic": firmo,
                "technographic": techno,
                "intent": intent,
                "readiness": readiness,
                "value": value
            },
            "is_disqualified": is_disqualified,
            "disqualification_reason": disq_reason,
            "strategy": {
                "value_wedge": val_wedge,
                "outreach_hook": outreach_hook
            },
            "discovery_questions": discovery_questions[:3],
            "key_strengths": key_strengths[:4],
            "key_risks": key_risks[:3]
        }

    @classmethod
    def extract_and_parse(cls, prospect_text: str, deal_size_usd: float = 50000.0) -> Dict[str, Any]:
        """End-to-end extraction pipeline from raw text."""
        entities = cls.extract_entities(prospect_text)
        return cls.evaluate_evidence(prospect_text, entities, deal_size_usd)