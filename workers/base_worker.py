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


from pathlib import Path


DEFAULT_WORKER_URL = "https://icp-scoring-worker-ai.devika-worker.workers.dev"


def get_worker_url() -> str:
    """Retrieve CLOUDFLARE_WORKER_URL from Streamlit secrets, OS environment, .streamlit/secrets.toml, or default fallback."""
    # 1. Check Streamlit runtime secrets (direct + case-insensitive + nested dicts)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "CLOUDFLARE_WORKER_URL" in st.secrets:
                val = str(st.secrets["CLOUDFLARE_WORKER_URL"]).strip().rstrip("/")
                if val:
                    return val
            for k, v in st.secrets.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        if "worker" in sub_k.lower() or "cloudflare" in sub_k.lower():
                            cand = str(sub_v).strip().rstrip("/")
                            if cand.startswith("http"):
                                return cand
                elif "worker" in k.lower() or "cloudflare" in k.lower():
                    cand = str(v).strip().rstrip("/")
                    if cand.startswith("http"):
                        return cand
    except Exception:
        pass

    # 2. Check OS environment variables
    for env_k in ["CLOUDFLARE_WORKER_URL", "WORKER_URL", "CF_WORKER_URL"]:
        env_val = os.environ.get(env_k, "").strip().rstrip("/")
        if env_val and env_val.startswith("http"):
            return env_val

    # 3. Direct read of local or global .streamlit/secrets.toml
    candidate_paths = [
        Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml",
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml"
    ]
    for p in candidate_paths:
        try:
            if p.exists() and p.is_file():
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if ("CLOUDFLARE_WORKER_URL" in line or "WORKER_URL" in line) and "=" in line:
                        _, raw_v = line.split("=", 1)
                        val = raw_v.strip().strip("\"'").rstrip("/")
                        if val and val.startswith("http"):
                            return val
        except Exception:
            pass

    # 4. Canonical Production Worker Fallback
    return DEFAULT_WORKER_URL


class WorkerAIClient:
    """
    Client connecting to Cloudflare Worker AI for structured evidence extraction.
    Scores and decisions are deterministically computed by MasterScoringEngine.
    """

    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = (worker_url or get_worker_url()).strip().rstrip("/")
        self.timeout_sec = 25

    def is_connected(self) -> bool:
        return bool(self.worker_url or get_worker_url())

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
        endpoint = (self.worker_url or get_worker_url()).strip().rstrip("/")

        if not prospect_text.strip():
            return AccountAssessment(
                metadata=AssessmentMetadata(
                    request_id=req_id,
                    success=False,
                    error_code="EMPTY_INPUT",
                    error_message="Prospect text input is empty."
                )
            )

        if not endpoint:
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
                endpoint,
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

