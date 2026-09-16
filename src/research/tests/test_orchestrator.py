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

    def test_detect_flow_divergence_accumulation(self):
        from research.services.orchestrator import detect_flow_divergence
        context = {
            "BBCA_daily_transaction": [{"close": 9500}, {"close": 10000}],
            "BBCA_foreign_flow": [
                {"net_foreign": 50_000_000_000},
                {"net_foreign": 60_000_000_000},
            ],
        }
        divergences = detect_flow_divergence(context, ["BBCA"])
        self.assertEqual(len(divergences), 1)
        self.assertEqual(divergences[0]["type"], "ACCUMULATION_DIVERGENCE")
        self.assertEqual(divergences[0]["symbol"], "BBCA")
        self.assertIn("Accumulation Divergence", divergences[0]["badge_label"])

    def test_detect_flow_divergence_distribution(self):
        from research.services.orchestrator import detect_flow_divergence
        context = {
            "BBRI_daily_transaction": [{"close": 4800}, {"close": 4500}],
            "BBRI_foreign_flow": [
                {"net_foreign": -30_000_000_000},
                {"net_foreign": -40_000_000_000},
            ],
        }
        divergences = detect_flow_divergence(context, ["BBRI"])
        self.assertEqual(len(divergences), 1)
        self.assertEqual(divergences[0]["type"], "DISTRIBUTION_WARNING")
        self.assertEqual(divergences[0]["symbol"], "BBRI")
        self.assertIn("Distribution", divergences[0]["badge_label"])

    def test_build_programmatic_citations(self):
        from research.services.orchestrator import _build_programmatic_citations
        context = {
            "BBCA_company_report": {
                "overview": {"company_name": "Bank Central Asia Tbk", "market_cap": 1200000000000000},
                "valuation": {"pe_ratio": 23.4, "pb_ratio": 4.8},
            },
            "BBCA_daily_transaction": [{"date": "2026-09-15", "close": 9975}],
            "BBCA_foreign_flow": [{"date": "2026-09-15", "net_foreign": 45000000000}],
        }
        citations = _build_programmatic_citations(context, ["BBCA"])
        self.assertTrue(len(citations) >= 2)
        endpoints = [c["source_endpoint"] for c in citations]
        self.assertIn("/v2/company/report/BBCA/", endpoints)
        self.assertIn("/v2/foreign-flow/BBCA/", endpoints)
