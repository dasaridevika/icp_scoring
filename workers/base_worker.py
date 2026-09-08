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
        self.auth_secret = (
            get_secret("CLOUDFLARE_AUTH_SECRET") or
            get_secret("AUTH_SECRET") or
            get_secret("WORKER_AUTH_SECRET") or
            ""
        ).strip()

    def is_connected(self) -> bool:
        return bool(self.worker_url)

    def score_prospect(self, prospect_text: str, deal_size_usd: float = 50000.0) -> Optional[Dict[str, Any]]:
        """
        Calls the Cloudflare Worker AI with enterprise synthesis prompt and JSON schema.
        Extracts entities, dynamic pillar scores (0-100), and personalized deal strategy.
        """
        if not self.worker_url:
            return None

        system_prompt = (
            "You are an enterprise ICP Revenue Intelligence and qualification AI engine. "
            "Analyze the provided prospect text according to GTM Partners & Saber ICP qualification standards. "
            "Dynamically evaluate 4 pillars: Firmographics, Technographics, Intent/Timing, and Buyer Persona. "
            "Extract entity details, compute dynamic continuous scores (0 to 100) for each pillar, "
            "provide concise executive rationales, and generate custom deal strategy hooks. "
            "You MUST respond ONLY with valid JSON conforming to the following structure:\n"
            "{\n"
            '  "company_name": "string",\n'
            '  "contact_name": "string",\n'
            '  "job_title": "string",\n'
            '  "industry": "string",\n'
            '  "scale": "string",\n'
            '  "tech_stack": "string",\n'
            '  "intent_timeline": "string",\n'
            '  "urgency_level": "string",\n'
            '  "firmographics_score": 85,\n'
            '  "firmographics_rationale": "Rationale...",\n'
            '  "technographics_score": 80,\n'
            '  "technographics_rationale": "Rationale...",\n'
            '  "intent_score": 90,\n'
            '  "intent_rationale": "Rationale...",\n'
            '  "persona_score": 88,\n'
            '  "persona_rationale": "Rationale...",\n'
            '  "value_wedge": "High-impact value wedge...",\n'
            '  "outreach_hook": "Personalized cold outreach hook...",\n'
            '  "discovery_questions": ["Question 1", "Question 2"]\n'
            "}"
        )

        user_prompt = (
            f"Prospect Raw Text / RFP Ingestion:\n{prospect_text}\n\n"
            f"Estimated Target Deal Size: ${deal_size_usd:,.2f} USD\n\n"
            "Generate the full ICP qualification analysis and JSON output."
        )

        payload = {
            "action": "synthesize",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "text": prospect_text,
            "prospect_text": prospect_text,
            "deal_size_usd": deal_size_usd
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Enterprise-ICP/1.0",
            "Accept": "application/json"
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
            with urllib.request.urlopen(req, timeout=35) as response:
                body = response.read().decode("utf-8")
                res_data = json.loads(body)
                
                # Handle worker envelope response formats
                if isinstance(res_data, dict):
                    if "response" in res_data and isinstance(res_data["response"], (dict, str)):
                        nested = res_data["response"]
                        if isinstance(nested, dict):
                            return nested
                        try:
                            return json.loads(nested)
                        except Exception:
                            pass
                    if "result" in res_data and isinstance(res_data["result"], (dict, str)):
                        nested = res_data["result"]
                        if isinstance(nested, dict):
                            return nested
                        try:
                            return json.loads(nested)
                        except Exception:
                            pass
                    return res_data
                return None
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
