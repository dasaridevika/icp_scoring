# Enterprise ICP Intelligence & Revenue Qualification Engine (v2.0)

A production-grade, evidence-driven B2B Revenue Intelligence Engine implementing the **GTM Partners & Saber ICP Framework 2.0**.

**100% Dynamic Engine**: Zero hardcoded keyword dictionaries, static lists, or mock datasets. Driven purely by AI semantic evaluation, mathematical weights, and dynamic feature distance.

---

## 🏛️ System Architecture

```text
Account / Inbound Lead
        ↓
Data Normalization & Dynamic Evidence Extraction (DataStatus: Known Positive/Negative, Inferred, Unknown)
        ↓
Hard Eligibility & Anti-ICP Check (Disqualifier Engine)
        ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      4-DIMENSIONAL REVENUE ENGINES                     │
├───────────────────┬───────────────────┬────────────────────────────────┤
│ 1. ICP FIT ENGINE │  2. INTENT ENGINE │ 3. READINESS   │ 4. VALUE      │
│ (Firmographics,   │ (Active RFPs,     │ (Authority,    │ (ARR Scale,   │
│  Vertical, Tech,  │  Buying Timeline, │  Budget,       │  Expansion    │
│  Dynamic Sim)     │  Expansion)       │  Deployment)   │  Potential)   │
└───────────────────┴───────────────────┴────────────────────────────────┘
        ↓
Expected Value Model (P(Win) × Expected ARR × P(Retention) - Expected CAC)
        ↓
Operational Next Best Action (SLA Cadence, Channel, Hook, Discovery Prompts)
        ↓
Sales Outcome Recording & Dynamic Feedback Store (Model Evaluation & Calibration)
```

---

## 🎯 Key Architectural Upgrades (v1.0 → v2.0)

| Capability | Legacy v1.0 Prototype | Production v2.0 Engine |
| :--- | :--- | :--- |
| **Fit vs. Intent Separation** | Combined into a single murky 1–100 number. | **Strictly decoupled**: Static ICP Fit vs. Dynamic Buying Intent. |
| **Missing Data Handling** | Defaulted missing attributes to positive ~70 points. | Explicit `DataStatus.UNKNOWN`, **reduces confidence** instead of inflating score. |
| **Hard Eligibility** | Subtracted arbitrary points for anti-ICP. | **Binary Gatekeeper**: Hard disqualifiers (freemail, sanctioned geos, sub-scale). |
| **Win Likelihood** | Fake/uncalibrated conversion claims. | **Calibrated Win Propensity** $P(\text{Win} \mid \text{Features})$ via Logistic Regression. |
| **Valuation Model** | Simple deal multiplier. | **Expected Net Value (EV)** equation incorporating Retention and CAC. |
| **Model Governance** | Unversioned, hardcoded weights. | **Model Versioning (`ICP-v2.0-Production`)**, configurable YAML/Pydantic weights ($\sum w = 1.0$). |
| **Sales Activation** | Generic recommendation. | **Actionable SLAs, cold outreach hooks, and gap-filling discovery prompts**. |

---

## 📐 Mathematical Specification & Scoring Formulas

### 1. ICP Fit Engine (0–100)
$$\text{ICP Fit} = \sum_{i} w_i \times S_i$$
* **Weights:** Firmographics ($0.25$), Vertical ($0.25$), Problem Fit ($0.20$), Technographics ($0.15$), Geo ($0.05$), Dynamic Similarity ($0.10$).
* **Constraint:** $\sum w_i = 1.00$.

### 2. Intent Engine (0–100)
$$\text{Intent} = (0.30 \times \text{Search/RFP}) + (0.35 \times \text{Timeline}) + (0.20 \times \text{Expansion}) + (0.15 \times \text{Competitor})$$

### 3. Readiness Engine (0–100)
$$\text{Readiness} = (0.35 \times \text{Authority}) + (0.30 \times \text{Budget}) + (0.20 \times \text{Deployment}) + (0.15 \times \text{Procurement})$$

### 4. Expected Net Value (EV)
$$\text{Expected Net Value} = \left[ P(\text{Win}) \times \text{ARR} \times (1 + P(\text{Retention})) \right] - \left[ P(\text{Win}) \times \text{CAC} \right]$$

---

## 🚦 Priority Tiers & Next Best Action Matrix

| Priority Tier | Fit Score | Intent Score | Sales SLA & Recommended Action |
| :--- | :---: | :---: | :--- |
| **Tier A1: Strategic Inbound** | $\ge 80$ | $\ge 70$ | **<2 hours** outreach by Senior AE & Research Director. Deliver bespoke proposal. |
| **Tier A2: High Priority Outbound** | $\ge 75$ | $< 70$ | **<24 hours** SDR outbound cadence leading with tailored value wedge. |
| **Tier B1: Mid-Market Fast Track** | $\ge 50$ | $\ge 50$ | Inside Sales demonstration and rapid qualification call. |
| **Tier A3: Outbound Nurture** | $\ge 45$ | $< 50$ | Automated marketing webinar drip sequences and expansion trigger monitoring. |
| **Tier C: Deprioritize** | $< 45$ | Any | Self-serve product documentation / marketing newsletter. |
| **Disqualified / Anti-ICP** | N/A | N/A | Automated disqualification (Preserves SDR calling bandwidth). |

---

## 🚀 Launching the Streamlit Application

```bash
pip install -r requirements.txt
streamlit run app.py
```
