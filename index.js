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
  let rawText = String(raw).trim();
  try {
    return JSON.parse(rawText);
  } catch (e) {
    let errDetail = e.message;
    const jsonMatch = rawText.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[1]);
      } catch (err) {
        errDetail = err.message;
        rawText = jsonMatch[1].trim();
      }
    }
    const match = rawText.match(/\{[\s\S]*\}/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch (err) {
        errDetail = err.message;
        rawText = match[0].trim();
      }
    }

    // Repair 0: Unquoted UNKNOWN / undefined / NaN to null
    let candidate = rawText.replace(/:\s*(?:UNKNOWN|undefined|NaN)\b/gi, ': null');
    try {
      return JSON.parse(candidate);
    } catch (err) {}

    // Repair 1: Trailing array closed with '}' instead of ']' at the end
    candidate = candidate.replace(/("[^"\\]*(?:\\.[^"\\]*)*")\s*\}\s*\}\s*$/, '$1\n  ]\n}');
    try {
      return JSON.parse(candidate);
    } catch (err) {}

    // Repair 2: Trailing commas before } or ]
    candidate = candidate.replace(/,\s*([\}\]])/g, '$1');
    try {
      return JSON.parse(candidate);
    } catch (err) {}

    // Repair 3: Both unquoted UNKNOWN, trailing commas, and unclosed array
    candidate = rawText.replace(/:\s*(?:UNKNOWN|undefined|NaN)\b/gi, ': null')
                       .replace(/,\s*([\}\]])/g, '$1')
                       .replace(/("[^"\\]*(?:\\.[^"\\]*)*")\s*\}\s*\}\s*$/, '$1\n  ]\n}');
    try {
      return JSON.parse(candidate);
    } catch (err) {}

    console.warn("[parseJsonSafely Error]: " + errDetail + " | Sample: " + rawText.substring(0, 300));
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
  if (["null", "none", "undefined", "n/a", "unknown", ""].includes(s.toLowerCase())) return null;
  return s;
}

