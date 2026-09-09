# Enterprise ICP Intelligence & Revenue Qualification Engine (v2.0)

A production-grade, evidence-driven B2B Revenue Intelligence Engine powered by Cloudflare Worker AI for edge evidence extraction and a deterministic Python scoring engine for qualification, tiering, and sales action recommendations.

---

## 🏛️ System Architecture

```text
Streamlit UI / Inbound CSV
         ↓
Worker AI Client (`workers/base_worker.py`) [Generates Trace/Request ID: req_...]
         ↓
Cloudflare Worker (`index.js` on Edge)
         ↓
Workers AI (Meta Llama 3.1 8B Instruct)
         ↓
Evidence Extraction & Schema Validation (Pillars: Firmographic, Technographic, Intent, Readiness, Value)
         ↓
Deterministic Scoring Engine (`engine/scorer.py`) [Applies Centralized Weights & Thresholds]
         ↓
Canonical Assessment Contract (`AccountAssessment`)
         ↓
UI / CRM Export (`app.py`)
```

### Separation of Responsibilities
* **Workers AI on Edge (`index.js`)**: Responsible for language understanding, extracting entity attributes, classifying evidence status (`VERIFIED`, `INFERRED`, `UNKNOWN`), generating sales discovery questions, and crafting cold outreach copy.
* **Deterministic Scoring Engine (`engine/scorer.py`)**: Owns 100% of final score computation, weighted dimensional aggregation, tier assignment, and expected value calculation using authoritative weights from `engine/config.py`. AI cannot override final deterministic scores.

---

## 🛡️ Failure Modes & Error Behavior

1. **AI Failure → Explicit Visible Error with Request ID**:
   - If Workers AI binding is missing (`HTTP 500`), inference fails (`HTTP 502`), or response is malformed (`HTTP 422`), the system returns `AccountAssessment` with `success=False`, error details, and a unique `request_id`.
   - **Zero Fake Scores**: AI failure never generates fallback average scores (`75/70/70/75` or `50.0`). The UI clearly presents:
     ```text
     ❌ Unable to score this account.
     AI evaluation failed: [Error Message]
     Request ID: req_1725883800000_abc123
     ```
2. **Missing Data Handling (Zero `70` Fallbacks)**:
   - Missing or unverified attributes receive `EvidenceStatus.UNKNOWN` with `confidence = 0.0`.
   - Missing pillars contribute `0.0` points, reducing overall confidence instead of inflating scores.
   - Targeted discovery questions are automatically generated so sales reps know what questions to ask.

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

## 🧪 Automated Test Suite

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

### Verified Test Scenarios:
1. `test_ai_failure_produces_no_score_and_visible_error`: Confirms AI failure returns structured error and zero fake scores.
2. `test_missing_pillar_is_unknown_not_70`: Confirms missing data receives `UNKNOWN` status, 0 confidence, and no 70 default.
3. `test_malformed_ai_response_validation`: Confirms invalid JSON from LLM is safely handled.
4. `test_out_of_range_ai_scores_clamped`: Confirms scores outside 0-100 are strictly bounded.
5. `test_ai_final_score_override_is_ignored`: Confirms deterministic engine calculates score regardless of LLM claim.
6. `test_materially_different_companies_produce_different_scores`: Confirms Account A (Enterprise, Score $\ge 85$) > Account B (Mid-Market, Score $50-70$) > Account C (Disqualified, Score $0$).
7. `test_account_d_unknown_data_low_confidence`: Confirms company-only accounts have low confidence and flagged unknowns.
8. `test_configuration_consistency`: Confirms updating weights in `config.py` consistently alters score calculations.
9. `test_disqualification_personal_email_and_prohibited_vertical`: Confirms personal emails (@gmail.com) and excluded industries are disqualified.
10. `test_batch_processing_isolated_failures`: Confirms batch processing handles row-level failures safely without corrupting other rows.

---

## 🚀 Running the Streamlit Application

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables (Optional):
* `CLOUDFLARE_WORKER_URL`: Cloudflare Worker endpoint URL (defaults to deployed worker).
* `CLOUDFLARE_AUTH_SECRET`: Bearer token if Cloudflare Worker is protected with auth secret.

