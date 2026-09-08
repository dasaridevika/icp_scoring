"""
Production Worker AI Client
Connects strictly via CLOUDFLARE_WORKER_URL configured in GitHub Secrets / Streamlit Secrets / Environment Variables.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


DEFAULT_WORKER_URL = "https://icp-scoring-worker-ai.devika-worker.workers.dev"


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from Streamlit secrets or OS environment, with default fallback."""
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
    def __init__(self, worker_url: Optional[str] = None):
        self.worker_url = (
            worker_url or
            get_secret("CLOUDFLARE_WORKER_URL") or
            get_secret("WORKER_AI_URL") or
            DEFAULT_WORKER_URL
        ).strip().rstrip("/")

    def is_connected(self) -> bool:
        return bool(self.worker_url)

    def score_prospect(self, prospect_text: str, deal_size_usd: float = 50000.0) -> Optional[Dict[str, Any]]:
        """
        Calls the Cloudflare Worker AI link with the raw prospect text and deal size.
        Returns the complete dynamic added-up score, Saber tier, and AI deal strategy.
        """
        if not self.worker_url:
            return None

        try:
            payload = {
                "text": prospect_text,
                "prospect_text": prospect_text,
                "deal_size_usd": deal_size_usd
            }
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.worker_url,
                data=data_bytes,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                print(f"[Worker AI HTTP Error {e.code}]: {err_body}")
            except Exception:
                pass
            return None
        except Exception as e:
            print(f"[Worker AI Client Error]: {e}")
            return None