function pickCleanList(primary, secondary) {
  const src = (Array.isArray(primary) && primary.length > 0)
    ? primary
    : ((Array.isArray(secondary) && secondary.length > 0) ? secondary : []);
  return src.map(cleanStr).filter(Boolean);
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

      const primaryModel = env?.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct-fast";
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

      const cs = payload.company_standards || {};
      const orgName = cleanStr(cs.org_name) || "Blackridge Research & Consulting";
      const coreOfferings = Array.isArray(cs.core_offerings)
        ? cs.core_offerings.map(cleanStr).filter(Boolean)
        : [];
      const focusIndustries = Array.isArray(cs.target_focus_industries)
        ? cs.target_focus_industries.map(cleanStr).filter(Boolean)
        : [];
      const tier1Territories = Array.isArray(cs.tier1_territories)
        ? cs.tier1_territories.map(cleanStr).filter(Boolean)
        : [];
      const prohibitedCountries = Array.isArray(cs.prohibited_countries)
        ? cs.prohibited_countries.map(cleanStr).filter(Boolean)
        : [];

      const offeringsBlock = coreOfferings.length > 0
        ? coreOfferings.map((item, idx) => `${idx + 1}. ${item}`).join("\n")
        : "Not explicitly enumerated in request config; evaluate alignment from the prospect's stated product, research, database, or consulting need.";

      const focusBlock = focusIndustries.length > 0
        ? focusIndustries.join(", ")
        : "Not explicitly enumerated in request config; evaluate commercial B2B fit from the prospect's stated industry and project context.";

      const systemPrompt =
        `You are a Senior B2B Revenue Intelligence Analyst evaluating inbound prospect leads for ${orgName}.\n` +
        "Rate each of the 4 ICP Pillars strictly from 1 to 5 based on verified evidence, or mark as UNKNOWN if no evidence is present.\n\n" +
        `ORGANIZATION SETTINGS & CATALOG (${orgName}):\n` +
        `Core Offerings (from config):\n${offeringsBlock}\n\n` +
        `Target Focus Industries (from config):\n${focusBlock}\n` +
        (tier1Territories.length > 0 ? `Tier 1 Supported Territories: ${tier1Territories.join(", ")}\n` : "") +
        (prohibitedCountries.length > 0 ? `Prohibited / Sanctioned Countries: ${prohibitedCountries.join(", ")}\n` : "") +
        "\nIMPORTANT COVERAGE RULE: Treat every industry in Target Focus Industries as an equal first-class focus sector, and treat every database, report, or service in Core Offerings as an equal direct-match offering.\n" +
        "MISSING OPTIONAL FIELDS RULE: Annual revenue, employee count/headcount, timeline, buying role, and deal size are optional and omitted by default. NEVER penalize or reduce Firmographic, Offering Fit, Buyer Authority, or Intent ratings because revenue, headcount, timeline, buying role, or deal size is absent.\n\n" +
        "RATING RUBRIC (1 to 5):\n" +
        "5: Strong match, clear evidence\n" +
        "4: Good match\n" +
        "3: Partial match\n" +
        "2: Weak match\n" +
        "1: Clear mismatch (evidence says no)\n" +
        "UNKNOWN: No evidence at all (when unverified, output null for rating, and \"UNKNOWN\" for status; never output literal unquoted UNKNOWN).\n\n" +
        "THE 4 PILLARS:\n" +
        "1. FIRMOGRAPHIC (35%): " +
        "5 = company operates in OR builds/develops capital projects or facilities covered by any configured Target Focus Industry AND country/location matches a Tier 1 Supported Territory (including standard abbreviations like US/USA for United States, UK for United Kingdom, UAE for United Arab Emirates) AND uses a business email; " +
        "4 = company operates in OR builds/develops capital projects covered by a configured Target Focus Industry AND uses a business email, but location is outside Tier 1 supported territories (while not prohibited) or location is unconfirmed; " +
        "3 = company is in a closely adjacent commercial/B2B industrial, infrastructure, engineering, EPC, or real-asset sector related to the configured Target Focus Industries with a business email; " +
        "2 = company matches or is adjacent to a configured Target Focus Industry but uses a free email provider (e.g. gmail, yahoo); " +
        "1 = organization/sector has no match or relevance to any configured Target Focus Industry (nor any project/facility type covered by them) -> MUST rate 1 regardless of size, revenue, title, or location; OR prohibited country; " +
        "UNKNOWN = sector and location and company details are all completely missing.\n" +
        "2. OFFERING FIT (25%): Does what the lead needs match any item in the configured Core Offerings list above? " +
        "5 = Direct match for one or more configured Core Offerings (Stated Offering Interest — even as a comma-separated list with no message — or the message directly names or maps to any listed project database, report, research, or consulting offering); " +
        "4 = High alignment with the scope of one or more configured Core Offerings without naming the exact offering; " +
        "3 = Partial or adjacent data/research request weakly related to configured Core Offerings; " +
        "2 = Weak alignment with configured Core Offerings; " +
        "1 = Clear mismatch (needs something unrelated to configured Core Offerings, or non-commercial/job applicant request). " +
        "UNKNOWN = Neither Stated Offering Interest nor a product/solution need message is provided (if both are missing, output null for rating and \"UNKNOWN\" for status; never mark Offering Fit as UNKNOWN when Stated Offering Interest is present, and do not infer offering fit from company industry alone).\n" +
        "3. BUYER AUTHORITY (25%): Seniority and decision mandate within the organization. " +
        "5 = C-Suite / Founder / VP / Head of (Top Decision Maker); " +
        "4 = Director (Senior Decision Maker); " +
        "3 = Manager / Lead (Mid-level); " +
        "2 = Junior or Individual Contributor business role (Coordinator, Specialist, Analyst, Associate, Executive Assistant, Staff, or Commercial role with low decision authority — including at poor-fit or non-target companies); " +
        "1 = Student, intern, academic/thesis requester, job applicant, or personal/hobbyist with no business purchasing role.\n" +
        "4. INTENT (15%): " +
        "5 = mentions an RFP, formal quote request, vendor selection, approved budget, or purchase/decision date within 30 days; " +
        "4 = mentions an evaluation or project timeline of 1 to 3 months (or specific quarter stated) or explicit commercial pilot/trial request; " +
        "3 = mentions a stated project need, tender search, or data requirement with NO purchasing timeline specified (e.g. 'We need data on upcoming tenders', 'need research reports on solar pipeline'); " +
        "2 = early exploratory or curious: downloaded a sample, general pricing curiosity, or browsing without project scope (e.g. 'Downloaded a sample, curious about pricing', general cost inquiry); " +
        "1 = non-commercial research, academic, student/thesis, personal/hobby project, or job applicant; " +
        "UNKNOWN = no inquiry, buying intent, notes, or message provided at all (output null for rating, and 'UNKNOWN' for status).\n\n" +
        "DISQUALIFICATION RULE (is_disqualified & disqualification_reason):\n" +
        "- Allow is_disqualified = true ONLY if the lead's title, email, or message/notes falls into one of these 3 cases:\n" +
        "  1. Student, thesis, or academic/university research request;\n" +
        "  2. Job applicant, resume/CV submission, or career/internship inquiry;\n" +
        "  3. Personal or hobby project.\n" +
        "- Check BOTH the title AND the message/notes: even if the lead has a normal business title (e.g. Researcher, Engineer, Manager), set is_disqualified = true when their message requests data for a thesis or academic paper, applies for a job/internship, or describes a personal/hobby project.\n" +
        "- NEVER set is_disqualified = true for normal business contacts, junior employees (e.g. Coordinator, Associate, Analyst, Assistant), poor-fit companies/sectors, or merely because contact role/title or message is blank/missing. Leave is_disqualified = false and rate their pillars low (1 or 2) instead.\n" +
        "- When is_disqualified = true, disqualification_reason MUST quote the exact words from the lead's own title or message showing why it matched one of the 3 cases above. Do NOT copy category lists or wording from this prompt. When is_disqualified = false, set disqualification_reason to \"\".\n\n" +
        "CRITICAL COPYWRITING:\n" +
        "- outreach_hook: A sharp 1-sentence consultative cold email opener directly referencing their sector, company, and project focus. Never echo raw prospect notes or output 'UNKNOWN'.\n" +
        "- value_wedge: 1-2 sentence executive ROI thesis anchored to their stated needs and matching configured Core Offerings. Never output 'UNKNOWN'.\n" +
        "- discovery_questions: Up to 3 scoping questions grounded ONLY in facts explicitly stated in the lead data (never invent unstated facts). Output an empty list [] if disqualified or if there is nothing real to ask.\n" +
        "- key_strengths: Up to 3 positive ICP fit points grounded ONLY in facts explicitly stated in the lead data (never invent years of experience, online presence, headcount, or unstated details). Output an empty list [] if there are no real strengths.\n" +
        "- key_risks: Up to 2 qualification risks grounded ONLY in facts explicitly stated in the lead data or gaps observed in the input (never invent facts). Output an empty list [] if there are no real risks.\n\n" +
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
        "    \"firmographic\": { \"rationale\": \"string\", \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number },\n" +
        "    \"offering\": { \"rationale\": \"string\", \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number },\n" +
        "    \"authority\": { \"rationale\": \"string\", \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number },\n" +
        "    \"intent\": { \"rationale\": \"string\", \"rating\": number or null, \"score\": number or null, \"status\": \"VERIFIED|INFERRED|UNKNOWN\", \"confidence\": number }\n" +
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
        "  \"disqualification_reason\": \"empty string unless is_disqualified is true; quote exact words from the lead's title or message\",\n" +
        "  \"strategy\": {\n" +
        "    \"urgency_sla\": \"string\",\n" +
        "    \"recommended_channel\": \"string\",\n" +
        "    \"value_wedge\": \"string\",\n" +
        "    \"outreach_hook\": \"string\"\n" +
        "  },\n" +
        "  \"discovery_questions\": [\"string (or [] if none)\"],\n" +
        "  \"key_strengths\": [\"string (or [] if none)\"],\n" +
        "  \"key_risks\": [\"string (or [] if none)\"]\n" +
        "}\nRespond ONLY with valid JSON. Ensure every array [ ] and object { } is strictly and correctly closed.";

      let userPromptContent = "PROSPECT DATA TO EVALUATE:\n" + prospectInput;
      if (dealSize !== null && !isNaN(dealSize) && dealSize > 0) {
        userPromptContent += "\nTarget Contract Size: $" + dealSize.toLocaleString() + " USD";
      }
      if (payload.offering_interest) {
        userPromptContent += "\nStated Offering Interest: " + payload.offering_interest;
      }
      if (payload.sub_vertical && payload.sub_vertical !== payload.industry_sector) {
        userPromptContent += "\nSub-Vertical / Specialty: " + payload.sub_vertical;
      }
      if (Array.isArray(payload.branch_locations) && payload.branch_locations.length > 0) {
        userPromptContent += "\nBranch Locations: " + payload.branch_locations.join(", ");
      }
      if (payload.existing_platform) {
        userPromptContent += "\nIncumbent / Existing Platform: " + payload.existing_platform;
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
              temperature: 0
            });
          } catch (chatErr) {
            aiResponse = await env.AI.run(model, {
              prompt: systemPrompt + "\n\n" + userPromptContent,
              max_tokens: 2500,
              temperature: 0
            });
          }

          if (typeof aiResponse === "string") {
            aiRaw = aiResponse;
          } else if (aiResponse && typeof aiResponse.response === "string") {
            aiRaw = aiResponse.response;
          } else if (aiResponse && typeof aiResponse.response === "object" && aiResponse.response !== null) {
            aiResult = aiResponse.response;
            aiRaw = JSON.stringify(aiResponse.response);
          } else if (aiResponse && Array.isArray(aiResponse.choices) && aiResponse.choices[0]?.message?.content) {
            aiRaw = aiResponse.choices[0].message.content;
          } else {
            aiRaw = JSON.stringify(aiResponse || "");
          }

          if (!aiResult) {
            aiResult = parseJsonSafely(aiRaw);
          }

          if (aiResult) {
            if (aiResult.response && typeof aiResult.response === "object") {
              aiResult = aiResult.response;
            } else if (Array.isArray(aiResult.choices) && aiResult.choices[0]?.message?.content) {
              const inner = parseJsonSafely(aiResult.choices[0].message.content);
              if (inner) aiResult = inner;
            }
          }

          if (aiResult && (aiResult.evidence || aiResult.account || aiResult.ai_analysis || aiResult.strategy)) {
            modelUsed = model;
            break;
          } else {
            const rawLen = aiRaw ? aiRaw.length : 0;
            const tail = aiRaw && rawLen > 200 ? aiRaw.substring(rawLen - 200) : "";
            console.warn(`[Workers AI Parse Warning][${model}][${requestId}]: Model output could not be parsed as valid JSON (len: ${rawLen}). Head: ${aiRaw ? aiRaw.substring(0, 200) : ""}. Tail: ${tail}`);
            aiResult = null;
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
            rating = Math.max(1, Math.min(5, Math.round(Number(p.score) / 20)));
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
      const disqReason = isDisqualified ? (cleanStr(aiResult.disqualification_reason) || "") : "";
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
        ], "Unspecified"),
        persona_type: resolveEnum(rawRole.persona_type, [
          "Economic Buyer",
          "Technical Champion",
          "End User / Practitioner",
          "Non-Buyer"
        ], "Unspecified"),
        department: cleanStr(rawRole.department) || "Unspecified",
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
        ], "Unspecified"),
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
          disqualification_reason: disqReason
        },
        is_disqualified: isDisqualified,
        disqualification_reason: disqReason,
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
          value_wedge: cleanStr(aiResult.strategy?.value_wedge || aiResult.value_wedge) || "",
          outreach_hook: cleanStr(aiResult.strategy?.outreach_hook || aiResult.outreach_hook) || "",
          discovery_questions: pickCleanList(aiResult.discovery_questions, aiResult.strategy?.discovery_questions),
          key_strengths: pickCleanList(aiResult.key_strengths, aiResult.strategy?.key_strengths),
          key_risks: pickCleanList(aiResult.key_risks, aiResult.strategy?.key_risks)
        },
        discovery_questions: pickCleanList(aiResult.discovery_questions, aiResult.strategy?.discovery_questions),
        key_strengths: pickCleanList(aiResult.key_strengths, aiResult.strategy?.key_strengths),
        key_risks: pickCleanList(aiResult.key_risks, aiResult.strategy?.key_risks)
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
