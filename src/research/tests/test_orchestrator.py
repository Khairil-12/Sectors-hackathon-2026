import os
from unittest.mock import patch

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

import django
django.setup()

from django.test import TestCase
from research.services.orchestrator import run_analysis, run_comparison, _safe_dates, _symbols


class OrchestratorTests(TestCase):
    def test_safe_dates_valid_window(self):
        intent = {"date_range": {"start": "2026-08-01", "end": "2026-08-20"}}
        dates = _safe_dates(intent)
        self.assertEqual(dates["start"], "2026-08-01")
        self.assertEqual(dates["end"], "2026-08-20")

    def test_safe_dates_handles_corrupt_values(self):
        intent = {"date_range": {"start": "invalid-date", "end": "2026-08-20"}}
        dates = _safe_dates(intent)
        self.assertIn("start", dates)
        self.assertIn("end", dates)

    def test_symbols_normalization(self):
        intent = {"symbols": ["bbca.jk", "bmri", "INVALID123", "BBCA"]}
        symbols = _symbols(intent)
        self.assertIn("BBCA", symbols)
        self.assertIn("BMRI", symbols)
        self.assertEqual(len(symbols), 2)

    @patch("research.services.groq_client._call_groq_json")
    def test_run_analysis_single_stock(self, mock_groq):
        mock_groq.side_effect = [
            {"analysis_type": "single_stock", "symbols": ["BBCA"], "required_endpoints": ["company_report"], "user_goal_summary": "Analysis of BBCA"},
            {
                "title": "Equity Research: BBCA",
                "summary": "Solid fundamentals.",
                "analyzed_symbols": ["BBCA"],
                "fundamental_analysis": {"valuation_verdict": "fair", "pe_pb_commentary": "PE 23x", "revenue_profit_trend": "Growing"},
                "flow_and_momentum": {"foreign_flow_sentiment": "strong_inflow", "net_foreign_amount_idr": 1000000000, "top_broker_action": "Buy", "price_trend_summary": "Up"},
                "bullish_drivers": ["Market leader"],
                "bearish_risks": ["Rate risk"],
                "data_citations": [{"source_endpoint": "/v2/company/report/BBCA/", "as_of_date": "2026-09-15", "key_datapoints": "PE: 23x"}],
                "disclaimer": "Disclaimer here",
            },
        ]
        with self.settings(SECTORS_API_KEY=""):
            result = run_analysis("Analisis fundamental saham BBCA")
        self.assertIn("intent", result)
        self.assertIn("report", result)
        report = result["report"]
        self.assertIn("title", report)
        self.assertIn("fundamental_analysis", report)
        self.assertIn("flow_and_momentum", report)
        self.assertIn("data_citations", report)

    def test_run_comparison_multi_stock(self):
        with self.settings(SECTORS_API_KEY=""):
            result = run_comparison(["BBCA", "BMRI"])
        self.assertEqual(len(result), 2)
        symbols = [item["symbol"] for item in result]
        self.assertIn("BBCA", symbols)
        self.assertIn("BMRI", symbols)
        for item in result:
            self.assertIn("company_name", item)
            self.assertIn("pe_ratio", item)
