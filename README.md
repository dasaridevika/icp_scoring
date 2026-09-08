# Enterprise B2B Ideal Customer Profile (ICP) Scoring Engine

A production-grade, enterprise lead qualification and revenue intelligence engine connecting to Cloudflare Worker AI and implementing the Saber ICP Scoring Model.

---

## Overview

- **Dynamic AI Qualification**: Evaluates unstructured prospect data (emails, RFPs, LinkedIn bios, CRM notes) across the 4 Saber Pillars:
  - **Firmographics (30%)**: Target industry vertical, headcount, revenue scale, geographic market.
  - **Technographics (25%)**: Technology stack sophistication, CRM/ERP infrastructure, data maturity.
  - **Intent & Timing (25%)**: Buying urgency, hiring velocity, CapEx/project expansion triggers.
  - **Persona & Authority (20%)**: Decision-maker seniority, champion alignment, budget power.
- **Saber Tiers & Sales Action**:
  - **Tier 1: Dream ICP (80 – 100)**: Strategic Outbound / Senior AE outreach within 2h.
  - **Tier 2: Strong Fit (60 – 79.9)**: Standard Sales Pipeline / SDR cadence within 24h.
  - **Tier 3: Moderate Fit (40 – 59.9)**: Inside Sales / Automated marketing nurture.
  - **Out of ICP (< 40 or Disqualified)**: Deprioritize to protect sales team capacity.
- **Quality-Weighted Forecast**: Calculates realistic deal value based on lead score.
- **Zero UI URL Inputs**: Reads worker link securely from `.streamlit/secrets.toml` or environment variables.

---

## Setup & Running

### 1. Configure Secret
Add your deployed Cloudflare Worker AI URL to `.streamlit/secrets.toml`:
```toml
CLOUDFLARE_WORKER_URL = "https://icp-scoring-worker-ai.<your-subdomain>.workers.dev"
```

### 2. Launch Streamlit Studio
```bash
pip install -r requirements.txt
streamlit run app.py
```
