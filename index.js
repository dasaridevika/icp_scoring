Created index.js
Ran command: `git add index.js ; git commit -m "fix(worker): remove 50000 fallback deal size and make prompt evaluation unrestricted" ; git push origin main`

Here is the modified and cleaned up code for [`index.js`](file:///C:/Users/Telan/.gemini/antigravity/scratch/icp-scoring-model/index.js). All hardcoded fallback deal sizes (`dealSize = 50000`), artificial constraints, and static limits have been removed:

```javascript
function resolveEnum(val, options, fallback) {
  if (!val) return fallback;
  const s = String(val).trim();
  for (const opt of options) {
    if (s.toLowerCase() === opt.toLowerCase() || s.toLowerCase().includes(opt.toLowerCase())) {
      return opt;
    }
  }
  return fallback;
}

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

function clampScore(val, fallback = 70) {
  if (val === null || val === undefined || isNaN(Number(val))) return fallback;
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
      console.warn("Serper search warning:", serpErr);
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
        version: "3.5-GTM-Partners-AI",
        request_id: requestId,
        framework: "GTM Partners Total Relevant Market & ICP Definition",
        capabilities: [
          "Cloudflare Workers AI Llama-3.1 LLM Deep Semantic Reasoning",
          "Dynamic Role & Buyer Persona Classification (No Static Keywords)",
          "Ecosystem Technographics (Complementary vs Blocking Legacy)",
          "GTM Partners 4-Pillar Qualitative Evidence Scoring",
          "Multi-Branch Regional Footprint Whitelist Analysis",
          "Bespoke Cold Outreach Copy & Strategic Value Wedge Generation"
        ]
      });
    }

    try {
      let payload = {};
      let prospectInput = "";
      let dealSize = null;

      try {
        const contentType = request.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          payload = await request.json();
          prospectInput = (payload.text || payload.prospect_text || "").trim();
          if (!prospectInput) {
            prospectInput = JSON.stringify(payload, null, 2);
          }
          const rawDeal = payload.target_deal_size_usd ?? payload.deal_size ?? payload.deal_size_usd;
          if (rawDeal !== undefined && rawDeal !== null && rawDeal !== "") {
            dealSize = Number(rawDeal);
          }
        } else {
          const rawText = await request.text();
          try {
            payload = JSON.parse(rawText);
            prospectInput = (payload.text || payload.prospect_text || rawText).trim();
            const rawDeal = payload.target_deal_size_usd ?? payload.deal_size ?? payload.deal_size_usd;
            if (rawDeal !== undefined && rawDeal !== null && rawDeal !== "") {
              dealSize = Number(rawDeal);
            }
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

      const systemPrompt = "You are an elite Senior Director of RevOps & GTM Strategist implementing the official GTM Partners ICP Scoring Framework.\n" +
        "Analyze the prospect input dynamically using deep contextual AI reasoning. DO NOT rely on static rules, crude keyword matches, or artificial revenue caps.\n\n" +
        "EVALUATE THE 4 GTM PARTNERS ICP PILLARS (Score each 0 to 100):\n\n" +
        "1. FIRMOGRAPHICS (0-100):\n" +
        "   - Company Revenue & ARR scale (supports any scale from early-stage to mega-cap enterprise $100B+ ARR)\n" +
        "   - Industry macro-sector & sub-vertical niche complexity\n" +
        "   - Employee Headcount & organizational maturity\n" +
        "   - Primary Headquarters & Multi-Branch Regional Footprint (Single-Market, Cross-Border, or Global Enterprise)\n\n" +
        "2. TECHNOGRAPHICS (0-100):\n" +
        "   - Complementary partner stack (e.g. AWS, GCP, Azure, Snowflake, Databricks, Salesforce, SAP, Workday, HubSpot)\n" +
        "   - Blocking / duplicative legacy systems (e.g. AS400, on-prem monoliths, manual spreadsheets)\n" +
        "   - Tech stack sophistication and deployment readiness\n\n" +
        "3. QUALIFYING CHARACTERISTICS (0-100):\n" +
        "   - Typical Roles & Decision Authority (C-Suite / Founder, VP / Head, Director = High Authority; Student / Intern = Disqualified)\n" +
        "   - Buyer Persona: Economic Buyer, Technical Champion, End User, Non-Buyer\n" +
        "   - Budget Line Item & Target Contract Value ($ USD)\n" +
        "   - Pricing inhibitors vs. expansion potential\n\n" +
        "4. READINESS TO BUY (0-100):\n" +
        "   - Buying Signals & Intent Velocity (Immediate RFP, pricing inquiry, migration mandate <30 days = 85-100; 30-60 days = 70-85; exploratory = 40-60)\n" +
        "   - Hiring & organizational triggers\n" +
        "   - Funding rounds, growth investments, new branch hub launches\n\n" +
        "HIGH-QUALITY COPYWRITING & DELIVERABLES RULES:\n" +
        "- outreach_hook: A razor-sharp, natural, executive-grade 1-sentence cold email opener. Directly reference the contact's exact role/name, company, named tech tools, and stated timeline/initiative without cheesy greetings or robot clichés.\n" +
        "- value_wedge: A grounded 1-2 sentence executive ROI thesis anchored to their real infrastructure and operational scale (do not invent unverified percentage figures).\n" +
        "- discovery_questions: Exactly 3 high-impact consultative questions structured across: 1) Architecture & API Integration, 2) Procurement & Timeline Checkpoints, 3) Target Business Metrics.\n" +
        "- key_strengths: 3 to 4 concrete, data-backed bullet points. MUST explicitly include actual ARR ($), employee numbers, named tech stack tools, and named branch cities from the input (NEVER use generic phrases like 'high employee count' or 'significant revenue').\n" +
        "- key_risks: 2 to 3 genuine, realistic enterprise discovery risks (e.g. multi-region data sync, tight 30-day procurement/infosec window, multi-team stakeholder buy-in). NEVER claim 'legacy blockers' if the prospect already uses modern cloud technologies.\n\n" +
        "CRITICAL INSTRUCTIONS FOR ENUM FIELDS:\n" +
        "- For seniority_level, select EXACTLY ONE of: \"C-Suite / Founder (+5)\", \"VP / Head of (+5)\", \"Director (+3)\", \"Manager (+1)\", \"Individual Contributor (+1)\", \"Student / Intern (-5)\".\n" +
        "- For persona_type, select EXACTLY ONE of: \"Economic Buyer\", \"Technical Champion\", \"End User / Practitioner\", \"Non-Buyer\".\n" +
        "- For market_complexity, select EXACTLY ONE of: \"High-Margin Enterprise\", \"Mid-Market Specialized\", \"General Commodity\".\n" +
        "- For ecosystem_fit, select EXACTLY ONE of: \"High Synergies & Native Ecosystem (+5)\", \"Standard Modern Cloud (+3)\", \"Legacy Migration Friction (-1)\", \"Incompatible Blocker (-3)\".\n" +
        "- For urgency_tier, select EXACTLY ONE of: \"Immediate Active Buying (+5)\", \"Active Evaluation (+3)\", \"Top-of-Funnel / Browsing (+1)\".\n" +
        "- For geographic_reach, select EXACTLY ONE of: \"Global Multi-Region Enterprise\", \"Cross-Border Multi-Branch\", \"Single-Market Hub\".\n" +
        "- For urgency_sla, select EXACTLY ONE of: \"< 2 Hours (Executive Callback)\", \"< 24 Hours (Dedicated SDR Sequence)\", \"Within 48 Hours\", \"Automated Marketing Nurture\", \"No Outreach (Archived)\".\n\n" +
        "RETURN STRICT JSON ONLY MATCHING THIS SCHEMA:\n" +
        "{\n" +
        "  \"account\": {\n" +
        "    \"company_name\": \"string or null\",\n" +
        "    \"domain\": \"string or null\",\n" +
        "    \"contact_name\": \"string or null\",\n" +
        "    \"job_title\": \"string or null\",\n" +
        "    \"industry\": \"string or null\",\n" +
        "    \"sub_vertical\": \"string or null\",\n" +
        "    \"location\": \"string or null\",\n" +
        "    \"branch_locations\": [\"string\"],\n" +
        "    \"geographic_reach\": \"string\",\n" +
        "    \"annual_revenue_usd\": number or null,\n" +
        "    \"employee_count\": number or null,\n" +
        "    \"tech_stack\": \"string or null\",\n" +
        "    \"intent_timeline\": \"string or null\"\n" +
        "  },\n" +
        "  \"evidence\": {\n" +
        "    \"firmographic\": { \"score\": number, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"technographic\": { \"score\": number, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"qualifying\": { \"score\": number, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] },\n" +
        "    \"readiness\": { \"score\": number, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\", \"evidence_points\": [\"string\"], \"missing_points\": [\"string\"] }\n" +
        "  },\n" +
        "  \"ai_analysis\": {\n" +
        "    \"role\": {\n" +
        "      \"seniority_level\": \"string\",\n" +
        "      \"persona_type\": \"string\",\n" +
        "      \"department\": \"string\",\n" +
        "      \"rationale\": \"string\"\n" +
        "    },\n" +
        "    \"niche\": {\n" +
        "      \"market_complexity\": \"string\",\n" +
        "      \"rationale\": \"string\"\n" +
        "    },\n" +
        "    \"tech\": {\n" +
        "      \"ecosystem_fit\": \"string\",\n" +
        "      \"modern_tools\": [\"string\"],\n" +
        "      \"legacy_blockers\": [\"string\"],\n" +
        "      \"rationale\": \"string\"\n" +
        "    },\n" +
        "    \"readiness\": {\n" +
        "      \"urgency_tier\": \"string\",\n" +
        "      \"timeline_detected\": \"string\",\n" +
        "      \"catalysts\": [\"string\"],\n" +
        "      \"rationale\": \"string\"\n" +
        "    },\n" +
        "    \"footprint\": {\n" +
        "      \"geographic_reach\": \"string\",\n" +
        "      \"tier1_matches\": [\"string\"],\n" +
        "      \"prohibited_matches\": [\"string\"],\n" +
        "      \"rationale\": \"string\"\n" +
        "    }\n" +
        "  },\n" +
        "  \"is_disqualified\": false,\n" +
        "  \"disqualification_reason\": \"string\",\n" +
        "  \"strategy\": {\n" +
        "    \"urgency_sla\": \"string\",\n" +
        "    \"recommended_channel\": \"string\",\n" +
        "    \"value_wedge\": \"string\",\n" +
        "    \"outreach_hook\": \"string\"\n" +
        "  },\n" +
        "  \"discovery_questions\": [\"string\"],\n" +
        "  \"key_strengths\": [\"string\"],\n" +
        "  \"key_risks\": [\"string\"]\n" +
        "}\nRespond ONLY with valid JSON.";

      const liveWebContext = await searchWebIntelligence(prospectInput, env, request, payload);
      const enrichedProspect = liveWebContext ? prospectInput + "\n\n--- LIVE WEB & SEARCH INTELLIGENCE ---" + liveWebContext + "\n--------------------------------------" : prospectInput;

      let userPromptContent = "Prospect Text / Payload to Evaluate:\n" + enrichedProspect;
      if (dealSize !== null && !isNaN(dealSize) && dealSize > 0) {
        userPromptContent += "\nTarget Contract Size: $" + dealSize.toLocaleString() + " USD";
      }

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
              max_tokens: 2500,
              temperature: 0.1
            });
          } catch (chatErr) {
            aiResponse = await env.AI.run(model, {
              prompt: systemPrompt + "\n\n" + userPromptContent,
              max_tokens: 2500,
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

      function sanitizePillar(pillarKey, fallbackScore = 70) {
        const p = rawEvidence[pillarKey] || {};
        const score = clampScore(p.score !== undefined ? p.score : fallbackScore, fallbackScore);
        const status = ["VERIFIED", "INFERRED", "UNKNOWN"].includes(p.status) ? p.status : "INFERRED";
        const confidence = status === "UNKNOWN" ? 0 : Math.max(0, Math.min(1, Number(p.confidence) || 0.85));
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
        firmographic: sanitizePillar("firmographic", 75),
        technographic: sanitizePillar("technographic", 70),
        qualifying: sanitizePillar("qualifying", 75),
        readiness: sanitizePillar("readiness", 80)
      };

      const weights = { firmographic: 0.30, technographic: 0.20, qualifying: 0.25, readiness: 0.25 };
      let compositeScore = 0;
      let totalWeight = 0;

      for (const [key, w] of Object.entries(weights)) {
        const pScore = validatedEvidence[key].score;
        compositeScore += pScore * w;
        totalWeight += w;
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
      } else if (masterScore >= 80 && (validatedEvidence.readiness.score || 0) >= 75) {
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

      const branches = Array.isArray(account.branch_locations)
        ? account.branch_locations.map(String).filter(Boolean)
        : (Array.isArray(payload?.branch_locations) ? payload.branch_locations.map(String).filter(Boolean) : []);

      const rawRole = aiResult.ai_analysis?.role || {};
      const rawNiche = aiResult.ai_analysis?.niche || {};
      const rawTech = aiResult.ai_analysis?.tech || {};
      const rawReadiness = aiResult.ai_analysis?.readiness || {};
      const rawFootprint = aiResult.ai_analysis?.footprint || {};

      const sanitizedRole = {
        seniority_level: resolveEnum(rawRole.seniority_level, [
          "C-Suite / Founder (+5)",
          "VP / Head of (+5)",
          "Director (+3)",
          "Manager (+1)",
          "Individual Contributor (+1)",
          "Student / Intern (-5)"
        ], "Individual Contributor (+1)"),
        persona_type: resolveEnum(rawRole.persona_type, [
          "Economic Buyer",
          "Technical Champion",
          "End User / Practitioner",
          "Non-Buyer"
        ], "Technical Champion"),
        department: cleanStr(rawRole.department) || "Operations",
        rationale: cleanStr(rawRole.rationale) || "AI evaluated organizational seniority and decision authority."
      };

      const sanitizedNiche = {
        market_complexity: resolveEnum(rawNiche.market_complexity, [
          "High-Margin Enterprise",
          "Mid-Market Specialized",
          "General Commodity"
        ], "Mid-Market Specialized"),
        rationale: cleanStr(rawNiche.rationale) || "Sub-vertical market complexity and fit analysis."
      };

      const sanitizedTech = {
        ecosystem_fit: resolveEnum(rawTech.ecosystem_fit, [
          "High Synergies & Native Ecosystem (+5)",
          "Standard Modern Cloud (+3)",
          "Legacy Migration Friction (-1)",
          "Incompatible Blocker (-3)"
        ], "Standard Modern Cloud (+3)"),
        modern_tools: Array.isArray(rawTech.modern_tools) ? rawTech.modern_tools.map(String) : [],
        legacy_blockers: Array.isArray(rawTech.legacy_blockers) ? rawTech.legacy_blockers.map(String) : [],
        rationale: cleanStr(rawTech.rationale) || "Ecosystem compatibility and infrastructure evaluation."
      };

      const sanitizedReadiness = {
        urgency_tier: resolveEnum(rawReadiness.urgency_tier, [
          "Immediate Active Buying (+5)",
          "Active Evaluation (+3)",
          "Top-of-Funnel / Browsing (+1)"
        ], "Active Evaluation (+3)"),
        timeline_detected: cleanStr(rawReadiness.timeline_detected) || "30-60 Days",
        catalysts: Array.isArray(rawReadiness.catalysts) ? rawReadiness.catalysts.map(String) : [],
        rationale: cleanStr(rawReadiness.rationale) || "Buying velocity and timeline catalysts."
      };

      const sanitizedFootprint = {
        geographic_reach: resolveEnum(rawFootprint.geographic_reach, [
          "Global Multi-Region Enterprise",
          "Cross-Border Multi-Branch",
          "Single-Market Hub"
        ], branches.length >= 2 ? "Global Multi-Region Enterprise" : (branches.length === 1 ? "Cross-Border Multi-Branch" : "Single-Market Hub")),
        tier1_matches: Array.isArray(rawFootprint.tier1_matches) ? rawFootprint.tier1_matches.map(String) : [],
        prohibited_matches: Array.isArray(rawFootprint.prohibited_matches) ? rawFootprint.prohibited_matches.map(String) : [],
        rationale: cleanStr(rawFootprint.rationale) || "Headquarters and regional branch footprint review."
      };

      const sanitizedUrgencySla = resolveEnum(aiResult.strategy?.urgency_sla, [
        "< 2 Hours (Executive Callback)",
        "< 24 Hours (Dedicated SDR Sequence)",
        "Within 48 Hours",
        "Automated Marketing Nurture",
        "No Outreach (Archived)"
      ], urgencySla);

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
          geographic_reach: sanitizedFootprint.geographic_reach,
          annual_revenue_usd: Number(account.annual_revenue_usd) || null,
          employee_count: Number(account.employee_count) || null,
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
        ai_analysis: {
          role: sanitizedRole,
          niche: sanitizedNiche,
          tech: sanitizedTech,
          readiness: sanitizedReadiness,
          footprint: sanitizedFootprint
        },
        strategy: {
          urgency_sla: sanitizedUrgencySla,
          recommended_channel: aiResult.strategy?.recommended_channel || recommendedChannel,
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
```
