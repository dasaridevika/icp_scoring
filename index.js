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

function parseJsonSafely(raw) {
  if (!raw) return null;
  if (typeof raw === "object") return raw;
  const rawText = String(raw).trim();
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

// Live Web & SerpAPI Enrichment Helper
async function searchWebIntelligence(prospectText, env, request = null, payload = null) {
  let webData = "";

  // 1. Extract domain or company keywords for search query
  const domainMatch = prospectText.match(/(?:https?:\/\/)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)/i);
  const emailMatch = prospectText.match(/@([a-zA-Z0-9-]+\.[a-zA-Z]{2,})/i);
  const companyMatch = prospectText.match(/Company[:\s]+([^\n\r,]+)/i);

  const rawDomain = (domainMatch ? domainMatch[1] : (emailMatch ? emailMatch[1] : "")).toLowerCase();
  const domain = (rawDomain.includes("gmail") || rawDomain.includes("yahoo") || rawDomain.includes("hotmail") || rawDomain.includes("outlook")) ? "" : rawDomain;
  const company = companyMatch ? companyMatch[1].trim() : "";

  const querySubject = company || domain;
  if (!querySubject) return "";

  // 2. SerpAPI Integration (env, request header, or payload)
  const serpApiKey = env.SERPAPI_API_KEY || env.SERP_API_KEY || request?.headers?.get("X-SerpApi-Key") || payload?.serpapi_api_key;
  if (serpApiKey) {
    try {
      const serpUrl = `https://serpapi.com/search.json?q=${encodeURIComponent(querySubject + " company overview headcount revenue industry")}&api_key=${serpApiKey}&num=3`;
      const serpRes = await fetch(serpUrl, { cf: { cacheTtl: 86400 } });
      if (serpRes.ok) {
        const serpData = await serpRes.json();
        const organic = serpData.organic_results || [];
        const snippets = organic.slice(0, 3).map(r => `• ${r.title}: ${r.snippet || ""}`).join("\n");
        if (snippets) {
          webData += `\n[SerpAPI Live Web Search for "${querySubject}"]:\n${snippets}`;
        }
      }
    } catch (serpErr) {
      console.warn("SerpAPI search warning:", serpErr);
    }
  }

  // 3. Serper.dev Integration (env, request header, or payload)
  const serperKey = env.SERPER_API_KEY || request?.headers?.get("X-Serper-Key") || payload?.serper_api_key;
  if (!webData && serperKey) {
    try {
      const serperRes = await fetch("https://google.serper.dev/search", {
        method: "POST",
        headers: { "X-API-KEY": serperKey, "Content-Type": "application/json" },
        body: JSON.stringify({ q: `${querySubject} company overview headcount revenue industry`, num: 3 }),
        cf: { cacheTtl: 86400 }
      });
      if (serperRes.ok) {
        const serperData = await serperRes.json();
        const organic = serperData.organic || [];
        const snippets = organic.slice(0, 3).map(r => `• ${r.title}: ${r.snippet || ""}`).join("\n");
        if (snippets) {
          webData += `\n[Serper Live Web Search for "${querySubject}"]:\n${snippets}`;
        }
      }
    } catch (serperErr) {
      console.warn("Serper search warning:", serperErr);
    }
  }

  // 4. Direct Homepage Scraping (Free & Fast fallback if domain found)
  if (!webData && domain && !domain.includes("blackridgeresearch.com")) {
    try {
      const siteRes = await fetch(`https://${domain}`, {
        headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
        cf: { cacheTtl: 86400 }
      });
      if (siteRes.ok) {
        const html = await siteRes.text();
        const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
        const metaDescMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i);
        const title = titleMatch ? titleMatch[1].trim() : "";
        const desc = metaDescMatch ? metaDescMatch[1].trim() : "";
        if (title || desc) {
          webData += `\n[Direct Live Website Meta for ${domain}]:\nTitle: ${title}\nDescription: ${desc}`;
        }
      }
    } catch (siteErr) {}
  }

  return webData;
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

    try {
      let payload = {};
      let prospectInput = "";
      let dealSize = 50000;

      try {
        const contentType = request.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          payload = await request.json();
          prospectInput = (payload.text || payload.prospect_text || "").trim() || JSON.stringify(payload);
          dealSize = Number(payload.deal_size_usd) || 50000;
        } else {
          const rawText = await request.text();
          try {
            payload = JSON.parse(rawText);
            prospectInput = (payload.text || payload.prospect_text || rawText).trim();
            dealSize = Number(payload.deal_size_usd) || 50000;
          } catch (e) {
            prospectInput = rawText.trim();
          }
        }
      } catch (err) {
        try {
          prospectInput = (await request.text()).trim();
        } catch (e2) {}
      }

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
    
    // Standard production model with exactly 1 fallback
    const primaryModel = env.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct";
    const candidateModels = [primaryModel, "@cf/meta/llama-3.2-3b-instruct"];

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
    const systemPrompt = `You are an elite Senior Director of RevOps & Enterprise GTM Strategist.
Analyze the prospect input text and generate a structured, highly personalized B2B intelligence dossier for ICP qualification.
DO NOT fabricate details. If a field is not present or cannot be inferred from context, mark it as null or UNKNOWN.

EVALUATION & SCORING RULES (Score 0-100 based on verified or inferred evidence):
1. Firmographics (0-100): Headcount, revenue, corporate status, industry alignment (65-90 for verified B2B/industrial corporations). Mark "VERIFIED" if exact numbers given, "INFERRED" if established corporate firm.
2. Technographics (0-100): Current stack compatibility and data infrastructure (55-80 inferred for established industry operations).
3. Intent & Urgency (0-100): Active inquiry, inbound callback request, scheduled appointment date/time, RFP, or buying timeline (Score 75-95 for direct callback requests or stated expansion projects).
4. Buyer Readiness & Authority (0-100): Corporate business email domain (@company.com), commercial/procurement role, or decision-maker mandate (Score 65-85).
5. Commercial Value & Expansion (0-100): Contract ARR potential, multi-region or solar/product division expansion (Score 65-85).

EVIDENCE STATUS RULES:
- "VERIFIED": Explicitly stated in the text with clear numbers/dates/titles.
- "INFERRED": Logically deduced from industry, company description, corporate domain, or role context.
- "UNKNOWN": Only use if the text provides zero commercial context.

DISQUALIFICATION RULES:
- Mark is_disqualified = true only if the contact is clearly a student, personal user (@gmail/@yahoo for non-business), job seeker, or non-commercial spam.

STRATEGIC COPYWRITING REQUIREMENTS:
- outreach_hook: Write a compelling, bespoke 1-sentence cold email opening line tailored directly to the contact (or company if contact is unknown). Reference their specific role, tech stack, scale, or stated initiative to prove deep contextual relevance. NEVER output a generic phrase or lazy snippet. Example: "Hi Sarah, with CloudScale Dynamics planning a Q3 rollout across 180 enterprise reps, I wanted to share how we integrate directly with Snowflake and Salesforce to replace legacy pipeline analytics without workflow disruption."
- value_wedge: A sharp 1-2 sentence executive positioning thesis that articulates the exact business differentiation and ROI for their specific infrastructure and team size.
- key_strengths: 2 to 4 concrete, data-backed bullet points highlighting specific numbers, tech stack tools, or buyer signals found in the input.
- key_risks: 1 to 3 realistic enterprise implementation or discovery risks (e.g. legacy data migration, enterprise change management, security sign-off).
- discovery_questions: 2 to 3 sharp, consultative discovery questions targeted at uncovering gaps or accelerating the buying cycle.

SCHEMA TO RETURN (Strict JSON only):
{
  "account": {
    "company_name": "string or null",
    "domain": "string or null",
    "contact_name": "string or null",
    "job_title": "string or null",
    "industry": "string or null",
    "location": "string (headquarters city, state, or country) or null",
    "scale": "string or null",
    "tech_stack": "string or null",
    "intent_timeline": "string or null"
  },
  "evidence": {
    "firmographic": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "clear concise explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "technographic": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "clear concise explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "intent": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "clear concise explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "readiness": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "clear concise explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    },
    "value": {
      "score": number 0-100 or null,
      "status": "VERIFIED" | "INFERRED" | "UNKNOWN",
      "confidence": number 0.0-1.0,
      "rationale": "clear concise explanation",
      "evidence_points": ["string"],
      "missing_points": ["string"]
    }
  },
  "is_disqualified": boolean,
  "disqualification_reason": "string (empty if eligible)",
  "strategy": {
    "value_wedge": "string (sharp executive value proposition)",
    "outreach_hook": "string (personalized 1-sentence cold email opener)"
  },
  "discovery_questions": ["string"],
  "key_strengths": ["string"],
  "key_risks": ["string"]
}
Respond ONLY with valid JSON.`;

    // Enrich prospect data with SerpAPI / Live Web Intelligence
    const liveWebContext = await searchWebIntelligence(prospectInput, env, request, payload);
    const enrichedProspect = liveWebContext ? `${prospectInput}\n\n--- LIVE WEB & SEARCH INTELLIGENCE ---${liveWebContext}\n--------------------------------------` : prospectInput;

    const userPromptContent = `Prospect Text to Evaluate:\n${enrichedProspect}\n\nTarget Contract Size: $${dealSize.toLocaleString()} USD`;

    let aiRaw = null;
    let aiErrorMsg = "";
    let aiResult = null;

    // Try candidate models in sequence
    for (const model of candidateModels) {
      try {
        let aiResponse;
        try {
          // 1. Try standard OpenAI-compatible messages format first
          aiResponse = await env.AI.run(model, {
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: userPromptContent }
            ],
            max_tokens: 2048,
            temperature: 0.1
          });
        } catch (chatErr) {
          // 2. Fall back to direct prompt string format if messages format rejected
          aiResponse = await env.AI.run(model, {
            prompt: `${systemPrompt}\n\n${userPromptContent}`,
            max_tokens: 2048,
            temperature: 0.1
          });
        }

        if (typeof aiResponse === "string") {
          aiRaw = aiResponse;
        } else if (aiResponse && typeof aiResponse.response === "string") {
          aiRaw = aiResponse.response;
        } else {
          aiRaw = JSON.stringify(aiResponse || "");
        }

        aiResult = parseJsonSafely(aiRaw);
        if (aiResult) {
          break; // Successfully got structured JSON
        }
      } catch (aiError) {
        aiErrorMsg = aiError.message || String(aiError);
        console.warn(`[Workers AI Warning][${model}][${requestId}]:`, aiErrorMsg);
      }
    }

    // 3. Handle inference failure
    if (!aiResult) {
      const safeRawStr = typeof aiRaw === "string" ? aiRaw : JSON.stringify(aiRaw || "");
      return jsonResponse({
        success: false,
        error: {
          code: aiErrorMsg ? "AI_EXECUTION_FAILED" : "AI_PARSE_FAILED",
          message: aiErrorMsg || "Failed to parse structured JSON from Workers AI output.",
          request_id: requestId,
          raw_output: safeRawStr ? safeRawStr.substring(0, 500) : null
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

    function cleanStr(v) {
      if (!v) return null;
      const s = String(v).trim();
      if (["null", "none", "undefined", "n/a", ""].includes(s.toLowerCase())) return null;
      return s;
    }

    return jsonResponse({
      success: true,
      request_id: requestId,
      account: {
        company_name: cleanStr(account.company_name),
        domain: cleanStr(account.domain),
        contact_name: cleanStr(account.contact_name),
        job_title: cleanStr(account.job_title),
        industry: cleanStr(account.industry),
        location: cleanStr(account.location),
        scale: cleanStr(account.scale),
        tech_stack: cleanStr(account.tech_stack),
        intent_timeline: cleanStr(account.intent_timeline)
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
    } catch (fatalErr) {
      return jsonResponse({
        success: false,
        error: {
          code: "WORKER_INTERNAL_ERROR",
          message: fatalErr.message || String(fatalErr),
          request_id: requestId
        }
      }, 500);
    }
  }
};

