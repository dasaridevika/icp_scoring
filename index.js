// Enterprise ICP Revenue Intelligence - Cloudflare Worker AI Edge Engine
// GTM Partners Polarized Forced-Choice Framework (-5, -3, -1, +1, +3, +5)

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
};

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

export default {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }
    if (request.method !== "POST") {
      return jsonResponse({
        status: "online",
        service: "Enterprise ICP Intelligence Engine (GTM Partners Model)",
        protocol: "Send a POST request with prospect text or JSON payload."
      });
    }

    let payload = {};
    try {
      payload = await request.json();
    } catch (err) {
      return jsonResponse({ error: "Invalid JSON request payload." }, 400);
    }

    const prospectInput = (payload.text || payload.prospect_text || "").trim() || JSON.stringify(payload);
    const dealSize = Number(payload.deal_size_usd) || 50000;
    const model = env.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct";

    // 1. Check if Cloudflare Workers AI binding is attached
    if (!env.AI) {
      return jsonResponse({
        ai_status: "binding_missing",
        error: "Cloudflare Workers AI binding [ai] is not bound. Ensure [ai] binding = 'AI' is in wrangler.toml.",
        company_name: null,
        contact_name: null,
        job_title: null,
        industry: null,
        is_disqualified: false,
        disqualification_reason: "",
        ratings: {
          firmographic: -1,
          technographic: -1,
          intent: -1,
          persona: -1
        },
        rationales: {
          firmographic: "AI binding unavailable. Field marked as -1 (Uncertainty).",
          technographic: "AI binding unavailable. Field marked as -1 (Uncertainty).",
          intent: "AI binding unavailable. Field marked as -1 (Uncertainty).",
          persona: "AI binding unavailable. Field marked as -1 (Uncertainty)."
        },
        discovery_questions: [
          "What is the official operating company name and target industry?",
          "What is your target timeline for evaluating a solution?"
        ]
      }, 500);
    }

    // 2. Strict GTM Partners Polarized System Prompt
    const systemPrompt = `You are an expert Enterprise B2B Revenue Intelligence Engine implementing the GTM Partners ICP Scoring Framework.
Analyze the prospect text and evaluate the 4 ICP Pillars using the forced-choice polarized rating scale:

RATING SCALE (Use ONLY these exact integers: -5, -3, -1, +1, +3, +5):
+5: High Potential for Growth / Rapid Expansion / Ideal ICP
+3: Clear Advantages / Strong Product-Market Fit
+1: Serviceable / Limited Growth Potential
-1: Uncertainty / Missing Data / Unverified in Inbound Context
-3: High Resource Drain / Sub-Scale Economics / Complex Custom Needs
-5: High Churn Risk / Non-Commercial / Anti-ICP / Disqualified

PILLARS TO EVALUATE:
1. Firmographics: Headcount scale, revenue (ARR), target vertical, operating model.
2. Technographics: Technology stack sophistication, CRM/data warehouse infrastructure.
3. Intent & Timing: Active RFP, buying urgency, expansion triggers, hiring momentum.
4. Buyer Persona & Authority: VP/C-Suite budget authority (mark students, job seekers, and academic inquiries as -5).

EXTRACTION RULES:
- If company name, contact, job title, or industry is not explicitly mentioned, return null (do NOT invent placeholder names).
- If any pillar has missing or unknown information, rate it as -1 (Uncertainty) and generate a discovery question to qualify it on the call.

Return a strict JSON object with EXACTLY this schema:
{
  "company_name": "string or null",
  "contact_name": "string or null",
  "job_title": "string or null",
  "industry": "string or null",
  "is_disqualified": boolean,
  "disqualification_reason": "string (empty if eligible)",
  "ratings": {
    "firmographic": 5,
    "technographic": 3,
    "intent": 1,
    "persona": -1
  },
  "rationales": {
    "firmographic": "string (1-2 sentences explaining rating)",
    "technographic": "string (1-2 sentences explaining rating)",
    "intent": "string (1-2 sentences explaining rating)",
    "persona": "string (1-2 sentences explaining rating)"
  },
  "strategy": {
    "value_wedge": "string (sharpest positioning angle)",
    "outreach_hook": "string (1-sentence cold email opener)"
  },
  "discovery_questions": [
    "string (question to qualify missing -1 attributes)"
  ],
  "key_strengths": ["string (evidence 1)", "string (evidence 2)"],
  "key_risks": ["string (risk 1)"]
}
Respond ONLY with pure valid JSON.`;

    let aiResult = null;
    let aiRaw = null;
    let aiErrorMsg = "";

    try {
      const aiResponse = await env.AI.run(model, {
        prompt: `${systemPrompt}\n\nProspect Text to Evaluate:\n${prospectInput}\n\nTarget Contract Size: $${dealSize.toLocaleString()} USD`
      });
      const rawText = typeof aiResponse === "string" ? aiResponse : aiResponse.response || JSON.stringify(aiResponse);
      aiRaw = rawText;
      aiResult = parseJsonSafely(rawText);
    } catch (aiError) {
      aiErrorMsg = aiError.message || String(aiError);
      console.error("[Workers AI Run Error]:", aiErrorMsg);
    }

    // 3. Handle parse or execution failure with explicit error surfacing
    if (!aiResult) {
      return jsonResponse({
        ai_status: "inference_failed",
        ai_error: aiErrorMsg || "Failed to parse structured JSON from LLM output.",
        raw_output: aiRaw,
        company_name: null,
        contact_name: null,
        job_title: null,
        industry: null,
        is_disqualified: false,
        disqualification_reason: "",
        ratings: {
          firmographic: -1,
          technographic: -1,
          intent: -1,
          persona: -1
        },
        rationales: {
          firmographic: "AI inference failed. Field marked as -1 (Uncertainty).",
          technographic: "AI inference failed. Field marked as -1 (Uncertainty).",
          intent: "AI inference failed. Field marked as -1 (Uncertainty).",
          persona: "AI inference failed. Field marked as -1 (Uncertainty)."
        },
        strategy: {
          value_wedge: "Deliver tailored enterprise intelligence to accelerate strategic initiatives.",
          outreach_hook: "Reaching out regarding your growth roadmap and operational initiatives."
        },
        discovery_questions: [
          "What is your target timeline for evaluating and deploying a solution?",
          "What core CRM, data warehouse, or ERP tools do you currently operate?"
        ],
        key_strengths: [],
        key_risks: ["AI inference unverified - requires manual discovery."]
      }, 502);
    }

    // 4. Validate and Clamp Ratings to valid GTM Partners values: {-5, -3, -1, +1, +3, +5}
    const ALLOWED_GTM_RATINGS = [-5, -3, -1, 1, 3, 5];
    function sanitizeGtmRating(val) {
      const num = Number(val);
      if (ALLOWED_GTM_RATINGS.includes(num)) return num;
      // Closest GTM rating mapping if model output is outside
      if (num >= 4) return 5;
      if (num >= 2) return 3;
      if (num >= 0) return 1;
      if (num >= -2) return -1;
      if (num >= -4) return -3;
      return -5;
    }

    const ratings = aiResult.ratings || {};
    const fRating = sanitizeGtmRating(ratings.firmographic ?? -1);
    const tRating = sanitizeGtmRating(ratings.technographic ?? -1);
    const iRating = sanitizeGtmRating(ratings.intent ?? -1);
    const pRating = sanitizeGtmRating(ratings.persona ?? -1);

    const isDisqualified = Boolean(aiResult.is_disqualified) || pRating === -5;

    // GTM Partners Mathematical Weighted Formula (Weights: Firmo 30%, Techno 25%, Intent 25%, Persona 20%)
    const rawGtmScore = isDisqualified ? -5.0 : ((fRating * 0.30) + (tRating * 0.25) + (iRating * 0.25) + (pRating * 0.20));
    // Normalized 0 to 100 score: (Raw - (-5)) / 10 * 100
    const normalizedScore = isDisqualified ? 12 : Math.round(Math.max(0, Math.min(100, (rawGtmScore + 5.0) * 10.0)));

    return jsonResponse({
      ai_status: "success",
      company_name: aiResult.company_name || null,
      contact_name: aiResult.contact_name || null,
      job_title: aiResult.job_title || null,
      industry: aiResult.industry || null,
      is_disqualified: isDisqualified,
      disqualification_reason: aiResult.disqualification_reason || (isDisqualified ? "Non-commercial lead or anti-ICP role" : ""),
      ratings: {
        firmographic: fRating,
        technographic: tRating,
        intent: iRating,
        persona: pRating
      },
      raw_gtm_weighted_score: Number(rawGtmScore.toFixed(2)),
      final_icp_score: normalizedScore,
      rationales: aiResult.rationales || {},
      strategy: aiResult.strategy || {},
      discovery_questions: aiResult.discovery_questions || [],
      key_strengths: aiResult.key_strengths || [],
      key_risks: aiResult.key_risks || []
    });
  }
};
