# 🎯 Enterprise B2B Ideal Customer Profile (ICP) Scoring Engine

A production-grade, enterprise lead qualification and revenue intelligence engine powered by Cloudflare Worker AI and the [Saber ICP Scoring Model](https://www.saber.app/glossary/icp-scoring-model).

---

## 🏗️ Architecture

- **100% Dynamic Qualification**: Evaluates unstructured prospect data (emails, RFPs, LinkedIn bios, CRM notes) using Cloudflare Worker AI (`@cf/meta/llama-3.1-8b-instruct`).
- **Saber Weighted Matrix**:
  - **Firmographics (30%)**: Target industry vertical, headcount, revenue scale, geographic market.
  - **Technographics (25%)**: Technology stack sophistication, CRM/ERP infrastructure, data maturity.
  - **Intent & Timing (25%)**: Buying urgency, hiring velocity in strategic functions, CapEx/project expansion triggers.
  - **Persona & Authority (20%)**: Decision-maker seniority (C-Suite/VP/Director), champion alignment, budget power.
- **Saber Tiers & Sales Action**:
  - **Tier 1: Dream ICP (80 – 100)** $\rightarrow$ Strategic Outbound / Senior AE outreach within 2h.
  - **Tier 2: Strong Fit (60 – 79.9)** $\rightarrow$ Standard Sales Pipeline / SDR cadence within 24h.
  - **Tier 3: Moderate Fit (40 – 59.9)** $\rightarrow$ Inside Sales / Automated marketing nurture.
  - **Out of ICP (< 40 or Disqualified)** $\rightarrow$ Deprioritize to protect sales team capacity.
- **Quality-Weighted Forecast**: Calculates realistic deal value ($\text{Estimated Deal Size} \times \text{Score} / 100$).
- **Zero UI URL Inputs**: Reads strictly from secrets (`CLOUDFLARE_WORKER_URL`).

---

## 🚀 Setup & Deployment

### 1. Deploy Cloudflare Worker AI
```bash
cd cloudflare-worker
npx wrangler deploy
```
Copy your published Worker URL: `https://icp-scoring-worker-ai.<your-subdomain>.workers.dev`

### 2. Configure Secret
Add to your GitHub Repository Secrets or `.streamlit/secrets.toml`:
```toml
CLOUDFLARE_WORKER_URL = "https://icp-scoring-worker-ai.<your-subdomain>.workers.dev"
```

### 3. Launch Streamlit Studio
```bash
streamlit run app.py
```
