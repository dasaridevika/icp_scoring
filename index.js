/**
 * Enterprise ICP Revenue Intelligence - Cloudflare Worker API
 * 
 * Features:
 * 1. AI Semantic Text Analysis:
 *    - Role Title -> Seniority (+5/+3/+1/-5), Buyer Persona (Economic Buyer/Technical Champion/End User), Department.
 *    - Sub-Vertical Niche -> Market Complexity & High-Margin Enterprise Fit.
 *    - Buying Intent Notes -> Urgency Tier (+5/+3/+1), Timeline Signals (<30 Days, 30-60 Days).
 *    - Tech Stack -> Modern Partner Ecosystem Synergies vs Legacy Blockers.
 * 2. Deterministic Settings-Driven Scoring:
 *    - Revenue ($), Headcount, Deal Size ($), and Territories evaluated against configurable standards.
 * 3. 4-Pillar GTM Forced-Choice Scoring & Priority Tier SLA Routing.
 */

const MASTER_INDUSTRY_SECTORS = [
  "Manufacturing & Industrial Goods",
  "Energy, Utilities & Renewables",
  "Technology, SaaS & IT",
  "Financial Services & FinTech",
  "Healthcare & Life Sciences",
  "Logistics, Freight & Supply Chain",
  "Retail, Wholesale & E-Commerce",
  "Construction & Real Estate",
  "Professional & Business Services",
  "Telecommunications & Media",
  "Education & Public Sector"
];

const DISPOSABLE_DOMAINS = new Set([
  "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com",
  "outlook.com", "live.com", "msn.com", "icloud.com", "protonmail.com",
  "proton.me", "pm.me", "mail.ru", "163.com", "tempmail.com", "mailinator.com"
]);

// Modern Tech recognition
const MODERN_ECOSYSTEM_KEYWORDS = {
  "SAP": "Enterprise ERP & Supply Chain",
  "AWS": "Cloud Infrastructure",
  "Azure": "Enterprise Microsoft Cloud",
  "Google Cloud": "GCP Cloud Infrastructure",
  "Snowflake": "Data Cloud & Warehousing",
  "Databricks": "Data Lakehouse & ML",
  "Salesforce": "Enterprise CRM",
  "HubSpot": "Inbound CRM & Marketing",
  "Workday": "Enterprise HR & Finance",
  "Oracle Cloud": "Enterprise Cloud ERP",
  "PostgreSQL": "Relational Data Platform",
  "Kubernetes": "Container Orchestration",
  "Stripe": "Billing & Payments Engine",
  "PowerBI": "Enterprise BI & Analytics",
  "Tableau": "Data Visualization"
};

const LEGACY_BLOCKER_KEYWORDS = {
  "AS400": "Legacy IBM Mainframe Architecture",
  "On-Premises Monolith": "Air-gapped Legacy Infrastructure",
  "Custom In-House Legacy": "Proprietary Unmaintained Stack",
  "Excel Manual": "Manual Spreadsheet Workflows",
  "Legacy Mainframe": "High-friction Mainframe Core"
};

// --- Semantic AI Text Classifiers ---

