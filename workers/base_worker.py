"""
Enterprise ICP Intelligence Engine - Worker AI Client.
Delegates evidence extraction to Cloudflare Worker AI on edge,
validates the response schema, and evaluates deterministic scores
via the centralized MasterScoringEngine.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from engine.models import (
    AccountAssessment,
    AssessmentMetadata,
    AccountInfo,
    ScoresBreakdown,
    ConfidenceBreakdown,
    EvidenceBreakdown,
    DecisionInfo,
    CommercialInfo,
    EvidencePillar,
    EvidenceStatus
)
from engine.config import active_config
from engine.scorer import MasterScoringEngine
from engine.extractor import ProspectExtractor


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from Streamlit secrets or OS environment (case-flexible)."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k, val in st.secrets.items():
                if k.lower() == key.lower():
                    clean_val = str(val).strip()
                    if clean_val:
                        return clean_val
    except Exception:
        pass
    for k, val in os.environ.items():
        if k.lower() == key.lower():
            return str(val).strip()
    return os.environ.get(key, default).strip()


class WorkerAIClient:
    """
    Client connecting to Cloudflare Worker AI for structured evidence extraction.
    Scores and decisions are deterministically computed by MasterScoringEngine.
    """

    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = (
            worker_url or
            get_secret("CLOUDFLARE_WORKER_URL") or
            get_secret("WORKER_URL") or
            get_secret("WORKER_AI_URL") or
            ""
        ).strip().rstrip("/")
        self.auth_secret = get_secret("CLOUDFLARE_AUTH_SECRET") or get_secret("AUTH_SECRET") or ""
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

    def evaluate_account(self, prospect_text: str, deal_size_usd: float = 50000.0) -> AccountAssessment:
        """
        Executes end-to-end ICP qualification:
        1. Calls Cloudflare Worker AI to extract structured evidence and signals.
        2. Validates the extracted payload and schema.
        3. Deterministically computes scores and business tiers via MasterScoringEngine.
        4. If Worker fails, returns an un-scored AccountAssessment with success=False and request_id.
        """
        req_id = f"req_{int(time.time() * 1000)}_{os.urandom(3).hex()}"

        if not prospect_text.strip():
            return AccountAssessment(
                metadata=AssessmentMetadata(
                    request_id=req_id,
                    success=False,
                    error_code="EMPTY_INPUT",
                    error_message="Prospect text input is empty."
                )
            )

        if not self.worker_url:
            return AccountAssessment(
                metadata=AssessmentMetadata(
                    request_id=req_id,
                    success=False,
                    error_code="WORKER_URL_MISSING",
                    error_message="CLOUDFLARE_WORKER_URL is not configured."
                )
            )

        payload = {
            "text": prospect_text,
            "prospect_text": prospect_text,
            "deal_size_usd": deal_size_usd
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Enterprise-ICP-Engine/2.0",
            "Accept": "application/json",
            "X-Request-ID": req_id
        }
        if self.auth_secret:
            headers["Authorization"] = f"Bearer {self.auth_secret}"

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

                # Check for explicit failure from Worker
                if not raw_res.get("success", True):
                    err_info = raw_res.get("error") or {}
                    return AccountAssessment(
                        metadata=AssessmentMetadata(
                            request_id=raw_res.get("request_id") or req_id,
                            success=False,
                            error_code=err_info.get("code", "AI_EXECUTION_FAILED"),
                            error_message=err_info.get("message", "Workers AI evaluation failed.")
                        )
                    )

                # Extract validated evidence components
                account_data = raw_res.get("account") or {}
                evidence_data = raw_res.get("evidence") or {}
                strategy_data = raw_res.get("strategy") or {}
                discovery_questions = raw_res.get("discovery_questions") or []
                key_strengths = raw_res.get("key_strengths") or []
                key_risks = raw_res.get("key_risks") or []
                is_disq = bool(raw_res.get("is_disqualified"))
                disq_reason = str(raw_res.get("disqualification_reason") or "")
                server_req_id = raw_res.get("request_id") or req_id

                # Pass extracted evidence into deterministic scoring engine
                return MasterScoringEngine.evaluate_assessment(
                    account_data=account_data,
                    evidence_data=evidence_data,
                    deal_size_usd=deal_size_usd,
                    strategy_data=strategy_data,
                    discovery_questions=discovery_questions,
                    key_strengths=key_strengths,
                    key_risks=key_risks,
                    is_disqualified=is_disq,
                    disqualification_reason=disq_reason,
                    config=active_config,
                    request_id=server_req_id
                )

        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="ignore")
            parsed_err = {}
            try:
                parsed_err = json.loads(error_body)
            except Exception:
                pass
            err_details = parsed_err.get("error", {})
            return AccountAssessment(
                metadata=AssessmentMetadata(
                    request_id=parsed_err.get("request_id") or req_id,
                    success=False,
                    error_code=err_details.get("code", f"HTTP_{http_err.code}"),
                    error_message=err_details.get("message", f"Worker returned HTTP {http_err.code}: {http_err.reason}")
                )
            )
        except Exception as e:
            return AccountAssessment(
                metadata=AssessmentMetadata(
                    request_id=req_id,
                    success=False,
                    error_code="CONNECTION_FAILED",
                    error_message=f"Could not connect to Cloudflare Worker AI: {e}"
                )
            )

    @classmethod
    def evaluate_locally(cls, prospect_text: str, deal_size_usd: float = 50000.0) -> AccountAssessment:
        """
        Pure deterministic offline qualification for tests and local fallback without remote AI.
        """
        req_id = f"req_local_{int(time.time() * 1000)}"
        extracted = ProspectExtractor.extract_evidence(prospect_text)
        
        # Build evidence structure from local extractor
        ev_fields = extracted.get("evidence_fields") or {}
        
        def to_pillar_dict(f_key: str):
            f = ev_fields.get(f_key)
            if not f or f.status == EvidenceStatus.UNKNOWN:
                return {"score": None, "status": "UNKNOWN", "confidence": 0.0, "rationale": f.rationale if f else "", "evidence_points": [], "missing_points": [f_key]}
            calc_score = round(f.confidence * 100.0, 1)
            return {"score": calc_score, "status": f.status.value, "confidence": f.confidence, "rationale": f.rationale, "evidence_points": [str(f.raw_value)], "missing_points": []}

        rev_field = ev_fields.get("annual_revenue")
        evidence_dict = {
            "firmographic": to_pillar_dict("company_name"),
            "technographic": to_pillar_dict("technographics"),
            "intent": to_pillar_dict("intent_signals"),
            "readiness": to_pillar_dict("contact_authority"),
            "value": {
                "score": round((rev_field.confidence if rev_field else 0.5) * 100.0, 1),
                "status": rev_field.status.value if rev_field else "UNKNOWN",
                "confidence": rev_field.confidence if rev_field else 0.0,
                "rationale": rev_field.rationale if rev_field else "Value proxy",
                "evidence_points": [str(rev_field.raw_value)] if rev_field and rev_field.raw_value else [],
                "missing_points": [] if rev_field and rev_field.raw_value else ["annual_revenue"]
            }
        }

        return MasterScoringEngine.evaluate_assessment(
            account_data={
                "company_name": extracted.get("company_name"),
                "domain": extracted.get("domain"),
                "contact_name": extracted.get("contact_name"),
                "job_title": extracted.get("job_title"),
                "industry": extracted.get("industry")
            },
            evidence_data=evidence_dict,
            deal_size_usd=deal_size_usd,
            discovery_questions=extracted.get("discovery_questions") or [],
            config=active_config,
            request_id=req_id
        )

