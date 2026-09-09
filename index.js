// Enterprise ICP Revenue Intelligence - Cloudflare Worker AI Edge Engine
// Dynamic Evidence-Aware Qualification & Structured Extraction

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID"
};

function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "Content-Type": "application/json", ...CORS_HEADERS }
  });
}

function parseJsonSafely(rawText) {
  try {
    return JSON.parse(rawText);
  } catch (e) {
    const match = rawText.match(/\{[\s\S]*\}/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch (err) {}
    }
    return null;
  }
}

function clampScore(val) {
  if (val === null || val === undefined || isNaN(Number(val))) return null;
  return Math.max(0, Math.min(100, Number(val)));
}

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const requestId = request.headers.get("X-Request-ID") || generateRequestId();

    if (request.method !== "POST") {
      return jsonResponse({
        success: true,
        status: "online",
        service: "Enterprise ICP Intelligence Engine",
        request_id: requestId,
        protocol: "Send a POST request with prospect text or JSON payload."
      });
    }

    let payload = {};
    try {
      payload = await request.json();
    } catch (err) {
      return jsonResponse({
        success: false,
        error: {
          code: "INVALID_JSON_PAYLOAD",
          message: "Request body must be valid JSON.",
          request_id: requestId
        }
      }, 400);
    }

    const prospectInput = (payload.text || payload.prospect_text || "").trim() || JSON.stringify(payload);
    if (!prospectInput || prospectInput === "{}") {
      return jsonResponse({
        success: false,
        error: {
          code: "EMPTY_PROSPECT_INPUT",
          message: "Prospect text or account payload is required.",
          request_id: requestId
        }
      }, 400);
    }

    const dealSize = Number(payload.deal_size_usd) || 50000;
    const model = env.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct";

    // 1. Check if Cloudflare Workers AI binding is attached
    if (!env.AI) {
      return jsonResponse({
        success: false,
        error: {
          code: "AI_BINDING_MISSING",
          message: "Cloudflare Workers AI binding [ai] is not bound. Ensure [ai] binding = 'AI' is in wrangler.toml.",
          request_id: requestId
        }
      }, 500);
    }

    // 2. Strict Evidence Extraction System Prompt
    const systemPrompt = `You are an expert Enterprise B2B Revenue Intelligence Engine.
Analyze the prospect input text and extract structured evidence for ICP qualification.
DO NOT fabricate details. If a field is not present or cannot be inferred from context, mark it as null or UNKNOWN.

EVALUATION DIMENSIONS (Score 0-100 where evidence exists, or null if UNKNOWN):
1. Firmographics: Headcount, revenue, operational scale, vertical fit.
2. Technographics: Current software stack, data infrastructure, sophistication.
3. Intent & Urgency: Active RFP, buying timeline, hiring expansion, pain point urgency.
4. Buyer Readiness & Authority: Decision maker title, VP/C-suite authority, budget availability.
5. Commercial Value & Expansion: Potential contract scale, multi-department expansion.

EVIDENCE STATUS RULES:
- "VERIFIED": Explicitly stated in the text with clear numbers/titles.
- "INFERRED": Logically deduced from industry, company description, or role context.
- "UNKNOWN": Information is missing, unclear, or unverified.

DISQUALIFICATION RULES:
- Mark is_disqualified = true if the contact is clearly a student, personal user, job seeker, or non-commercial inquiry.

SCHEMA TO RETURN (Strict JSON only):
{
  "account": {
    "company_name": "string or null",
    "domain": "string or null",
    "contact_name": "string or null",
    "job_title": "string or null",
    "industry": "string or null",
    "scale": "string or null",
    "tech_stack": "string or null",
    "intent_timeline": "string or null"
  },
  "evidence": {
    "firmographic": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "string explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "technographic": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "string explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "intent": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "string explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "readiness": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "string explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "value": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "string explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    }
  },
  "is_disqualified": boolean,
  "disqualification_reason": "string (empty if eligible)",
  "strategy": {
    "value_wedge": "string (sharpest positioning angle)",
    "outreach_hook": "string (1-sentence cold email opener)"
  },
  "discovery_questions": ["string (questions for missing UNKNOWN attributes)"],
  "key_strengths": ["string (evidence 1)", "string (evidence 2)"],
  "key_risks": ["string (risk 1)"]
}
Respond ONLY with valid JSON.`;

    let aiRaw = null;
    let aiErrorMsg = "";
    let aiResult = null;

    try {
      const aiResponse = await env.AI.run(model, {
        prompt: `${systemPrompt}\n\nProspect Text to Evaluate:\n${prospectInput}\n\nTarget Contract Size: $${dealSize.toLocaleString()} USD`
      });
      aiRaw = typeof aiResponse === "string" ? aiResponse : aiResponse.response || JSON.stringify(aiResponse);
      aiResult = parseJsonSafely(aiRaw);
    } catch (aiError) {
      aiErrorMsg = aiError.message || String(aiError);
      console.error(`[Workers AI Error][${requestId}]:`, aiErrorMsg);
    }

    // 3. Handle inference failure
    if (!aiResult) {
      return jsonResponse({
        success: false,
        error: {
          code: aiErrorMsg ? "AI_EXECUTION_FAILED" : "AI_PARSE_FAILED",
          message: aiErrorMsg || "Failed to parse structured JSON from Workers AI output.",
          request_id: requestId,
          raw_output: aiRaw ? aiRaw.substring(0, 500) : null
        }
      }, 502);
    }

    // 4. Sanitize and Validate AI evidence output
    const account = aiResult.account || {};
    const rawEvidence = aiResult.evidence || {};

    function sanitizePillar(pillarKey, fallbackScore = null) {
      const p = rawEvidence[pillarKey] || {};
      const score = clampScore(p.score !== undefined ? p.score : fallbackScore);
      const status = ["VERIFIED", "INFERRED", "UNKNOWN"].includes(p.status) ? p.status : (score !== null ? "INFERRED" : "UNKNOWN");
      const confidence = status === "UNKNOWN" ? 0.0 : Math.max(0.0, Math.min(1.0, Number(p.confidence) || 0.5));
      return {
        score: score,
        status: status,
        confidence: Number(confidence.toFixed(2)),
        rationale: String(p.rationale || ""),
        evidence_points: Array.isArray(p.evidence_points) ? p.evidence_points.map(String) : [],
        missing_points: Array.isArray(p.missing_points) ? p.missing_points.map(String) : []
      };
    }

    const validatedEvidence = {
      firmographic: sanitizePillar("firmographic"),
      technographic: sanitizePillar("technographic"),
      intent: sanitizePillar("intent"),
      readiness: sanitizePillar("readiness"),
      value: sanitizePillar("value")
    };

    return jsonResponse({
      success: true,
      request_id: requestId,
      account: {
        company_name: account.company_name || null,
        domain: account.domain || null,
        contact_name: account.contact_name || null,
        job_title: account.job_title || null,
        industry: account.industry || null,
        scale: account.scale || null,
        tech_stack: account.tech_stack || null,
        intent_timeline: account.intent_timeline || null
      },
      evidence: validatedEvidence,
      is_disqualified: Boolean(aiResult.is_disqualified),
      disqualification_reason: String(aiResult.disqualification_reason || ""),
      strategy: {
        value_wedge: String(aiResult.strategy?.value_wedge || ""),
        outreach_hook: String(aiResult.strategy?.outreach_hook || "")
      },
      discovery_questions: Array.isArray(aiResult.discovery_questions) ? aiResult.discovery_questions.map(String) : [],
      key_strengths: Array.isArray(aiResult.key_strengths) ? aiResult.key_strengths.map(String) : [],
      key_risks: Array.isArray(aiResult.key_risks) ? aiResult.key_risks.map(String) : []
    });
  }
};

