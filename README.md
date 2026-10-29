# Enterprise ICP Intelligence & Revenue Qualification Engine

A production-grade, evidence-driven B2B Revenue Intelligence Engine. Powered by a deterministic Python extraction and scoring pipeline for real-time account qualification, priority tiering, win propensity calibration, and sales outreach generation.

---

## 🏛️ System Architecture

```text
Streamlit Dashboard / API Input
         ↓
Compliance & Policy Hard Stops (`engine/rules.py`)
  • Prohibited & sanctioned territory checks (whole-word matching & branch location review)
  • Non-commercial persona checks (students, interns, trainees, academic research)
         ↓
Currency FX Normalization Engine (`engine/fx.py`)
  • Verified regional currency conversion to USD
  • Independent deal/budget currency normalization
         ↓
AI Evidence & Rating Extractor (`index.js` / Worker API)
  • Semantic classification: Firmographic, Offering Fit, Buyer Authority, Intent & Velocity
  • 1 to 5 criteria ratings (or UNKNOWN for unverified attributes; zero data fabrication)
         ↓
Deterministic Scoring & Coverage Engine (`engine/gtm_engine.py`)
  • Dynamic weight renormalization across known pillars
  • Mathematical scoring based on verified evidence
  • "Needs review" safety-tier override when coverage < 60% or authority is unknown
         ↓
Interactive RevOps Dashboard (`app.py`) / REST API (`worker.py`)
```

### Key Capabilities
* **100% Self-Contained Core**: Hard compliance rules and mathematical scoring reside entirely in Python.
* **Deterministic Scoring Engine (`engine/gtm_engine.py`)**: Computes master composite score, tier assignment, coverage percentage, and next-action SLAs.
* **Zero Mock Datasets & Zero Fake Fallbacks**: Missing attributes are classified as `UNKNOWN` ($0$ contribution) rather than assuming inflated values, triggering targeted sales discovery questions.
* **Dynamic Weight Renormalization**: Scoring dynamically scales across verified pillars, ensuring incomplete leads are flagged for manual review rather than falsely awarded high-priority tiers.

---

## 📐 Scoring Methodology

### 1. 4-Pillar Qualitative Rubric
* **Firmographic Fit (35%)**: Organization scale, focus sector, geography, and corporate email verification.
* **Offering Fit (25%)**: Alignment between prospect needs and company product/service offerings, including incumbent displacement.
* **Buyer Authority (25%)**: Decision-making authority, seniority hierarchy, and executive mandate.
* **Intent & Velocity (15%)**: Active buying urgency, RFP, timeline checkpoints, and stated project catalysts.

### 2. Rating Scale (1 to 5)
* **5**: Strong match, clear verified evidence
* **4**: Good match
* **3**: Partial match
* **2**: Weak match
* **1**: Clear mismatch (evidence indicates incompatibility)
* **UNKNOWN**: No evidence provided (excluded from score calculation)

### 3. Master ICP Score & Coverage
$$\text{Score} = \frac{\sum_{\text{known pillars}} (\text{weight} \times \text{rating})}{\sum_{\text{known pillars}} \text{weight}} \times 20$$

$$\text{Coverage} = \sum_{\text{known pillars}} \text{weight} \times 100\%$$

### 4. Priority Tiers & Action Matrix

| Priority Tier | Score | Qualification Condition | Recommended Sales SLA & Action |
| :--- | :---: | :---: | :--- |
| **Tier A: Contact First** | $\ge 80$ | High Coverage & Strong Match | **< 2 hours**: Executive callback by Senior AE & Research Director. |
| **Tier B: Follow Up** | $60 - 79$ | Qualified Opportunity | **< 24 hours**: Dedicated SDR strategic outbound sequence. |
| **Tier C: Nurture** | $40 - 59$ | Moderate Match | **Within 48 hours**: Automated marketing educational nurture sequences. |
| **Tier D: Low Priority** | $< 40$ | Low ICP Fit | Automated marketing newsletter and documentation. |
| **Tier: Needs review** | Any | Coverage $< 60\%$ OR Authority Unknown | **Manual Review**: Human sales qualification call required. |
| **Disqualified: Anti-ICP** | $0.0$ | Compliance violation or non-buyer role | **Archived**: Do Not Contact. |

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
from engine.gtm_engine import GTMScoringEngine, StreamlinedLeadForm, CompanyStandardsConfig

# Initialize custom company standards (all fields configurable)
config = CompanyStandardsConfig(
    company_name="",
    min_deal_size_usd=0.0,
    target_deal_size_usd=0.0,
    min_company_revenue_usd=0.0
)

# Provide prospect attributes dynamically
form = StreamlinedLeadForm(
    company_name="",
    industry_sector="",
    sub_vertical="",
    location="",
    contact_name="",
    contact_role_title="",
    buying_role="",
    buying_intent="",
    timeline="",
    annual_revenue_usd=None,
    employee_count=None,
    target_deal_size_usd=None
)

# Run deterministic evaluation
assessment = GTMScoringEngine.evaluate(form, config)

print(f"Company: {assessment.company_name}")
print(f"Tier: {assessment.priority_tier}")
print(f"Master ICP Score: {assessment.master_icp_score}")
print(f"Data Coverage: {assessment.coverage_pct}%")
print(f"Next Action SLA: {assessment.urgency_sla}")
```
