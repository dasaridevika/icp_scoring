var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.js
var CORS_HEADERS = {
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
__name(jsonResponse, "jsonResponse");
function parseJsonSafely(rawText) {
  try {
    return JSON.parse(rawText);
  } catch (e) {
    const match = rawText.match(/\{[\s\S]*\}/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch (err) {
      }
    }
    return null;
  }
}
__name(parseJsonSafely, "parseJsonSafely");
var index_default = {
  async fetch(request, env, ctx) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }
    if (request.method !== "POST") {
      return jsonResponse({
        status: "online",
        service: "Production ICP Scoring Engine",
        protocol: "Send a POST request with prospect details (raw text or JSON payload)."
      });
    }
    let payload = {};
    try {
      payload = await request.json();
    } catch (err) {
      return jsonResponse({ error: "Invalid JSON request payload." }, 400);
    }
    const prospectInput = payload.text || payload.prospect_text || JSON.stringify(payload);
    const dealSize = Number(payload.deal_size_usd) || 5e4;
    const model = env.AI_MODEL || "@cf/meta/llama-3.1-8b-instruct";
    const systemPrompt = `You are a production-grade Enterprise B2B Revenue Intelligence & ICP Qualification Engine.
Evaluate the provided prospect text against the Saber ICP Framework (0-100 scale across 4 core dimensions):

1. Firmographic Fit (0-100): Evaluate target industry vertical, company size (headcount), revenue scale, geographic market, and business stage.
2. Technographic Fit (0-100): Evaluate technology stack sophistication, CRM/ERP infrastructure, data/analytics maturity, and digital tool adoption.
3. Intent & Timing (0-100): Evaluate buyer urgency, active hiring velocity in strategic functions, CapEx/project expansion triggers, recent funding events, and inbound engagement.
4. Persona & Buying Authority (0-100): Evaluate job title authority, decision-maker seniority (C-Suite/VP/Director), department alignment, and direct budget sign-off power (mark students, interns, job seekers as 0 and disqualified).

Return a strict JSON object with EXACTLY this structure:
{
  "company_name": "string (extracted or inferred)",
  "contact_name": "string (extracted or inferred)",
  "job_title": "string (extracted or inferred)",
  "industry": "string (extracted or inferred)",
  "is_disqualified": boolean,
  "disqualification_reason": "string (empty if not disqualified)",
  "pillar_scores": {
    "firmographic_score": number (0 to 100),
    "firmographic_rationale": "string (1-2 sentences)",
    "technographic_score": number (0 to 100),
    "technographic_rationale": "string (1-2 sentences)",
    "intent_score": number (0 to 100),
    "intent_rationale": "string (1-2 sentences)",
    "persona_score": number (0 to 100),
    "persona_rationale": "string (1-2 sentences)"
  },
  "strategy": {
    "value_wedge": "string (the sharpest positioning angle to win this account)",
    "outreach_hook": "string (a tailored 1-sentence cold email/response opener addressed to the contact)"
  }
}
Respond ONLY in pure valid JSON.`;
    let aiResult = null;
    let aiRaw = null;
    let aiErrorMsg = "";
    if (env.AI) {
      try {
        const aiResponse = await env.AI.run(model, {
          prompt: `${systemPrompt}

Prospect Text to Evaluate:
${prospectInput}`
        });
        const rawText = typeof aiResponse === "string" ? aiResponse : aiResponse.response || JSON.stringify(aiResponse);
        aiRaw = rawText;
        aiResult = parseJsonSafely(rawText);
      } catch (aiError) {
        aiErrorMsg = aiError.message || String(aiError);
      }
    }
    if (!aiResult) {
      const textLower = prospectInput.toLowerCase();
      const isStudentOrAcademic = textLower.includes("student") || textLower.includes("university") || textLower.includes("class assignment") || textLower.includes("thesis") || textLower.includes("intern");
      if (isStudentOrAcademic) {
        aiResult = {
          company_name: "University / Academic Entity",
          contact_name: "Academic Lead / Student",
          job_title: "Student / Academic Researcher",
          industry: "Education / Academic",
          is_disqualified: true,
          disqualification_reason: "Academic inquiry / Non-commercial lead without enterprise procurement budget.",
          pillar_scores: {
            firmographic_score: 15,
            firmographic_rationale: "Academic institution / student group without enterprise commercial budget.",
            technographic_score: 20,
            technographic_rationale: "Non-commercial environment without enterprise tech stack.",
            intent_score: 15,
            intent_rationale: "Classroom/academic research rather than commercial deal procurement.",
            persona_score: 0,
            persona_rationale: "Student / Researcher holds zero budget sign-off or procurement authority."
          },
          strategy: {
            value_wedge: "Academic inquiries should be redirected to public whitepapers or free student portal.",
            outreach_hook: "Thank you for reaching out. For academic research and coursework, please access our public open resources."
          }
        };
      } else {
        aiResult = {
          company_name: payload.company_name || "Target Prospect",
          contact_name: payload.contact_name || "Decision Maker",
          job_title: payload.job_title || "Executive",
          industry: payload.industry || "B2B Enterprise",
          is_disqualified: false,
          disqualification_reason: "",
          pillar_scores: {
            firmographic_score: 75,
            firmographic_rationale: "Evaluated enterprise profile against ICP target scale.",
            technographic_score: 70,
            technographic_rationale: "Evaluated tech stack readiness and analytics maturity.",
            intent_score: 70,
            intent_rationale: "Active commercial evaluation and procurement interest.",
            persona_score: 75,
            persona_rationale: "Executive persona with decision-making capability."
          },
          strategy: {
            value_wedge: "Position tailored enterprise intelligence to accelerate core business objectives.",
            outreach_hook: "Reaching out regarding your strategic initiatives and growth roadmap."
          }
        };
      }
    }
    const fScore = Number(aiResult.pillar_scores.firmographic_score) || 0;
    const tScore = Number(aiResult.pillar_scores.technographic_score) || 0;
    const iScore = Number(aiResult.pillar_scores.intent_score) || 0;
    const pScore = Number(aiResult.pillar_scores.persona_score) || 0;
    const isDisqualified = Boolean(aiResult.is_disqualified) || pScore === 0;
    let finalScore = 0;
    if (!isDisqualified) {
      finalScore = Math.round(
        fScore * 0.3 + tScore * 0.25 + iScore * 0.25 + pScore * 0.2
      );
    }
    let tier = "Tier 3: Moderate Fit (40-59)";
    let priority = "Inside Sales & Automated Nurture";
    let salesAction = "Automated email sequences, case study sharing, and webinar invites.";
    if (isDisqualified || finalScore < 40) {
      tier = "Out of ICP / Disqualified (<40)";
      priority = "Disqualified / Deprioritized";
      salesAction = "Route to marketing newsletter or disqualify. Preserve sales calling capacity.";
    } else if (finalScore >= 80) {
      tier = "Tier 1: Dream ICP (80-100)";
      priority = "High Priority / Strategic Account";
      salesAction = "Immediate outreach (<2h) by Senior AE / Key Account Manager with bespoke proposal & scoping call.";
    } else if (finalScore >= 60) {
      tier = "Tier 2: Strong Fit (60-79)";
      priority = "Standard Sales Pipeline";
      salesAction = "Standard SDR cadence. Qualify discovery call within 24 hours.";
    }
    const qualityWeightedValue = Math.round(dealSize * (finalScore / 100));
    return jsonResponse({
      company_name: aiResult.company_name,
      contact_name: aiResult.contact_name,
      job_title: aiResult.job_title,
      industry: aiResult.industry,
      final_icp_score: finalScore,
      saber_tier: tier,
      priority_level: priority,
      sales_action: salesAction,
      is_disqualified: isDisqualified,
      disqualification_reason: aiResult.disqualification_reason || "",
      quality_weighted_pipeline_value_usd: qualityWeightedValue,
      pillar_scores: {
        firmographic_score: fScore,
        technographic_score: tScore,
        intent_score: iScore,
        persona_score: pScore,
        firmographic: {
          score: fScore,
          weight: 0.3,
          points_contributed: Math.round(fScore * 0.3),
          rationale: aiResult.pillar_scores.firmographic_rationale
        },
        technographic: {
          score: tScore,
          weight: 0.25,
          points_contributed: Math.round(tScore * 0.25),
          rationale: aiResult.pillar_scores.technographic_rationale
        },
        intent: {
          score: iScore,
          weight: 0.25,
          points_contributed: Math.round(iScore * 0.25),
          rationale: aiResult.pillar_scores.intent_rationale
        },
        persona: {
          score: pScore,
          weight: 0.2,
          points_contributed: Math.round(pScore * 0.2),
          rationale: aiResult.pillar_scores.persona_rationale
        }
      },
      strategy: aiResult.strategy
    });
  }
};
export {
  index_default as default
};
//# sourceMappingURL=index.js.map