function analyzeRole(title) {
  const raw = (title || "").trim();
  if (!raw) {
    return {
      raw_title: "Unspecified Role",
      seniority_level: "Individual Contributor (+1)",
      seniority_points: 1,
      persona_type: "End User / Practitioner",
      department: "General Business",
      rationale: "No role provided; defaulting to baseline practitioner.",
      is_disqualifier: false
    };
  }

  const t = raw.toLowerCase();

  // Non-buyer check
  if (/\b(intern|internship|student|trainee|apprentice|volunteer|fellow|academic)\b/.test(t)) {
    return {
      raw_title: raw,
      seniority_level: "Student / Intern (-5)",
      seniority_points: -5,
      persona_type: "Non-Buyer",
      department: "Academic / Entry-level",
      rationale: `Identified non-buyer / student title in '${raw}'.`,
      is_disqualifier: true
    };
  }

  // Department extraction
  let dept = "Operations & General Management";
  if (/procurement|sourcing|purchasing|supply\s+chain|vendor|logistics|commercial/.test(t)) dept = "Procurement & Supply Chain";
  else if (/\bit\b|information\s+tech|cloud|devops|infrastructure|security|ciso|sysadmin/.test(t)) dept = "IT, Cloud & Infrastructure";
  else if (/engineer|software|technology|cto|product|architecture|data\s+platform|ai|ml/.test(t)) dept = "Product & Engineering";
  else if (/sales|cro|revenue|revops|account|business\s+development|growth/.test(t)) dept = "Sales, RevOps & GTM";
  else if (/finance|cfo|controller|accounting|treasury|legal/.test(t)) dept = "Finance & Legal";
  else if (/marketing|cmo|brand|demand\s+gen/.test(t)) dept = "Marketing";

  // C-Suite
  if (/\b(c[eioftmsra]o|chief\s+[a-z\s]+officer|founder|co-founder|president|managing\s+director|owner|general\s+manager)\b/.test(t)) {
    return {
      raw_title: raw,
      seniority_level: "C-Suite / Founder (+5)",
      seniority_points: 5,
      persona_type: "Economic Buyer",
      department: dept,
      rationale: `Executive leadership authority detected (${raw}) with signatory power.`,
      is_disqualifier: false
    };
  }

  // VP / Head of
  if (/\b(evp|svp|avp|vp|vice\s+president|head\s+of\s+[a-z\s]+|global\s+head|group\s+head)\b/.test(t)) {
    return {
      raw_title: raw,
      seniority_level: "VP / Head of (+5)",
      seniority_points: 5,
      persona_type: "Economic Buyer",
      department: dept,
      rationale: `VP / Department Head authority detected in '${raw}' with budget allocation mandate.`,
      is_disqualifier: false
    };
  }

  // Director
  if (/\b(director|sr\.?\s+director|senior\s+director|associate\s+director)\b/.test(t)) {
    return {
      raw_title: raw,
      seniority_level: "Director (+3)",
      seniority_points: 3,
      persona_type: "Technical Champion / Budget Influencer",
      department: dept,
      rationale: `Director-level champion identified in '${raw}' with direct project influence.`,
      is_disqualifier: false
    };
  }

  // Manager
  if (/\b(manager|lead|team\s+lead|supervisor|operations\s+lead)\b/.test(t)) {
    return {
      raw_title: raw,
      seniority_level: "Manager (+1)",
      seniority_points: 1,
      persona_type: "Technical Champion / Evaluator",
      department: dept,
      rationale: `Management title detected in '${raw}'—key influencer in evaluation cycle.`,
      is_disqualifier: false
    };
  }

  // Individual Contributor
  return {
    raw_title: raw,
    seniority_level: "Individual Contributor (+1)",
    seniority_points: 1,
    persona_type: "End User / Practitioner",
    department: dept,
    rationale: `Professional practitioner role detected in '${raw}'.`,
    is_disqualifier: false
  };
}

function analyzeNiche(niche, sector) {
  const raw = (niche || "").trim();
  if (!raw) {
    return {
      raw_niche: "General Commercial",
      market_complexity: "Standard Commercial",
      fit_points: 3,
      rationale: "Standard industry vertical alignment."
    };
  }

  const n = raw.toLowerCase();
  const highValueKeywords = [
    "oilfield", "solar", "renewable", "subsea", "pipeline", "aerospace",
    "finops", "devops", "cloud infrastructure", "cybersecurity", "autonomous",
    "medical device", "biopharma", "semiconductor", "enterprise erp", "cold chain",
    "freight logistics", "industrial automation", "robotics", "cleantech"
  ];

  for (const kw of highValueKeywords) {
    if (n.includes(kw)) {
      return {
        raw_niche: raw,
        market_complexity: "High-Margin Enterprise",
        fit_points: 5,
        rationale: `High-margin specialized enterprise niche detected: '${raw}'.`
      };
    }
  }

  return {
    raw_niche: raw,
    market_complexity: "Mid-Market Specialized",
    fit_points: 3,
    rationale: `Established B2B market sector: '${raw}'.`
  };
}

