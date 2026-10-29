"""
Enterprise ICP Revenue Intelligence - Python REST API Worker
Runs as a lightweight HTTP microservice using standard Python HTTP server (zero extra dependencies required)
or FastAPI/Uvicorn if installed.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from engine.gtm_engine import GTMScoringEngine, StreamlinedLeadForm, CompanyStandardsConfig


class ICPWorkerHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-ICP-Worker-Key")
        self.end_headers()

    def _check_auth(self) -> bool:
        auth_key = os.environ.get("ICP_WORKER_KEY", os.environ.get("ICP_AUTH_KEY", ""))
        if not auth_key:
            return True  # No auth required if secret key is not set
        provided_header = self.headers.get("X-ICP-Worker-Key", "")
        auth_header = self.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            bearer_token = auth_header[7:].strip()
        else:
            bearer_token = auth_header.strip()
        return (provided_header == auth_key) or (bearer_token == auth_key)

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        if not self._check_auth():
            self._set_headers(401)
            self.wfile.write(json.dumps({"success": False, "error": "Unauthorized: Invalid or missing API key"}).encode("utf-8"))
            return

        self._set_headers(200)
        resp = {
            "status": "active",
            "service": "Enterprise ICP Revenue Intelligence Worker API",
            "version": "3.6",
            "capabilities": [
                "Section 6 Four-Pillar ICP Scoring Rubric",
                "Firmographic, Offering Fit, Buyer Authority & Intent Evaluation",
                "Deterministic Sanctions & Anti-ICP Whole-Word Policy Checks",
                "Coverage-Weighted Mathematical Scoring (Zero Fake Defaults)",
                "Fail-Loud Observability"
            ]
        }
        self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))

    def do_POST(self):
        if not self._check_auth():
            self._set_headers(401)
            self.wfile.write(json.dumps({"success": False, "error": "Unauthorized: Invalid or missing API key"}).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}

            branches = body.get("branch_locations", body.get("branches", []))
            if isinstance(branches, str):
                branches = [b.strip() for b in branches.split(",") if b.strip()]

            # Safely parse employee count (No fake default 50)
            raw_hc = body.get("employee_count", body.get("headcount"))
            employee_count = None
            if raw_hc is not None and str(raw_hc).strip() != "":
                try:
                    employee_count = int(raw_hc)
                except (ValueError, TypeError):
                    employee_count = None

            # Safely parse revenue (No fake default 0)
            raw_rev = body.get("annual_revenue_usd", body.get("revenue"))
            annual_revenue_usd = None
            if raw_rev is not None and str(raw_rev).strip() != "":
                try:
                    annual_revenue_usd = float(raw_rev)
                except (ValueError, TypeError):
                    annual_revenue_usd = None

            # Safely parse deal size / budget (No fake default 0)
            raw_deal = body.get("target_deal_size_usd", body.get("deal_size"))
            target_deal_size_usd = None
            if raw_deal is not None and str(raw_deal).strip() != "":
                try:
                    target_deal_size_usd = float(raw_deal)
                except (ValueError, TypeError):
                    target_deal_size_usd = None

            deal_curr = body.get("deal_currency_code", body.get("deal_currency", body.get("currency_code", "USD")))

            # Extract prospect form submission (no made-up defaults)
            submission = StreamlinedLeadForm(
                company_name=body.get("company_name", body.get("company", "")),
                currency_code=body.get("currency_code", "USD"),
                deal_currency_code=deal_curr,
                industry_sector=body.get("industry_sector", body.get("industry", "")),
                sub_vertical=body.get("sub_vertical", body.get("niche", "")),
                annual_revenue_usd=annual_revenue_usd,
                employee_count=employee_count,
                location=body.get("location", body.get("territory", "")),
                branch_locations=branches,
                contact_name=body.get("contact_name", body.get("name", "")),
                contact_email=body.get("contact_email", body.get("email", "")),
                contact_role_title=body.get("contact_role_title", body.get("role_title", "")),
                buying_role=body.get("buying_role", ""),
                buying_intent=body.get("buying_intent", body.get("intent_notes", "")),
                timeline=body.get("timeline", ""),
                offering_interest=body.get("offering_interest", body.get("offering", "")),
                target_deal_size_usd=target_deal_size_usd,
                tech_stack_notes=body.get("tech_stack_notes", body.get("tech_stack", "")),
                existing_platform=body.get("existing_platform", body.get("uses_existing_platform", ""))
            )

            # Optional custom company standards config
            cfg_dict = body.get("company_standards", {})
            config = CompanyStandardsConfig(**cfg_dict) if cfg_dict else CompanyStandardsConfig()

            # Execute GTM scoring with authoritative Section 6 rubric
            res = GTMScoringEngine.evaluate(submission, config)

            self._set_headers(200)
            self.wfile.write(json.dumps(res.model_dump(), indent=2).encode("utf-8"))

        except Exception as e:
            self._set_headers(500)
            err_resp = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(err_resp).encode("utf-8"))


def run_worker(port=8787):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ICPWorkerHandler)
    print(f"[INFO] ICP Revenue Intelligence Worker API listening on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    run_worker()
