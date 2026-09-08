"""
Comprehensive Test Suite for 100% Dynamic Qualification Engine.
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from engine import ProspectExtractor, PillarScorer


class TestDynamicQualification(unittest.TestCase):
    def test_dynamic_enterprise_qualification(self):
        """Test dynamic AI-driven scoring for Enterprise Tier 1."""
        ai_sim = {
            "company_name": "NextEra Clean Infrastructure",
            "contact_name": "Arthur Pendelton",
            "job_title": "VP of Strategy",
            "industry": "Renewable Energy",
            "is_disqualified": False,
            "final_icp_score": 95,
            "pillar_scores": {
                "firmographic_score": 95,
                "firmographic_rationale": "Enterprise-scale global commercial footprint ($450M ARR).",
                "technographic_score": 95,
                "technographic_rationale": "Advanced enterprise data warehouse (SAP, Snowflake).",
                "intent_score": 95,
                "intent_rationale": "Immediate RFP CapEx mandate due in 3 weeks.",
                "persona_score": 95,
                "persona_rationale": "VP of Strategy holds direct corporate budget signing power."
            },
            "strategy": {
                "value_wedge": "De-risk active multi-GW renewable portfolio investment.",
                "outreach_hook": "Hi Arthur, saw NextEra's strategic expansion in the market."
            }
        }
        prospect = ProspectExtractor.extract("raw text", ai_data=ai_sim)
        breakdown = PillarScorer.evaluate_all_pillars(prospect)
        res = PillarScorer.compute_master_score(prospect, breakdown, deal_size_usd=100000.0)

        self.assertEqual(prospect.company_name, "NextEra Clean Infrastructure")
        self.assertEqual(breakdown.persona.gtm_scale, 5)
        self.assertEqual(res.final_score, 95)
        self.assertIn("Tier 1", res.tier_name)
        self.assertEqual(res.quality_weighted_value, 95000.0)
        self.assertEqual(res.crm_payload["ICP_Score_Total__c"], 95)

    def test_dynamic_disqualification(self):
        """Test dynamic negative scoring for student/academic inquiries."""
        ai_sim = {
            "company_name": "Stanford University",
            "contact_name": "Emily Green",
            "job_title": "Graduate Student",
            "industry": "Higher Education",
            "is_disqualified": True,
            "disqualification_reason": "Academic inquiry with zero commercial budget authority",
            "final_icp_score": 12,
            "pillar_scores": {
                "firmographic_score": 15,
                "technographic_score": 20,
                "intent_score": 10,
                "persona_score": 0
            }
        }
        prospect = ProspectExtractor.extract("raw text", ai_data=ai_sim)
        breakdown = PillarScorer.evaluate_all_pillars(prospect)
        res = PillarScorer.compute_master_score(prospect, breakdown, deal_size_usd=50000.0)

        self.assertTrue(res.is_disqualified)
        self.assertIn("Disqualified", res.tier_name)
        self.assertEqual(res.final_score, 12)
        self.assertEqual(res.conversion_probability, 2)


if __name__ == "__main__":
    unittest.main()
