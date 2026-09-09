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
                            ratings = candidate.get("ratings") or {}
                            rationales = candidate.get("rationales") or {}
                            strategy = candidate.get("strategy") or {}
                            pillars = candidate.get("pillar_scores") or {}

                            # Convert GTM ratings (-5..+5) to 0-100 scores
                            def rating_to_score(r):
                                try:
                                    num = float(r)
                                    return max(0.0, min(100.0, (num + 5.0) * 10.0))
                                except Exception:
                                    return 40.0

                            f_rating = ratings.get("firmographic")
                            t_rating = ratings.get("technographic")
                            i_rating = ratings.get("intent")
                            p_rating = ratings.get("persona")

                            fit_score = candidate.get("icp_fit_score") or candidate.get("final_icp_score")
                            if fit_score is None and f_rating is not None:
                                fit_score = rating_to_score(f_rating)
                            elif fit_score is None:
                                fit_score = pillars.get("firmographic_score", 0.0)

                            intent_score = rating_to_score(i_rating) if i_rating is not None else candidate.get("intent_score", pillars.get("intent_score", 0.0))
                            readiness_score = rating_to_score(p_rating) if p_rating is not None else candidate.get("readiness_score", pillars.get("persona_score", 0.0))
                            value_score = rating_to_score(t_rating) if t_rating is not None else candidate.get("value_score", pillars.get("technographic_score", 0.0))

                            # Calculate Data Confidence Percentage based on missing (-1) ratings
                            active_ratings = [f_rating, t_rating, i_rating, p_rating]
                            verified_count = sum(1 for r in active_ratings if r is not None and r != -1)
                            calc_confidence = int((verified_count / 4.0) * 100) if any(r is not None for r in active_ratings) else int(candidate.get("data_confidence_pct", 50))

                            is_disqualified = bool(candidate.get("is_disqualified")) or (p_rating == -5)
                            
                            # Determine Priority Tier dynamically
                            if is_disqualified:
                                priority_tier = "Disqualified / Anti-ICP"
                            elif float(fit_score) >= 80 and float(intent_score) >= 70:
                                priority_tier = "Tier A1: Strategic Inbound"
                            elif float(fit_score) >= 65:
                                priority_tier = "Tier A2: High Priority Outbound"
                            elif float(fit_score) >= 50:
                                priority_tier = "Tier B1: Nurture Pipeline"
                            else:
                                priority_tier = "Tier C: Low Priority / Long-Tail"

                            res_obj = ComprehensiveAIWorkerResponse(
                                company_name=candidate.get("company_name") or None,
                                domain=candidate.get("domain") or None,
                                contact_name=candidate.get("contact_name") or None,
                                job_title=candidate.get("job_title") or None,
                                industry=candidate.get("industry") or None,
                                scale=candidate.get("scale") or None,
                                tech_stack=candidate.get("tech_stack") or None,
                                intent_timeline=candidate.get("intent_timeline") or None,
                                icp_fit_score=float(fit_score or 0.0),
                                icp_fit_rationale=candidate.get("icp_fit_rationale") or rationales.get("firmographic") or "Evaluated firmographic fit.",
                                intent_score=float(intent_score or 0.0),
                                intent_rationale=candidate.get("intent_rationale") or rationales.get("intent") or "Evaluated intent signal.",
                                readiness_score=float(readiness_score or 0.0),
                                readiness_rationale=candidate.get("readiness_rationale") or rationales.get("persona") or "Evaluated buyer persona.",
                                value_score=float(value_score or 0.0),
                                expansion_potential=candidate.get("expansion_potential") or ("High" if float(value_score or 0) >= 75 else ("Moderate" if float(value_score or 0) >= 50 else "Low")),
                                is_disqualified=is_disqualified,
                                disqualification_reason=candidate.get("disqualification_reason") or ("Disqualified by role/anti-ICP rule" if is_disqualified else ""),
                                data_confidence_pct=calc_confidence,
                                priority_tier=candidate.get("priority_tier") or priority_tier,
                                sales_action=candidate.get("sales_action") or ("Disqualify or route to self-service." if is_disqualified else "Schedule discovery qualification call within 24 hours."),
                                urgency_sla=candidate.get("urgency_sla") or ("N/A" if is_disqualified else "Within 24 hours"),
                                recommended_channel=candidate.get("recommended_channel") or "Email + LinkedIn",
                                value_wedge=candidate.get("value_wedge") or (strategy.get("value_wedge") if isinstance(strategy, dict) else ""),
                                outreach_hook=candidate.get("outreach_hook") or (strategy.get("outreach_hook") if isinstance(strategy, dict) else ""),
                                discovery_questions=candidate.get("discovery_questions") or [],
                                key_strengths=candidate.get("key_strengths") or [],
                                key_risks=candidate.get("key_risks") or []
                            )
                            return res_obj
                except Exception as e:
                    if attempt == 1:
                        print(f"[Worker AI Connection Exception]: {e}")
                    continue

        # Unreachable fallback - surfaces status as unverified with 0 confidence
        return ComprehensiveAIWorkerResponse(
            company_name=None,
            domain=None,
            contact_name=None,
            job_title=None,
            industry=None,
            scale=None,
            tech_stack=None,
            intent_timeline=None,
            icp_fit_score=0.0,
            icp_fit_rationale="Worker AI offline or unreachable. Field marked as unverified.",
            intent_score=0.0,
            intent_rationale="Worker AI offline or unreachable. Field marked as unverified.",
            readiness_score=0.0,
            readiness_rationale="Worker AI offline or unreachable. Field marked as unverified.",
            value_score=0.0,
            expansion_potential="Uncertain",
            is_disqualified=False,
            disqualification_reason="",
            data_confidence_pct=0,
            priority_tier="Unverified Pipeline",
            sales_action="Check Cloudflare Worker AI connection or inspect wrangler logs.",
            urgency_sla="N/A",
            recommended_channel="Email",
            value_wedge="",
            outreach_hook="",
            discovery_questions=[
                "What is the official operating company name and target industry?",
                "What is your target timeline for evaluating and deploying a solution?"
            ],
            key_strengths=[],
            key_risks=["Worker AI offline or unreachable - manual review required."]
        )
