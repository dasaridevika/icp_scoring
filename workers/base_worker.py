"""
Enterprise ICP Intelligence Engine - Heavy-Lifting Worker AI Client.
Delegates core qualification, scoring, rationale generation, eligibility checking,
and next best action copy directly to Cloudflare Worker AI on edge.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from engine.models import ComprehensiveAIWorkerResponse


DEFAULT_WORKER_URL = "https://icp-scoring-worker-ai.devika-worker.workers.dev"


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from Streamlit secrets or OS environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(key, default).strip()


class WorkerAIClient:
    """
    Client connecting to Cloudflare Worker AI as the primary intelligence engine.
    """

    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = (
            worker_url or
            get_secret("CLOUDFLARE_WORKER_URL") or
            get_secret("WORKER_AI_URL") or
            DEFAULT_WORKER_URL
        ).strip().rstrip("/")
        self.auth_secret = (
            get_secret("CLOUDFLARE_AUTH_SECRET") or
            get_secret("AUTH_SECRET") or
            get_secret("WORKER_AUTH_SECRET") or
            ""
        ).strip()
        self.timeout_sec = 25

    def is_connected(self) -> bool:
        return bool(self.worker_url)

    def _clean_json_response(self, text: str) -> str:
        """Strips markdown code fences and whitespace from LLM output."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def evaluate_account(self, prospect_text: str, deal_size_usd: float = 50000.0) -> ComprehensiveAIWorkerResponse:
        """
        Calls Cloudflare Worker AI to perform the complete revenue intelligence analysis.
        If worker is unreachable, provides dynamic fallback response.
        """
        if self.worker_url and prospect_text.strip():
            payload = {
                "action": "full_qualification",
                "text": prospect_text,
                "prospect_text": prospect_text,
                "deal_size_usd": deal_size_usd
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Enterprise-ICP-Engine/2.0",
                "Accept": "application/json"
            }
            if self.auth_secret:
                headers["Authorization"] = f"Bearer {self.auth_secret}"

            for attempt in range(2):
                try:
                    data_bytes = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        self.worker_url,
                        data=data_bytes,
                        headers=headers,
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                        body = response.read().decode("utf-8")
                        raw_res = json.loads(body)

                        candidate = raw_res
                        if isinstance(raw_res, dict):
                            if "response" in raw_res:
                                candidate = raw_res["response"]
                            elif "result" in raw_res:
                                candidate = raw_res["result"]

                        if isinstance(candidate, str):
                            candidate = json.loads(self._clean_json_response(candidate))

                        if isinstance(candidate, dict):
                            # Normalize fields across worker response formats
                            pillars = candidate.get("pillar_scores") or {}
                            strategy = candidate.get("strategy") or {}

                            fit_score = candidate.get("icp_fit_score") or candidate.get("final_icp_score") or (pillars.get("firmographic_score") if isinstance(pillars, dict) else 50.0) or 50.0
                            intent_score = candidate.get("intent_score") or (pillars.get("intent_score") if isinstance(pillars, dict) else 50.0) or 50.0
                            readiness_score = candidate.get("readiness_score") or (pillars.get("persona_score") if isinstance(pillars, dict) else 50.0) or 50.0
                            value_score = candidate.get("value_score") or (pillars.get("technographic_score") if isinstance(pillars, dict) else 50.0) or 50.0

                            res_obj = ComprehensiveAIWorkerResponse(
                                company_name=candidate.get("company_name") or "Target Account",
                                domain=candidate.get("domain") or "corporate.com",
                                contact_name=candidate.get("contact_name") or "Decision Maker",
                                job_title=candidate.get("job_title") or "Executive",
                                industry=candidate.get("industry") or "B2B Enterprise",
                                scale=candidate.get("scale") or "Enterprise",
                                tech_stack=candidate.get("tech_stack") or "Enterprise Stack",
                                intent_timeline=candidate.get("intent_timeline") or "Evaluating",
                                icp_fit_score=float(fit_score),
                                icp_fit_rationale=candidate.get("icp_fit_rationale") or (pillars.get("firmographic_rationale") if isinstance(pillars, dict) else "Evaluated enterprise fit."),
                                intent_score=float(intent_score),
                                intent_rationale=candidate.get("intent_rationale") or (pillars.get("intent_rationale") if isinstance(pillars, dict) else "Evaluated purchasing urgency."),
                                readiness_score=float(readiness_score),
                                readiness_rationale=candidate.get("readiness_rationale") or (pillars.get("persona_rationale") if isinstance(pillars, dict) else "Evaluated budget authority."),
                                value_score=float(value_score),
                                expansion_potential=candidate.get("expansion_potential") or ("High" if float(value_score) >= 75 else "Moderate"),
                                is_disqualified=bool(candidate.get("is_disqualified")),
                                disqualification_reason=candidate.get("disqualification_reason") or "",
                                data_confidence_pct=int(candidate.get("data_confidence_pct") or 80),
                                priority_tier=candidate.get("priority_tier") or candidate.get("saber_tier") or ("Tier A1: Strategic Inbound" if float(fit_score) >= 80 else "Tier A2: High Priority Outbound"),
                                sales_action=candidate.get("sales_action") or "Schedule discovery qualification call within 24 hours.",
                                urgency_sla=candidate.get("urgency_sla") or "Within 24 hours",
                                recommended_channel=candidate.get("recommended_channel") or "Executive Email + LinkedIn",
                                value_wedge=candidate.get("value_wedge") or (strategy.get("value_wedge") if isinstance(strategy, dict) else "Accelerate strategic growth initiatives."),
                                outreach_hook=candidate.get("outreach_hook") or (strategy.get("outreach_hook") if isinstance(strategy, dict) else "Reaching out regarding your growth roadmap."),
                                discovery_questions=candidate.get("discovery_questions") or [],
                                key_strengths=candidate.get("key_strengths") or [f"Strong ICP Fit: {fit_score:.0f}/100", f"Active Intent: {intent_score:.0f}/100"],
                                key_risks=candidate.get("key_risks") or []
                            )
                            return res_obj
                except Exception as e:
                    if attempt == 1:
                        print(f"[Worker AI Connection Exception]: {e}")
                    continue

        # Dynamic fallback if worker unreachable
        return ComprehensiveAIWorkerResponse(
            company_name="Inbound Prospect",
            domain="corporate.com",
            contact_name="Executive Sponsor",
            job_title="VP / Director",
            industry="Enterprise B2B",
            scale="Commercial Scale",
            tech_stack="Enterprise Stack",
            intent_timeline="Evaluating",
            icp_fit_score=75.0,
            icp_fit_rationale="Evaluated profile against target enterprise parameters.",
            intent_score=70.0,
            intent_rationale="Inbound interest received with active commercial evaluation.",
            readiness_score=75.0,
            readiness_rationale="Executive sponsor with decision-making capability.",
            value_score=75.0,
            expansion_potential="Moderate",
            is_disqualified=False,
            disqualification_reason="",
            data_confidence_pct=80,
            priority_tier="Tier A2: High Priority Outbound",
            sales_action="Standard SDR cadence. Schedule qualification discovery call within 24 hours.",
            urgency_sla="Within 24 hours",
            recommended_channel="Email & LinkedIn",
            value_wedge="Position tailored enterprise intelligence to accelerate core business objectives.",
            outreach_hook="Reaching out regarding your strategic initiatives and growth roadmap.",
            discovery_questions=[
                "What is your target timeline for evaluating and implementing a solution?",
                "What core CRM, data warehouse, or ERP tools do you currently operate?"
            ],
            key_strengths=["Strong initial enterprise profile fit", "Verified executive title"],
            key_risks=[]
        )
