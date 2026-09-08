"""
Comprehensive Test Suite for Steps 1 through 4 of the ICP Scoring Engine.
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from engine import ProspectExtractor, PillarScorer


class TestCompleteICPQualification(unittest.TestCase):
    def test_step1_extraction_and_uncertainty(self):
        """Test Step 1 extraction and uncertainty detection."""
        text = "Company: Acme Corp\nContact: Sarah Jenkins (VP Marketing)\nInquiry: Need pricing."
        prospect = ProspectExtractor.extract(text)
        
        self.assertEqual(prospect.company_name, "Acme Corp")
        self.assertEqual(prospect.contact_name, "Sarah Jenkins")
        self.assertEqual(prospect.job_title, "VP Marketing")
        self.assertIn("Technographic Infrastructure", prospect.uncertain_fields)
        self.assertGreater(len(prospect.discovery_questions), 0)

    def test_step2_gtm_polarized_scale(self):
        """Test Step 2 polarized scoring on -5 to +5 scale."""
        text = "Company: Enterprise NextGen\nContact: Arthur (Chief Strategy Officer)\nARR: $500M | 10,000 Employees\nTech: SAP, Salesforce, Snowflake\nInquiry: Active RFP proposal due in 3 weeks."
        prospect = ProspectExtractor.extract(text)
        breakdown = PillarScorer.evaluate_all_pillars(prospect)
        
        self.assertEqual(breakdown.firmographic.gtm_scale, 5)
        self.assertEqual(breakdown.technographic.gtm_scale, 5)
        self.assertEqual(breakdown.intent.gtm_scale, 5)
        self.assertEqual(breakdown.persona.gtm_scale, 5)

    def test_step3_master_score_and_revenue_forecast(self):
        """Test Step 3 master score aggregation and deal forecasting."""
        text = "Company: Enterprise NextGen\nContact: Arthur (Chief Strategy Officer)\nARR: $500M | 10,000 Employees\nTech: SAP, Salesforce, Snowflake\nInquiry: Active RFP proposal due in 3 weeks."
        prospect = ProspectExtractor.extract(text)
        breakdown = PillarScorer.evaluate_all_pillars(prospect)
        res = PillarScorer.compute_master_score(prospect, breakdown, deal_size_usd=100000.0)
        
        self.assertEqual(res.final_score, 95)
        self.assertIn("Tier 1", res.tier_name)
        self.assertEqual(res.quality_weighted_value, 95000.0)

    def test_step4_operational_cadence_and_crm(self):
        """Test Step 4 sales cadence, 2D matrix, and CRM payload."""
        text = "Company: Enterprise NextGen\nContact: Arthur (Chief Strategy Officer)\nARR: $500M | 10,000 Employees\nTech: SAP, Salesforce, Snowflake\nInquiry: Active RFP proposal due in 3 weeks."
        prospect = ProspectExtractor.extract(text)
        breakdown = PillarScorer.evaluate_all_pillars(prospect)
        res = PillarScorer.compute_master_score(prospect, breakdown, deal_size_usd=100000.0)
        
        self.assertIn("<2h", res.sales_action)
        self.assertGreaterEqual(res.fit_index, 90)
        self.assertGreaterEqual(res.intent_index, 90)
        self.assertIn("ICP_Score_Total__c", res.crm_payload)
        self.assertEqual(res.crm_payload["ICP_Score_Total__c"], 95)


if __name__ == "__main__":
    unittest.main()
