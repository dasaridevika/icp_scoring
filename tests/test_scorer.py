"""
Unit tests for the modular ICP Qualification & Scoring Engine.
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from engine.scorer import ICPScoringEngine, evaluate_prospect
from engine.models import ICPScoreResult


class TestICPScoringEngine(unittest.TestCase):
    def test_weights_sum_to_one(self):
        """Ensure mathematical pillar weights sum exactly to 1.0 (100%)."""
        total_weight = (
            ICPScoringEngine.WEIGHT_FIRMOGRAPHIC +
            ICPScoringEngine.WEIGHT_TECHNOGRAPHIC +
            ICPScoringEngine.WEIGHT_INTENT +
            ICPScoringEngine.WEIGHT_PERSONA
        )
        self.assertAlmostEqual(total_weight, 1.0, places=4)

    def test_tier1_enterprise_prospect(self):
        """Test a Tier 1 Dream ICP prospect scoring."""
        raw_ai = {
            "company_name": "NextEra Clean Infrastructure",
            "contact_name": "Arthur Pendelton",
            "job_title": "VP Strategy & Corporate Development",
            "industry": "Renewable Energy",
            "is_disqualified": False,
            "pillar_scores": {
                "firmographic_score": 92,
                "firmographic_rationale": "Global enterprise with $450M ARR.",
                "technographic_score": 88,
                "technographic_rationale": "Enterprise SAP & Salesforce infrastructure.",
                "intent_score": 94,
                "intent_rationale": "Active CapEx proposal due in 3 weeks.",
                "persona_score": 95,
                "persona_rationale": "Direct executive investment budget authority."
            }
        }
        res = evaluate_prospect(raw_ai, deal_size_usd=100000.0)
        
        # Expected: (92 * 0.30) + (88 * 0.25) + (94 * 0.25) + (95 * 0.20) = 27.6 + 22.0 + 23.5 + 19.0 = 92.1 -> 92
        self.assertEqual(res.final_icp_score, 92)
        self.assertIn("Tier 1", res.saber_tier)
        self.assertEqual(res.priority_level, "High Priority / Strategic Account")
        self.assertIn("<2h", res.sales_action)
        self.assertEqual(res.quality_weighted_value, 92000.0)
        self.assertFalse(res.is_disqualified)
        self.assertGreaterEqual(res.conversion_probability, 80)
        
        # Check CRM fields
        self.assertEqual(res.crm_payload["ICP_Score_Total__c"], 92)
        self.assertEqual(res.crm_payload["ICP_Firmographic_Score__c"], 92)

    def test_tier2_midmarket_prospect(self):
        """Test a Tier 2 Strong Fit mid-market prospect."""
        raw_ai = {
            "company_name": "Apex Cloud Analytics",
            "contact_name": "Marcus Vance",
            "job_title": "Head of Growth",
            "industry": "SaaS",
            "is_disqualified": False,
            "pillar_scores": {
                "firmographic_score": 75,
                "technographic_score": 70,
                "intent_score": 68,
                "persona_score": 72
            }
        }
        res = evaluate_prospect(raw_ai, deal_size_usd=50000.0)
        # Expected: (75*0.30) + (70*0.25) + (68*0.25) + (72*0.20) = 22.5 + 17.5 + 17.0 + 14.4 = 71.4 -> 71
        self.assertEqual(res.final_icp_score, 71)
        self.assertIn("Tier 2", res.saber_tier)
        self.assertEqual(res.priority_level, "Standard Sales Pipeline")
        self.assertIn("24h", res.sales_action)
        self.assertEqual(res.quality_weighted_value, 35500.0)

    def test_student_disqualification(self):
        """Test negative scoring: students / academic leads are disqualified."""
        text = "Name: Emily Green\nTitle: Graduate Student\nUniversity: Stanford University\nInquiry: Research for class assignment thesis paper."
        raw_ai = {
            "company_name": "Stanford University",
            "contact_name": "Emily Green",
            "job_title": "Graduate Student",
            "industry": "Education",
            "is_disqualified": True,
            "disqualification_reason": "Academic / Student inquiry",
            "pillar_scores": {
                "firmographic_score": 15,
                "technographic_score": 20,
                "intent_score": 10,
                "persona_score": 0
            }
        }
        res = evaluate_prospect(raw_ai, raw_text=text, deal_size_usd=50000.0)
        self.assertTrue(res.is_disqualified)
        self.assertIn("Disqualified", res.saber_tier)
        self.assertLessEqual(res.final_icp_score, 20)
        self.assertIn("Preserve AE", res.sales_action)
        self.assertEqual(res.conversion_probability, 2)


if __name__ == "__main__":
    unittest.main()
