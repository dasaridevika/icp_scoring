"""
Enterprise ICP Revenue Intelligence - Python REST API Worker
Runs as a lightweight HTTP microservice using standard Python HTTP server (zero extra dependencies required)
or FastAPI/Uvicorn if installed.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from engine import AITextAnalyzer, GTMScoringEngine, StreamlinedLeadForm, CompanyStandardsConfig


class ICPWorkerHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        self._set_headers(200)
        resp = {
            "status": "active",
            "service": "Enterprise ICP Revenue Intelligence Worker API",
            "version": "2.5",
            "capabilities": [
                "AI Role & Persona Semantic Classification",
                "AI Sub-Vertical & Market Complexity Analysis",
                "AI Buying Intent & Timeline Extraction",
                "AI Technographics Ecosystem Parsing",
                "Dynamic Settings-Driven Threshold Evaluation"
            ]
        }
        self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
            
            # Extract prospect form submission
            submission = StreamlinedLeadForm(
                company_name=body.get("company_name", body.get("company", "")),
                industry_sector=body.get("industry_sector", body.get("industry", "Technology, SaaS & IT")),
                sub_vertical=body.get("sub_vertical", body.get("niche", "")),
                annual_revenue_usd=float(body.get("annual_revenue_usd", body.get("revenue", 0.0))),
                employee_count=int(body.get("employee_count", body.get("headcount", 50))),
                location=body.get("location", body.get("territory", "")),
                contact_name=body.get("contact_name", body.get("name", "")),
                contact_email=body.get("contact_email", body.get("email", "")),
                contact_role_title=body.get("contact_role_title", body.get("role_title", "")),
                buying_intent=body.get("buying_intent", body.get("intent_notes", "")),
                target_deal_size_usd=float(body.get("target_deal_size_usd", body.get("deal_size", 0.0))),
                tech_stack_notes=body.get("tech_stack_notes", body.get("tech_stack", ""))
            )

            # Optional custom company standards config
            cfg_dict = body.get("company_standards", {})
            config = CompanyStandardsConfig(**cfg_dict) if cfg_dict else CompanyStandardsConfig()

            # Execute GTM scoring with AI text analysis
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