function analyzeIntent(intentInput) {
  const raw = (intentInput || "").trim();
  const t = raw.toLowerCase();

  if (/demo|callback|rfp|immediate|urgent|asap|q1|q2|q3|q4|next month|scheduled|\+5/.test(t)) {
    return {
      raw_intent: raw,
      urgency_tier: "Immediate Active Buying (+5)",
      intent_points: 5,
      timeline_detected: "< 30 Days (Active Buying)",
      rationale: "Urgent commercial intent with direct procurement/evaluation engagement."
    };
  }

  if (/pricing|quote|cost|proposal|budget|commercial inquiry|\+3/.test(t)) {
    return {
      raw_intent: raw,
      urgency_tier: "Active Evaluation (+3)",
      intent_points: 3,
      timeline_detected: "30 - 60 Days",
      rationale: "Prospect is actively reviewing commercial terms and budgetary line items."
    };
  }

  return {
    raw_intent: raw || "Exploratory",
    urgency_tier: "Top-of-Funnel / Browsing (+1)",
    intent_points: 1,
    timeline_detected: "60+ Days (Exploratory)",
    rationale: "Exploratory research phase; requires value-add discovery nurturing."
  };
}

function analyzeTechStack(stackNotes) {
  const raw = (stackNotes || "").trim();
  if (!raw) {
    return {
      raw_stack: "Unspecified",
      modern_tools: [],
      legacy_blockers: [],
      ecosystem_fit: "Standard Cloud Baseline (+3)",
      tech_points: 3,
      rationale: "Baseline technology profile; zero known integration blockers."
    };
  }

  const t = raw.toLowerCase();
  const modern = [];
  const legacy = [];

  for (const [kw, desc] of Object.entries(MODERN_ECOSYSTEM_KEYWORDS)) {
    if (t.includes(kw.toLowerCase())) modern.push(`${kw} (${desc})`);
  }

  for (const [kw, desc] of Object.entries(LEGACY_BLOCKER_KEYWORDS)) {
    if (t.includes(kw.toLowerCase())) legacy.push(`${kw} (${desc})`);
  }

  if (legacy.length > 0) {
    return {
      raw_stack: raw,
      modern_tools: modern,
      legacy_blockers: legacy,
      ecosystem_fit: "Legacy Migration Friction (-1)",
      tech_points: -1,
      rationale: `Detected legacy architecture (${legacy.join(", ")}) which may require migration support.`
    };
  }

  if (modern.length >= 2) {
    return {
      raw_stack: raw,
      modern_tools: modern,
      legacy_blockers: [],
      ecosystem_fit: "High Synergies & Native Ecosystem (+5)",
      tech_points: 5,
      rationale: `Strong integration synergy with existing modern stack: ${modern.join(", ")}.`
    };
  } else if (modern.length === 1) {
    return {
      raw_stack: raw,
      modern_tools: modern,
      legacy_blockers: [],
      ecosystem_fit: "Standard Modern Stack (+3)",
      tech_points: 3,
      rationale: `Compatible enterprise infrastructure detected (${modern[0]}).`
    };
  }

  return {
    raw_stack: raw,
    modern_tools: [],
    legacy_blockers: [],
    ecosystem_fit: "Standard Stack (+3)",
    tech_points: 3,
    rationale: "Custom or standard stack noted with no severe blockers."
  };
}

function pointsToScore(pointsArray) {
  if (!pointsArray || pointsArray.length === 0) return 50.0;
  const n = pointsArray.length;
  const sum = pointsArray.reduce((acc, p) => acc + p, 0);
  const norm = ((sum - (-5.0 * n)) / (10.0 * n)) * 100.0;
  return Math.max(0.0, Math.min(100.0, norm));
}

// --- Main Cloudflare Worker Handler ---

