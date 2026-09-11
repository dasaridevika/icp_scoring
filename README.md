# Enterprise ICP Intelligence & Revenue Qualification Engine (v2.0)

A production-grade, 100% self-contained, evidence-driven B2B Revenue Intelligence Engine. Powered by a deterministic Python extraction and scoring pipeline for real-time account qualification, priority tiering, win propensity calibration, and sales outreach generation — with zero external API dependencies and sub-50ms execution.

---

## 🏛️ System Architecture

```text
Streamlit UI / Lead Inbound Input
         ↓
Lead Evidence Extractor (`engine/extractor.py`)
  • Deterministic entity parsing (Company, Contact, Domain, Industry, Scale, Tech Stack, Intent Timeline)
  • Evidence pillar classification (Firmographic, Technographic, Intent, Readiness, Value)
  • Anti-ICP & freemail detection (student, personal freemail, non-commercial)
         ↓
Disqualification Engine (`engine/disqualifier.py`)
  • Hard eligibility checks (Prohibited industries, non-business domains, compliance)
         ↓
Deterministic Scoring Engine (`engine/scorer.py`)
  • Centralized authoritative weights & thresholds (`engine/config.py`)
  • 4-Dimensional mathematical scoring (Fit, Intent, Readiness, Value)
  • Probability calibration & expected value modeling (`engine/calibration.py`)
         ↓
Canonical Assessment Contract (`AccountAssessment`)
         ↓
Interactive Streamlit Dashboard (`app.py`)
```

### Key Capabilities
* **100% Self-Contained & Offline**: Zero network calls, zero external API keys, zero cloud worker bindings required. Runs anywhere Python 3.9+ runs.
* **Deterministic Scoring Engine (`engine/scorer.py`)**: Owns 100% of final score computation, weighted dimensional aggregation, tier assignment, and expected value calculation using authoritative weights from `engine/config.py`.
* **Zero Mock Datasets & Zero Fake Fallbacks**: Parses real inbound lead text dynamically and scores mathematically based on verified evidence points.
* **Granular Confidence & Missing Data Tracking**: Missing attributes are marked as `UNKNOWN` ($0$ contribution) rather than assuming inflated values, triggering targeted sales discovery questions.

---

## 📐 Scoring Methodology & Authoritative Configuration

All scoring weights, tier thresholds, and disqualifiers are centrally managed in `engine/config.py`.

### 1. 4-Dimensional Core Engine (0–100)
* **ICP Fit Score**: Firmographic Scale ($0.65$) + Technographic Sophistication ($0.35$).
* **Intent & Timing Score**: Active Research, RFP, and Buying Urgency Signals.
* **Readiness & Authority Score**: Decision-Maker Title, C-Suite Mandate, and Budget Authority.
* **Value & Expansion Score**: Contract ARR Scale and Expansion Potential.

### 2. Master ICP Score
$$\text{Master ICP Score} = (0.35 \times \text{Fit}) + (0.25 \times \text{Intent}) + (0.20 \times \text{Readiness}) + (0.20 \times \text{Value})$$

### 3. Business Priority Tiers & Action Matrix

| Priority Tier | Fit Score | Intent Score | Sales SLA & Recommended Action |
| :--- | :---: | :---: | :--- |
| **Tier A1: Strategic Inbound** | $\ge 80$ | $\ge 70$ | **<2 hours** outreach by Senior AE & Research Director. Deliver bespoke proposal. |
| **Tier A2: High Priority Outbound** | $\ge 65$ | Any | **<24 hours** SDR strategic outbound sequence. |
| **Tier B1: Mid-Market Fast Track** | $\ge 50$ | $\ge 50$ | Inside Sales rapid qualification call. |
| **Tier A3: Outbound Nurture** | $\ge 40$ | $< 50$ | Automated marketing educational sequences and trigger tracking. |
| **Tier C: Low Priority / Long-Tail** | $< 40$ | Any | Marketing newsletter and self-service documentation. |
| **Disqualified / Anti-ICP** | N/A | N/A | Personal freemail, prohibited industry, or non-commercial inquiry. |

---

## 🚀 Running the Application

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard
```bash
streamlit run app.py
```

### 3. Python SDK Usage
```python
from engine import evaluate_lead

lead_text = """
Company: Parveen Industries Pvt. Ltd.
Contact: Gabriel Martinez (Commercial Sales & Procurement)
Email: sales@parvenoilfield.com
Phone: +971 55 669 322
Location: United Arab Emirates (UAE)
Industry: Industrial Manufacturing & Solar Energy Infrastructure

Inquiry Details:
Requested an executive callback meeting scheduled for August 18 (08:30 PM - 09:30 PM IST).
Inquiring about solar power market offerings and product range suitability to support company business expansion.
"""

assessment = evaluate_lead(lead_text, deal_size_usd=75000)

print(f"Company: {assessment.company_name}")
print(f"Tier: {assessment.priority_tier}")
print(f"Master ICP Score: {assessment.scores.master_icp_score}")
print(f"Fit: {assessment.icp_fit_score} | Intent: {assessment.intent_score} | Readiness: {assessment.readiness_score} | Value: {assessment.value_score}")
print(f"Next Action: {assessment.sales_action}")
print(f"Cold Outreach Opener: {assessment.outreach_hook}")
```


