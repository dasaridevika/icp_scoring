const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID, X-SerpApi-Key, X-Serper-Key"
};

function generateRequestId() {
  return "req_" + Date.now() + "_" + Math.random().toString(36).substring(2, 9);
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
    const jsonMatch = rawText.match(/`(?:json)?\s*([\s\S]*?)\s*`/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[1]);
      } catch (err) {}
    }
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
  return Math.max(0, Math.min(100, Math.round(Number(val))));
}

function cleanStr(v) {
  if (!v) return null;
  const s = String(v).trim();
  if (["null", "none", "undefined", "n/a", ""].includes(s.toLowerCase())) return null;
  return s;
}

async function searchWebIntelligence(prospectText, env, request = null, payload = null) {
  let webData = "";
  const domainMatch = prospectText.match(/(?:https?:\/\/)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)/i);
  const emailMatch = prospectText.match(/@([a-zA-Z0-9-]+\.[a-zA-Z]{2,})/i);
  const companyMatch = prospectText.match(/Company[:\s]+([^\n\r,]+)/i);
  const rawDomain = (domainMatch ? domainMatch[1] : emailMatch ? emailMatch[1] : "").toLowerCase();
  const domain = rawDomain.includes("gmail") || rawDomain.includes("yahoo") || rawDomain.includes("hotmail") || rawDomain.includes("outlook") ? "" : rawDomain;
  const company = companyMatch ? companyMatch[1].trim() : (payload?.company_name || payload?.company || "");
  const querySubject = company || domain;
  
  if (!querySubject) return "";

  const serpApiKey = env?.SERPAPI_API_KEY || env?.SERP_API_KEY || request?.headers?.get("X-SerpApi-Key") || payload?.serpapi_api_key;
  if (serpApiKey) {
    try {
      const serpUrl = "https://serpapi.com/search.json?q=" + encodeURIComponent(querySubject + " company overview headcount revenue industry branches locations") + "&api_key=" + serpApiKey + "&num=3";
      const serpRes = await fetch(serpUrl, { cf: { cacheTtl: 86400 } });
      if (serpRes.ok) {
        const serpData = await serpRes.json();
        const organic = serpData.organic_results || [];
        const snippets = organic.slice(0, 3).map((r) => "• " + r.title + ": " + (r.snippet || "")).join("\n");
        if (snippets) {
          webData += "\n[SerpAPI Live Web Search for \"" + querySubject + "\"]:\n" + snippets;
        }
      }
    } catch (serpErr) {
      console.warn("SerpAPI search warning:", serpErr);
    }
  }

  const serperKey = env?.SERPER_API_KEY || request?.headers?.get("X-Serper-Key") || payload?.serper_api_key;
  if (!webData && serperKey) {
    try {
      const serperRes = await fetch("https://google.serper.dev/search", {
        method: "POST",
        headers: { "X-API-KEY": serperKey, "Content-Type": "application/json" },
        body: JSON.stringify({ q: querySubject + " company overview headcount revenue industry branches locations", num: 3 }),
        cf: { cacheTtl: 86400 }
      });
      if (serperRes.ok) {
        const serperData = await serperRes.json();
        const organic = serperData.organic || [];
        const snippets = organic.slice(0, 3).map((r) => "• " + r.title + ": " + (r.snippet || "")).join("\n");
        if (snippets) {
          webData += "\n[Serper Live Web Search for \"" + querySubject + "\"]:\n" + snippets;
        }
      }
    } catch (serperErr) {
      console.warn("Serper search warning:", serperErr);
    }
  }

  if (!webData && domain && !domain.includes("blackridgeresearch.com")) {
    try {
      const siteRes = await fetch("https://" + domain, {
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
          webData += "\n[Direct Live Website Meta for " + domain + "]:\nTitle: " + title + "\nDescription: " + desc;
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

    if (request.method === "GET") {
      return jsonResponse({
        success: true,
        status: "active",
        service: "Enterprise ICP Revenue Intelligence Engine",
        version: "3.0-CF-AI",
        request_id: requestId,
        capabilities: [
          "Cloudflare Workers AI Llama-3.1/3.2 RevOps Intelligence",
          "Multi-Branch & Regional Footprint Analysis",
          "Live Search & Domain Enrichment (SerpAPI, Serper, Site Meta)",
          "5-Pillar Evidence Scoring (Firmographic, Technographic, Intent, Readiness, Value)",
          "Dynamic Priority Tier Routing & SLA Extraction"
        ],
        protocol: "Send a POST request with prospect text, lead JSON payload, or form data."
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
          prospectInput = (payload.text || payload.prospect_text || "").trim();
          if (!prospectInput) {
            prospectInput = JSON.stringify(payload, null, 2);
          }
          dealSize = Number(payload.target_deal_size_usd || payload.deal_size || payload.deal_size_usd) || 50000;
        } else {
          const rawText = await request.text();
          try {
            payload = JSON.parse(rawText);
            prospectInput = (payload.text || payload.prospect_text || rawText).trim();
            dealSize = Number(payload.target_deal_size_usd || payload.deal_size || payload.deal_size_usd) || 50000;
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

      const primaryModel = env?.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct";
      const candidateModels = [primaryModel, "@cf/meta/llama-3.2-3b-instruct"];

      if (!env?.AI) {
        return jsonResponse({
          success: false,
          error: {
            code: "AI_BINDING_MISSING",
            message: "Cloudflare Workers AI binding [ai] is not bound in wrangler.toml.",
            request_id: requestId
          }
        }, 500);
      }

      const systemPrompt = "You are an elite Senior Director of RevOps & Enterprise GTM Strategist.\n" +
        "Analyze the prospect input text and generate a structured, highly personalized B2B intelligence dossier for ICP qualification.\n" +
        "DO NOT fabricate details. If a field is not present or cannot be inferred from context, mark it as null or UNKNOWN.\n\n" +
        "EVALUATION & SCORING RULES (Score 0-100 based on verified or inferred evidence):\n" +
        "1. Firmographics (0-100): Headcount, revenue, corporate status, headquarters, and multi-branch regional hubs (65-90 for verified B2B/industrial corporations). Mark \"VERIFIED\" if exact numbers given, \"INFERRED\" if established corporate firm.\n" +
        "2. Technographics (0-100): Current stack compatibility, cloud infrastructure, and modern data stack (55-85 inferred for established operations).\n" +
        "3. Intent & Urgency (0-100): Active inquiry, inbound callback request, RFP, scheduled meeting, or migration timeline (Score 75-95 for direct callback requests or stated project timelines).\n" +
        "4. Buyer Readiness & Authority (0-100): Corporate business email domain (@company.com), C-Suite / VP / Director procurement role, or signatory authority (Score 65-85).\n" +
        "5. Commercial Value & Expansion (0-100): Contract ARR potential, multi-region branch footprint, or product division expansion (Score 65-90).\n\n" +
        "EVIDENCE STATUS RULES:\n" +
        "- \"VERIFIED\": Explicitly stated in the text with clear numbers/dates/locations/titles.\n" +
        "- \"INFERRED\": Logically deduced from industry, company description, corporate domain, or role context.\n" +
        "- \"UNKNOWN\": Only use if the text provides zero commercial context.\n\n" +
        "DISQUALIFICATION RULES:\n" +
        "- Mark is_disqualified = true only if the contact is clearly a student, personal freemail user (@gmail/@yahoo for non-business), job seeker, or sanctioned territory.\n\n" +
        "STRATEGIC COPYWRITING REQUIREMENTS:\n" +
        "- outreach_hook: Write a compelling, bespoke 1-sentence cold email opening line tailored directly to the contact (or company). Reference their specific role, tech stack, scale, multi-branch footprint, or stated initiative. NEVER output a generic phrase.\n" +
        "- value_wedge: A sharp 1-2 sentence executive positioning thesis articulating business differentiation and ROI for their specific infrastructure and scale.\n" +
        "- key_strengths: 2 to 4 concrete, data-backed bullet points highlighting specific numbers, tech stack tools, branch locations, or buyer signals found in the input.\n" +
        "- key_risks: 1 to 3 realistic enterprise implementation or discovery risks.\n" +
        "- discovery_questions: 2 to 3 sharp, consultative discovery questions targeted at accelerating the deal.\n\n" +
        "SCHEMA TO RETURN (Strict JSON only):\n" +
        "{\n" +
        "  \"account\": {\n" +
        "    \"company_name\": \"string or null\",\n" +
        "    \"domain\": \"string or null\",\n" +
        "    \"contact_name\": \"string or null\",\n" +
        "    \"job_title\": \"string or null\",\n" +
        "    \"industry\": \"string or null\",\n" +
        "    \"sub_vertical\": \"string or null\",\n" +
        "    \"location\": \"string (headquarters city, state, or country) or null\",\n" +
        "    \"branch_locations\": [\"string (additional branch offices / hubs)\"],\n" +
        "    \"geographic_reach\": \"Global Multi-Region Enterprise | Cross-Border Multi-Branch | Single-Market Hub\",\n" +
        "    \"scale\": \"string or null\",\n" +
        "    \"tech_stack\": \"string or null\",\n" +
        "    \"intent_timeline\": \"string or null\"\n" +
        "  },\n" +
        "  \"evidence\": {\n" +
        "    \"firmographic\": { \"score\": 0-100, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": 0.0-1.0, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"technographic\": { \"score\": 0-100, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": 0.0-1.0, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"intent\": { \"score\": 0-100, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": 0.0-1.0, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"readiness\": { \"score\": 0-100, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": 0.0-1.0, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"value\": { \"score\": 0-100, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": 0.0-1.0, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] }\n" +
        "  },\n" +
        "  \"is_disqualified\": false,\n" +
        "  \"disqualification_reason\": \"string\",\n" +
        "  \"strategy\": { \"value_wedge\": \"string\", \"outreach_hook\": \"string\" },\n" +
        "  \"discovery_questions\": [\"string\"],\n" +
        "  \"key_strengths\": [\"string\"],\n" +
        "  \"key_risks\": [\"string\"]\n" +
        "}\nRespond ONLY with valid JSON.";

      const liveWebContext = await searchWebIntelligence(prospectInput, env, request, payload);
      const enrichedProspect = liveWebContext ? prospectInput + "\n\n--- LIVE WEB & SEARCH INTELLIGENCE ---" + liveWebContext + "\n--------------------------------------" : prospectInput;

      const userPromptContent = "Prospect Text / Payload to Evaluate:\n" + enrichedProspect + "\nTarget Contract Size: $" + dealSize.toLocaleString() + " USD";

      let aiRaw = null;
      let aiErrorMsg = "";
      let aiResult = null;

      for (const model of candidateModels) {
        try {
          let aiResponse;
          try {
            aiResponse = await env.AI.run(model, {
              messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPromptContent }
              ],
              max_tokens: 2048,
              temperature: 0.1
            });
          } catch (chatErr) {
            aiResponse = await env.AI.run(model, {
              prompt: systemPrompt + "\n\n" + userPromptContent,
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
          if (aiResult) break;
        } catch (aiError) {
          aiErrorMsg = aiError.message || String(aiError);
          console.warn("[Workers AI Warning][" + model + "][" + requestId + "]:", aiErrorMsg);
        }
      }

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

      const account = aiResult.account || {};
      const rawEvidence = aiResult.evidence || {};

      function sanitizePillar(pillarKey, fallbackScore = null) {
        const p = rawEvidence[pillarKey] || {};
        const score = clampScore(p.score !== undefined ? p.score : fallbackScore);
        const status = ["VERIFIED", "INFERRED", "UNKNOWN"].includes(p.status) ? p.status : (score !== null ? "INFERRED" : "UNKNOWN");
        const confidence = status === "UNKNOWN" ? 0 : Math.max(0, Math.min(1, Number(p.confidence) || 0.75));
        return {
          score,
          status,
          confidence: Number(confidence.toFixed(2)),
          rationale: String(p.rationale || ""),
          evidence_points: Array.isArray(p.evidence_points) ? p.evidence_points.map(String) : [],
          missing_points: Array.isArray(p.missing_points) ? p.missing_points.map(String) : []
        };
      }

      const validatedEvidence = {
        firmographic: sanitizePillar("firmographic", 70),
        technographic: sanitizePillar("technographic", 65),
        intent: sanitizePillar("intent", 75),
        readiness: sanitizePillar("readiness", 70),
        value: sanitizePillar("value", 70)
      };

      const weights = { firmographic: 0.25, technographic: 0.20, intent: 0.25, readiness: 0.15, value: 0.15 };
      let compositeScore = 0;
      let totalWeight = 0;

      for (const [key, w] of Object.entries(weights)) {
        const pScore = validatedEvidence[key].score;
        if (pScore !== null) {
          compositeScore += pScore * w;
          totalWeight += w;
        }
      }

      const isDisqualified = Boolean(aiResult.is_disqualified);
      const masterScore = isDisqualified ? 0.0 : Number((totalWeight > 0 ? compositeScore / totalWeight : 50).toFixed(1));

      let priorityTier = "Tier C: Low Priority / Nurture";
      let urgencySla = "Automated Marketing Nurture";
      let recommendedChannel = "Marketing Newsletter & Documentation";

      if (isDisqualified) {
        priorityTier = "Disqualified: Anti-ICP";
        urgencySla = "No Outreach (Archived)";
        recommendedChannel = "Do Not Contact";
      } else if (masterScore >= 80 && (validatedEvidence.intent.score || 0) >= 75) {
        priorityTier = "Tier A1: Strategic Inbound";
        urgencySla = "< 2 Hours (Executive Callback)";
        recommendedChannel = "Direct Phone & Bespoke Executive Email";
      } else if (masterScore >= 65) {
        priorityTier = "Tier A2: High Priority Outbound";
        urgencySla = "< 24 Hours (Dedicated SDR Sequence)";
        recommendedChannel = "Multi-Touch Email & LinkedIn InMail";
      } else if (masterScore >= 50) {
        priorityTier = "Tier B1: Mid-Market Fast Track";
        urgencySla = "Within 48 Hours";
        recommendedChannel = "Inside Sales Discovery Call";
      }

      const branches = Array.isArray(account.branch_locations) ? account.branch_locations.map(String).filter(Boolean) : [];

      return jsonResponse({
        success: true,
        request_id: requestId,
        account: {
          company_name: cleanStr(account.company_name),
          domain: cleanStr(account.domain),
          contact_name: cleanStr(account.contact_name),
          job_title: cleanStr(account.job_title),
          industry: cleanStr(account.industry),
          sub_vertical: cleanStr(account.sub_vertical),
          location: cleanStr(account.location),
          branch_locations: branches,
          geographic_reach: cleanStr(account.geographic_reach) || (branches.length >= 2 ? "Global Multi-Region Enterprise" : (branches.length === 1 ? "Cross-Border Multi-Branch" : "Single-Market Hub")),
          scale: cleanStr(account.scale),
          tech_stack: cleanStr(account.tech_stack),
          intent_timeline: cleanStr(account.intent_timeline)
        },
        scores: {
          master_icp_score: masterScore,
          priority_tier: priorityTier,
          is_disqualified: isDisqualified,
          disqualification_reason: String(aiResult.disqualification_reason || "")
        },
        evidence: validatedEvidence,
        strategy: {
          urgency_sla: urgencySla,
          recommended_channel: recommendedChannel,
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