export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Content-Type": "application/json"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method === "GET") {
      return new Response(JSON.stringify({
        status: "active",
        service: "Enterprise ICP Revenue Intelligence API",
        version: "2.5",
        capabilities: [
          "AI Role & Persona Semantic Classification",
          "AI Sub-Vertical & Market Complexity Analysis",
          "AI Buying Intent & Timeline Extraction",
          "AI Technographics Ecosystem Parsing",
          "Dynamic Settings-Driven Threshold Evaluation"
        ]
      }), { headers: corsHeaders });
    }

    try {
      const body = await request.json().catch(() => ({}));

      // 1. Prospect Input Data
      const companyName = body.company_name || body.company || "";
      const location = body.location || body.territory || "";
      const industrySector = body.industry_sector || body.industry || "Technology, SaaS & IT";
      const subVertical = body.sub_vertical || body.niche || "";
      const annualRevenue = Number(body.annual_revenue_usd || body.revenue || 0);
      const headcount = Number(body.employee_count || body.headcount || 50);
      const contactName = body.contact_name || body.name || "";
      const contactEmail = (body.contact_email || body.email || "").toLowerCase().trim();
      const roleTitle = body.contact_role_title || body.role_title || body.job_title || "";
      const buyingIntent = body.buying_intent || body.intent_notes || "";
      const targetDealSize = Number(body.target_deal_size_usd || body.deal_size || 0);
      const techStackNotes = body.tech_stack_notes || body.tech_stack || "";

      // 2. Company Standards & Settings Thresholds
      const cfg = body.company_standards || {
        company_name: "My Enterprise Revenue Org",
        min_deal_size_usd: 10000.0,
        target_deal_size_usd: 50000.0,
        min_company_revenue_usd: 2000000.0,
        ideal_revenue_usd: 20000000.0,
        min_headcount: 50,
        ideal_headcount: 250,
        target_focus_industries: [
          "Manufacturing & Industrial Goods",
          "Energy, Utilities & Renewables",
          "Technology, SaaS & IT"
        ],
        tier1_territories: [
          "United States", "United Kingdom", "United Arab Emirates", "European Union",
          "Canada", "Australia", "Singapore", "India", "Germany", "France", "UAE", "UK", "USA"
        ],
        prohibited_countries: ["North Korea", "Iran", "Syria", "Cuba"],
        weight_firmographics: 0.30,
        weight_authority: 0.25,
        weight_intent: 0.25,
        weight_value: 0.20,
        tier_a1_threshold: 80.0,
        tier_a2_threshold: 65.0,
        tier_b1_threshold: 50.0
      };

      // 3. Execute AI Text Field Analysis
      const aiRole = analyzeRole(roleTitle);
      const aiNiche = analyzeNiche(subVertical, industrySector);
      const aiIntent = analyzeIntent(buyingIntent);
      const aiTech = analyzeTechStack(techStackNotes);

      let isDisqualified = false;
      const disqReasons = [];
      const keyStrengths = [];
      const keyRisks = [];
      const discoveryQuestions = [];

      // Pillar 1: Firmographics (Scale & AI Niche)
      const firmoReceipts = [];
      let pRev = -1, rRev = "Revenue unstated";
      if (annualRevenue >= cfg.ideal_revenue_usd) {
        pRev = 5; rRev = `Revenue ($${annualRevenue.toLocaleString()}) exceeds ideal target ($${cfg.ideal_revenue_usd.toLocaleString()})`;
        keyStrengths.push(`Enterprise Revenue: $${annualRevenue.toLocaleString()} ARR`);
      } else if (annualRevenue >= cfg.min_company_revenue_usd) {
        pRev = 3; rRev = `Revenue ($${annualRevenue.toLocaleString()}) meets minimum standard`;
      } else if (annualRevenue > 0) {
        pRev = -1; rRev = `Revenue ($${annualRevenue.toLocaleString()}) below target`;
        keyRisks.push("Sub-scale annual revenue");
      }
      firmoReceipts.push({ field: "Company Revenue", points: pRev, rationale: rRev });

      let pHc = 1, rHc = `Small team (${headcount})`;
      if (headcount >= cfg.ideal_headcount) {
        pHc = 5; rHc = `Headcount (${headcount}) indicates strong organizational scale`;
        keyStrengths.push(`Headcount: ${headcount.toLocaleString()} employees`);
      } else if (headcount >= cfg.min_headcount) {
        pHc = 3; rHc = `Headcount (${headcount}) is within viable operating range`;
      }
      firmoReceipts.push({ field: "Headcount Scale", points: pHc, rationale: rHc });

      let pInd = 3, rInd = `Commercial B2B Industry: ${industrySector}`;
      if (cfg.target_focus_industries.includes(industrySector)) {
        pInd = 5; rInd = `Core focus industry: ${industrySector} [AI Niche: ${aiNiche.market_complexity}]`;
        keyStrengths.push(`Core Target Industry: ${industrySector}`);
      } else if (aiNiche.fit_points === 5) {
        pInd = 5; rInd = `AI High-Margin Niche: ${aiNiche.raw_niche} (${aiNiche.market_complexity})`;
        keyStrengths.push(`High-Margin Niche: ${subVertical}`);
      }
      firmoReceipts.push({ field: "Industry & Niche (AI)", points: pInd, rationale: rInd });

      let pLoc = 3, rLoc = `Supported territory: ${location || 'Global'}`;
      const isProhibited = cfg.prohibited_countries.some(p => (location || '').toLowerCase().includes(p.toLowerCase()));
      if (isProhibited) {
        pLoc = -5; rLoc = `Prohibited sanctioned territory: ${location}`;
        isDisqualified = true; disqReasons.push(rLoc);
      } else if (cfg.tier1_territories.some(t => (location || '').toLowerCase().includes(t.toLowerCase()))) {
        pLoc = 5; rLoc = `Tier 1 supported direct market: ${location}`;
        keyStrengths.push(`Tier 1 Territory: ${location}`);
      }
      firmoReceipts.push({ field: "Location / Territory", points: pLoc, rationale: rLoc });

      const firmoScore = pointsToScore(firmoReceipts.map(r => r.points));

      // Pillar 2: Decision Authority (AI Role Analysis)
      const authReceipts = [];
      const emailDomain = contactEmail.includes("@") ? contactEmail.split("@").pop() : "";
      let pAuth = aiRole.seniority_points;
      let rAuth = `AI Role Analysis: ${aiRole.seniority_level} • Persona: ${aiRole.persona_type} • Dept: ${aiRole.department}`;

      if (DISPOSABLE_DOMAINS.has(emailDomain)) {
        pAuth = -5; rAuth = `Personal freemail address (@${emailDomain})`;
        isDisqualified = true; disqReasons.push(`Freemail domain (@${emailDomain})`);
      } else if (aiRole.is_disqualifier) {
        pAuth = -5; rAuth = `AI Classified Non-Buyer Persona: ${aiRole.seniority_level}`;
        isDisqualified = true; disqReasons.push(`Non-buyer persona (${roleTitle})`);
      } else if (pAuth >= 5) {
        keyStrengths.push(`Executive Economic Buyer: ${contactName || 'Champion'} (${roleTitle}) [${aiRole.department}]`);
      } else if (pAuth >= 3) {
        keyStrengths.push(`Technical Champion: ${roleTitle} [${aiRole.department}]`);
      }

      authReceipts.push({ field: "Contact Role & Authority (AI)", points: pAuth, rationale: rAuth });
      const authScore = pointsToScore(authReceipts.map(r => r.points));

      // Pillar 3: Buying Intent (AI Intent Analysis)
      const intentReceipts = [{
        field: "Buying Intent & Urgency (AI)",
        points: aiIntent.intent_points,
        rationale: `AI Intent: ${aiIntent.urgency_tier} • ${aiIntent.rationale} [Timeline: ${aiIntent.timeline_detected}]`
      }];
      if (aiIntent.intent_points >= 5) keyStrengths.push(`High Intent Velocity: ${aiIntent.urgency_tier}`);
      const intentScore = pointsToScore(intentReceipts.map(r => r.points));

      // Pillar 4: Contract Value & Tech Stack (AI Stack Analysis)
      const valReceipts = [];
      let pDeal = 1, rDeal = "Target contract size unstated";
      if (targetDealSize >= cfg.target_deal_size_usd) {
        pDeal = 5; rDeal = `Deal size ($${targetDealSize.toLocaleString()}) meets ideal target ($${cfg.target_deal_size_usd.toLocaleString()})`;
        keyStrengths.push(`Target Contract Size: $${targetDealSize.toLocaleString()}`);
      } else if (targetDealSize >= cfg.min_deal_size_usd) {
        pDeal = 3; rDeal = `Deal size ($${targetDealSize.toLocaleString()}) meets minimum threshold`;
      } else if (targetDealSize > 0) {
        pDeal = -1; rDeal = `Deal size ($${targetDealSize.toLocaleString()}) below target`;
        keyRisks.push("Deal size is below ideal ACV threshold");
      }
      valReceipts.push({ field: "Contract Size ($)", points: pDeal, rationale: rDeal });

      if (techStackNotes) {
        valReceipts.push({
          field: "Tech Stack Ecosystem (AI)",
          points: aiTech.tech_points,
          rationale: `AI Stack: ${aiTech.ecosystem_fit} • ${aiTech.rationale}`
        });
        if (aiTech.modern_tools.length > 0) keyStrengths.push(`Modern Ecosystem Match: ${aiTech.modern_tools.join(", ")}`);
        if (aiTech.legacy_blockers.length > 0) keyRisks.push(`Legacy Architecture Detected: ${aiTech.legacy_blockers.join(", ")}`);
      }
      const valScore = pointsToScore(valReceipts.map(r => r.points));

      // Master ICP Score Calculation
      let masterScore = 0.0;
      let priorityTier = "Disqualified: Anti-ICP";
      let urgencySla = "No Outreach (Archived)";
      let recommendedChannel = "Do Not Contact";
      let valueWedge = "Account does not meet commercial eligibility compliance.";
      let outreachHook = "Disqualified inquiry.";

      if (!isDisqualified) {
        const rawComposite = (
          (firmoScore * cfg.weight_firmographics) +
          (authScore * cfg.weight_authority) +
          (intentScore * cfg.weight_intent) +
          (valScore * cfg.weight_value)
        );
        masterScore = Number(rawComposite.toFixed(1));

        if (masterScore >= cfg.tier_a1_threshold && intentScore >= 75.0) {
          priorityTier = "Tier A1: Strategic Inbound";
          urgencySla = "< 2 Hours (Executive Callback)";
          recommendedChannel = "Direct Phone & Bespoke Executive Email";
        } else if (masterScore >= cfg.tier_a2_threshold) {
          priorityTier = "Tier A2: High Priority Outbound";
          urgencySla = "< 24 Hours (Dedicated SDR Sequence)";
          recommendedChannel = "Multi-Touch Email & LinkedIn InMail";
        } else if (masterScore >= cfg.tier_b1_threshold) {
          priorityTier = "Tier B1: Mid-Market Fast Track";
          urgencySla = "Within 48 Hours";
          recommendedChannel = "Inside Sales Discovery Call";
        } else {
          priorityTier = "Tier C: Low Priority / Nurture";
          urgencySla = "Automated Marketing Nurture";
          recommendedChannel = "Marketing Newsletter & Documentation";
        }

        const subNiche = subVertical || industrySector;
        const comp = companyName || "your team";
        const contact = contactName || "there";

        valueWedge = `Accelerate operational throughput for ${subNiche} initiatives at ${comp}.`;
        outreachHook = `Hi ${contact}, saw your initiative around ${subNiche} at ${comp}—wanted to share how we support similar ${aiRole.department} teams with tailored integration for your stack.`;
      }

      return new Response(JSON.stringify({
        success: true,
        account: {
          company_name: companyName,
          location: location,
          industry_sector: industrySector,
          sub_vertical: subVertical,
          annual_revenue_usd: annualRevenue,
          employee_count: headcount,
          contact_name: contactName,
          contact_email: contactEmail,
          contact_role_title: roleTitle
        },
        scores: {
          master_icp_score: masterScore,
          priority_tier: priorityTier,
          is_disqualified: isDisqualified,
          disqualification_reason: disqReasons.join("; "),
          pillars: {
            firmographics: { score: Math.round(firmoScore), weight: cfg.weight_firmographics, receipts: firmoReceipts },
            decision_authority: { score: Math.round(authScore), weight: cfg.weight_authority, receipts: authReceipts },
            buying_intent: { score: Math.round(intentScore), weight: cfg.weight_intent, receipts: intentReceipts },
            contract_value: { score: Math.round(valScore), weight: cfg.weight_value, receipts: valReceipts }
          }
        },
        ai_analysis: {
          role: aiRole,
          niche: aiNiche,
          intent: aiIntent,
          tech_stack: aiTech
        },
        strategy: {
          urgency_sla: urgencySla,
          recommended_channel: recommendedChannel,
          value_wedge: valueWedge,
          outreach_hook: outreachHook
        },
        key_strengths: keyStrengths,
        key_risks: keyRisks
      }, null, 2), { headers: corsHeaders });

    } catch (err) {
      return new Response(JSON.stringify({
        success: false,
        error: err.message || String(err)
      }), { status: 500, headers: corsHeaders });
    }
  }
};
