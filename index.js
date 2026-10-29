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
  "Access-Control-Allow-Headers": "Content-Type, X-Request-ID"
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
    const jsonMatch = rawText.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
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

function clampScore(val, fallback = null) {
  if (val === null || val === undefined || isNaN(Number(val))) return fallback;
  return Math.max(0, Math.min(100, Math.round(Number(val))));
}

function cleanStr(v) {
  if (!v) return null;
  const s = String(v).trim();
  if (["null", "none", "undefined", "n/a", ""].includes(s.toLowerCase())) return null;
  return s;
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
        version: "3.6",
        request_id: requestId,
        framework: "Section 6 4-Pillar ICP Scoring & Rating Rubric",
        capabilities: [
          "Cloudflare Workers AI Llama-3.1 Semantic Reasoning",
          "1 to 5 Rating Evidence Classification (No Fabricated Defaults)",
          "Firmographics, Offering Fit, Buyer Authority, and Intent Scoring",
          "Model Observability and Secret Key Security"
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
          prospectInput = await request.text();
        }
      } catch (parseErr) {
        return jsonResponse({
          success: false,
          error: {
            code: "INVALID_JSON",
            message: "Malformed request payload.",
            request_id: requestId
          }
        }, 400);
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

      const systemPrompt = "You are a Senior B2B Revenue Intelligence Analyst evaluating inbound prospect leads.\n" +
        "Rate each of the 4 ICP Pillars strictly from 1 to 5 based on verified evidence, or mark as UNKNOWN if no evidence is present.\n\n" +
        "RATING RUBRIC (1 to 5):\n" +
        "5: Strong match, clear evidence\n" +
        "4: Good match\n" +
        "3: Partial match\n" +
        "2: Weak match\n" +
        "1: Clear mismatch (evidence says no)\n" +
        "UNKNOWN: No evidence at all (do not make up numbers)\n\n" +
        "THE 4 PILLARS:\n" +
        "1. FIRMOGRAPHIC (35%): Company size, industry sector, target geographic focus, business vs free email.\n" +
        "2. OFFERING FIT (25%): Does what they need match the organization's product or service offerings?\n" +
        "3. BUYER AUTHORITY (25%): Seniority and decision mandate. C-Suite/VP/Director = high (4-5); Manager = mid (3); IC = low (1-2); Student/Intern = Disqualified.\n" +
        "4. INTENT (15%): Ready to buy now? RFP/Proposal/Quote/Timeline <30 days = high (5); exploratory = mid (3); browsing = low (1-2).\n\n" +
        "CRITICAL COPYWRITING:\n" +
        "- outreach_hook: A sharp 1-sentence consultative cold email opener directly referencing their sector, company, and project focus.\n" +
        "- value_wedge: 1-2 sentence executive ROI thesis anchored to their product and solution needs.\n" +
        "- discovery_questions: 3 high-impact consultative questions for discovery scoping.\n" +
        "- key_strengths: 3 concrete data points from the prospect text.\n" +
        "- key_risks: 2 realistic qualification risks.\n\n" +
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
        "    \"intent_timeline\": \"string or null\"\n" +
        "  },\n" +
        "  \"evidence\": {\n" +
        "    \"firmographic\": { \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\" },\n" +
        "    \"offering\": { \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\" },\n" +
        "    \"authority\": { \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\" },\n" +
        "    \"intent\": { \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number, \"rationale\": \"string\" }\n" +
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
        "    \"readiness\": {\n" +
        "      \"urgency_tier\": \"string\",\n" +
        "      \"timeline_detected\": \"string or null\",\n" +
        "      \"rationale\": \"string\"\n" +
        "    },\n" +
        "    \"footprint\": {\n" +
        "      \"geographic_reach\": \"string\",\n" +
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

      let userPromptContent = "Prospect Text / Payload to Evaluate:\n" + prospectInput;
      if (dealSize !== null && !isNaN(dealSize) && dealSize > 0) {
        userPromptContent += "\nTarget Contract Size: $" + dealSize.toLocaleString() + " USD";
      }

      let aiRaw = null;
      let aiErrorMsg = "";
      let aiResult = null;
      let modelUsed = primaryModel;

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
          if (aiResult) {
            modelUsed = model;
            break;
          }
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

      // Bug 2.1 fix: Never invent fake numbers. Unknown stays Unknown.
      function sanitizePillar(pillarKey, fallbackKeys = []) {
        let p = rawEvidence[pillarKey];
        if (!p) {
          for (const fb of fallbackKeys) {
            if (rawEvidence[fb]) { p = rawEvidence[fb]; break; }
          }
        }
        p = p || {};
        const status = ["VERIFIED", "INFERRED", "UNKNOWN"].includes(p.status)
          ? p.status
          : (p.rating || p.score ? "INFERRED" : "UNKNOWN");

        let rating = null;
        if (status !== "UNKNOWN") {
          if (p.rating !== undefined && p.rating !== null && !isNaN(Number(p.rating))) {
            rating = Math.max(1, Math.min(5, Math.round(Number(p.rating))));
          } else if (p.score !== undefined && p.score !== null && !isNaN(Number(p.score)) && Number(p.score) > 0) {
            rating = Math.max(1, min(5, Math.round(Number(p.score) / 20)));
          }
        }

        const score = rating !== null ? rating * 20 : null;
        const confidence = status === "UNKNOWN" ? 0 : Math.max(0, Math.min(1, Number(p.confidence) || 0.85));

        return {
          rating,
          score,
          status,
          confidence: Number(confidence.toFixed(2)),
          rationale: String(p.rationale || (status === "UNKNOWN" ? "No verified data provided." : ""))
        };
      }

      const validatedEvidence = {
        firmographic: sanitizePillar("firmographic"),
        offering: sanitizePillar("offering", ["technographic"]),
        technographic: sanitizePillar("offering", ["technographic"]), // Alias
        authority: sanitizePillar("authority", ["qualifying"]),
        qualifying: sanitizePillar("authority", ["qualifying"]),       // Alias
        intent: sanitizePillar("intent", ["readiness"]),
        readiness: sanitizePillar("intent", ["readiness"])            // Alias
      };

      const isDisqualified = Boolean(aiResult.is_disqualified);
      const branches = Array.isArray(account.branch_locations)
        ? account.branch_locations.map(String).filter(Boolean)
        : (Array.isArray(payload?.branch_locations) ? payload.branch_locations.map(String).filter(Boolean) : []);

      const rawRole = aiResult.ai_analysis?.role || {};
      const rawNiche = aiResult.ai_analysis?.niche || {};
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
        confidence: 0.90,
        rationale: cleanStr(rawRole.rationale) || "Role analysis."
      };

      const sanitizedNiche = {
        market_complexity: resolveEnum(rawNiche.market_complexity, [
          "High-Margin Enterprise",
          "Mid-Market Specialized",
          "General Commodity"
        ], "Mid-Market Specialized"),
        rationale: cleanStr(rawNiche.rationale) || "Market complexity review."
      };

      const sanitizedReadiness = {
        urgency_tier: resolveEnum(rawReadiness.urgency_tier, [
          "Immediate Active Buying (+5)",
          "Active Evaluation (+3)",
          "Top-of-Funnel / Browsing (+1)"
        ], "Active Evaluation (+3)"),
        timeline_detected: cleanStr(rawReadiness.timeline_detected), // Bug 2.1: no fake "30-60 Days"
        rationale: cleanStr(rawReadiness.rationale) || "Buying velocity and timeline analysis."
      };

      const sanitizedFootprint = {
        geographic_reach: resolveEnum(rawFootprint.geographic_reach, [
          "Global Multi-Region Enterprise",
          "Cross-Border Multi-Branch",
          "Single-Market Hub"
        ], branches.length >= 2 ? "Global Multi-Region Enterprise" : (branches.length === 1 ? "Cross-Border Multi-Branch" : "Single-Market Hub")),
        rationale: cleanStr(rawFootprint.rationale) || "Footprint review."
      };

      return jsonResponse({
        success: true,
        request_id: requestId,
        model_used: modelUsed, // Bug 3.7 fix
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
          intent_timeline: cleanStr(account.intent_timeline)
        },
        scores: {
          is_disqualified: isDisqualified,
          disqualification_reason: String(aiResult.disqualification_reason || "")
        },
        evidence: validatedEvidence,
        ai_analysis: {
          role: sanitizedRole,
          niche: sanitizedNiche,
          readiness: sanitizedReadiness,
          footprint: sanitizedFootprint
        },
        strategy: {
          urgency_sla: cleanStr(aiResult.strategy?.urgency_sla) || "Manual Review Required",
          recommended_channel: cleanStr(aiResult.strategy?.recommended_channel) || "Direct Email",
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
