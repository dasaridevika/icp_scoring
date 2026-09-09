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


def get_worker_url() -> str:
    """Retrieve CLOUDFLARE_WORKER_URL strictly from Streamlit secrets or OS environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "CLOUDFLARE_WORKER_URL" in st.secrets:
                return str(st.secrets["CLOUDFLARE_WORKER_URL"]).strip().rstrip("/")
            for k, val in st.secrets.items():
                if k.lower() == "cloudflare_worker_url":
                    return str(val).strip().rstrip("/")
    except Exception:
        pass
    return os.environ.get("CLOUDFLARE_WORKER_URL", "").strip().rstrip("/")


class WorkerAIClient:
    """
    Client connecting to Cloudflare Worker AI for structured evidence extraction.
    Scores and decisions are deterministically computed by MasterScoringEngine.
    """

    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = (worker_url or get_worker_url()).strip().rstrip("/")
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

