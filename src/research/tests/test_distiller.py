import os
from django.test import TestCase

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
import django
django.setup()

from research.services.data_distiller import (
    distill_company_report,
    distill_daily_transactions,
    distill_foreign_flow,
    distill_quarterly,
    distill_broker_summary,
    distill_news,
    distill_context,
)


class DataDistillerTests(TestCase):
    def test_distill_company_report(self):
        raw = {
            "overview": {
                "symbol": "BBCA.JK",
                "company_name": "Bank Central Asia Tbk",
                "industry": "Financials",
                "sub_sector": "Banks",
                "market_cap": 1_200_000_000_000_000,
                "extra_metadata_unneeded": "ignore_me",
            },
            "valuation": {
                "pe_ratio": 23.5,
                "pb_ratio": 4.8,
                "ps_ratio": 12.0,
                "dividend_yield": 0.024,
                "roe": 0.21,
                "roa": 0.038,
            },
            "financials": {
                "revenue": 98_000_000_000_000,
                "net_income": 48_000_000_000_000,
                "total_assets": 1_400_000_000_000_000,
            },
        }
        res = distill_company_report(raw)
        self.assertEqual(res["symbol"], "BBCA.JK")
        self.assertEqual(res["name"], "Bank Central Asia Tbk")
        self.assertEqual(res["pe_ratio"], 23.5)
        self.assertEqual(res["roe"], 0.21)
        self.assertNotIn("extra_metadata_unneeded", res)

    def test_distill_daily_transactions(self):
        raw = [
            {"date": f"2026-09-{i:02d}", "close": 10000 + i * 50, "volume": 1000000}
            for i in range(1, 31)
        ]
        # raw has 30 items
        res = distill_daily_transactions(raw)
        self.assertEqual(res["record_count"], 30)
        self.assertEqual(res["latest_close"], 10050)
        self.assertEqual(res["period_start_close"], 11500)
        self.assertIsNotNone(res["period_change_pct"])
        self.assertEqual(len(res["recent_5_days_close"]), 5)

    def test_distill_foreign_flow(self):
        raw = [
            {"date": f"2026-09-{i:02d}", "net_foreign": 100_000_000 if i % 2 == 0 else -50_000_000}
            for i in range(1, 31)
        ]
        res = distill_foreign_flow(raw)
        self.assertEqual(res["inflow_days"], 15)
        self.assertEqual(res["outflow_days"], 15)
        self.assertGreater(res["period_total_net_foreign_idr"], 0)

    def test_distill_quarterly(self):
        raw = [
            {"quarter": f"Q{i}", "year": 2025, "revenue": 1000, "net_income": 200, "revenue_growth_yoy": 0.1}
            for i in range(1, 10)
        ]
        res = distill_quarterly(raw)
        self.assertEqual(len(res), 4)
        self.assertEqual(res[0]["quarter"], "Q1")
        self.assertEqual(res[0]["revenue"], 1000)

    def test_distill_broker_summary(self):
        raw = {
            "top_buyers": [{"broker_code": f"B{i}", "buy_value": 1000 * i} for i in range(1, 10)],
            "top_sellers": [{"broker_code": f"S{i}", "sell_value": 500 * i} for i in range(1, 10)],
        }
        res = distill_broker_summary(raw)
        self.assertEqual(len(res["top_buyers"]), 3)
        self.assertEqual(len(res["top_sellers"]), 3)
        self.assertEqual(res["top_buyers"][0]["broker"], "B1")

    def test_distill_news(self):
        raw = [{"published_at": "2026-09-01T12:00:00Z", "title": f"Headline {i}", "body": "long body" * 100} for i in range(10)]
        res = distill_news(raw)
        self.assertEqual(len(res), 3)
        self.assertNotIn("body", res[0])

    def test_distill_context_full(self):
        raw_context = {
            "symbols": ["BBCA"],
            "dates": {"start": "2026-08-01", "end": "2026-08-30"},
            "BBCA_company_report": {
                "overview": {"symbol": "BBCA.JK", "company_name": "Bank Central Asia"},
                "valuation": {"pe_ratio": 23.0},
            },
            "BBCA_daily_transaction": [
                {"date": "2026-08-30", "close": 10200, "volume": 5000000},
                {"date": "2026-08-29", "close": 10100, "volume": 4000000},
            ],
            "BBCA_foreign_flow": [
                {"date": "2026-08-30", "net_foreign": 50000000},
            ],
        }
        distilled = distill_context(raw_context)
        self.assertEqual(distilled["symbols"], ["BBCA"])
        self.assertIn("BBCA_company_report", distilled)
        self.assertIn("BBCA_daily_transaction", distilled)
        self.assertIn("BBCA_foreign_flow", distilled)
        self.assertEqual(distilled["BBCA_company_report"]["pe_ratio"], 23.0)
