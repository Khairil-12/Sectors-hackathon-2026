import os
from unittest.mock import patch

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

import django
django.setup()

from django.test import Client, TestCase
from research.models import SavedReport, WatchlistItem


class ViewRoutingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_report = SavedReport.objects.create(
            title="Equity Research: BBCA",
            symbols=["BBCA"],
            user_prompt="Analisis BBCA",
            report_data={
                "title": "Equity Research: BBCA",
                "summary": "Sample summary for BBCA",
                "analyzed_symbols": ["BBCA"],
                "fundamental_analysis": {
                    "valuation_verdict": "fair",
                    "pe_pb_commentary": "P/E 23.4x",
                    "revenue_profit_trend": "Growing steadily",
                },
                "flow_and_momentum": {
                    "foreign_flow_sentiment": "strong_inflow",
                    "net_foreign_amount_idr": 45000000000,
                    "top_broker_action": "Accumulation by ZP",
                    "price_trend_summary": "Steady consolidation",
                },
                "bullish_drivers": ["Market leader"],
                "bearish_risks": ["Rate volatility"],
                "data_citations": [
                    {
                        "source_endpoint": "/v2/company/report/BBCA/",
                        "as_of_date": "2026-09-15",
                        "key_datapoints": "P/E: 23.4x",
                    }
                ],
                "disclaimer": "Bukan rekomendasi beli atau jual.",
            },
        )
        self.sample_watchlist = WatchlistItem.objects.create(symbol="BBCA")

    def test_workspace_get_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Research Workspace")
        self.assertContains(response, "app.css")

    @patch("research.views.run_analysis")
    def test_workspace_post_valid_prompt_returns_redirect_json(self, mock_run_analysis):
        mock_run_analysis.return_value = {
            "intent": {"analysis_type": "single_stock", "symbols": ["BBCA"]},
            "report": {
                "title": "Equity Research: BBCA",
                "summary": "BBCA shows solid fundamentals.",
                "analyzed_symbols": ["BBCA"],
                "fundamental_analysis": {
                    "valuation_verdict": "fair",
                    "pe_pb_commentary": "PE 23.4x",
                    "revenue_profit_trend": "Positive",
                },
                "flow_and_momentum": {
                    "foreign_flow_sentiment": "strong_inflow",
                    "net_foreign_amount_idr": 1000000000,
                    "top_broker_action": "Net buy",
                    "price_trend_summary": "Upward",
                },
                "bullish_drivers": ["Strong ROE"],
                "bearish_risks": ["Competition"],
                "data_citations": [
                    {"source_endpoint": "/v2/company/report/BBCA/", "as_of_date": "2026-09-15", "key_datapoints": "PE: 23.4x"}
                ],
                "disclaimer": "Bukan rekomendasi beli atau jual.",
            },
        }
        response = self.client.post("/", {"prompt": "Bandingkan BBCA dan BMRI"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("redirect", data)
        self.assertIn("reportId", data)
        self.assertTrue(SavedReport.objects.filter(pk=data["reportId"]).exists())

    @patch("research.views.run_analysis")
    def test_workspace_post_standard_form_redirects_to_report(self, mock_run_analysis):
        mock_run_analysis.return_value = {
            "intent": {"analysis_type": "single_stock", "symbols": ["BBCA"]},
            "report": {
                "title": "Equity Research: BBCA",
                "summary": "BBCA shows solid fundamentals.",
                "analyzed_symbols": ["BBCA"],
                "fundamental_analysis": {
                    "valuation_verdict": "fair",
                    "pe_pb_commentary": "PE 23.4x",
                    "revenue_profit_trend": "Positive",
                },
                "flow_and_momentum": {
                    "foreign_flow_sentiment": "strong_inflow",
                    "net_foreign_amount_idr": 1000000000,
                    "top_broker_action": "Net buy",
                    "price_trend_summary": "Upward",
                },
                "bullish_drivers": ["Strong ROE"],
                "bearish_risks": ["Competition"],
                "data_citations": [],
                "disclaimer": "Disclaimer",
            },
        }
        response = self.client.post("/", {"prompt": "Analisis komprehensif saham BBCA"})
        self.assertEqual(response.status_code, 302)
        saved = SavedReport.objects.filter(user_prompt="Analisis komprehensif saham BBCA").first()
        self.assertIsNotNone(saved)
        self.assertRedirects(response, f"/report/{saved.pk}/")

    def test_workspace_post_invalid_short_prompt_returns_400(self):
        response = self.client.post("/", {"prompt": "a"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_report_detail_view_success(self):
        response = self.client.get(f"/report/{self.sample_report.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Equity Research: BBCA")
        self.assertContains(response, "Sample summary for BBCA")
        self.assertContains(response, "Verdict: Fair Value")

    def test_report_detail_view_404_for_nonexistent(self):
        response = self.client.get("/report/999999/")
        self.assertEqual(response.status_code, 404)

    def test_report_delete_action(self):
        pk = self.sample_report.pk
        response = self.client.post(f"/report/{pk}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SavedReport.objects.filter(pk=pk).exists())

    def test_report_delete_htmx_action(self):
        report2 = SavedReport.objects.create(
            title="Temp Report",
            symbols=["TLKM"],
            user_prompt="TLKM",
            report_data={"title": "Temp Report", "summary": "...", "analyzed_symbols": ["TLKM"]},
        )
        response = self.client.post(f"/report/{report2.pk}/delete/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SavedReport.objects.filter(pk=report2.pk).exists())

    def test_comparison_view_get(self):
        response = self.client.get("/compare/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock Comparison")

    @patch("research.views.run_comparison")
    def test_comparison_view_with_symbols(self, mock_comp):
        mock_comp.return_value = [
            {"symbol": "BBCA", "company_name": "Bank Central Asia", "sub_sector": "Banks", "industry": "Financials", "last_price": 9975, "market_cap": 1230000000000000, "pe_ratio": 23.4, "pb_ratio": 4.8, "dividend_yield": 2.4, "roe": 21.5, "net_foreign_30d": 45000000000},
            {"symbol": "BMRI", "company_name": "Bank Mandiri", "sub_sector": "Banks", "industry": "Financials", "last_price": 6850, "market_cap": 640000000000000, "pe_ratio": 11.8, "pb_ratio": 2.1, "dividend_yield": 5.1, "roe": 19.8, "net_foreign_30d": 30000000000},
        ]
        response = self.client.get("/compare/?symbols=BBCA,BMRI")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BBCA")
        self.assertContains(response, "BMRI")
        self.assertContains(response, "Market Capitalization")

    def test_screener_view_get(self):
        response = self.client.get("/screener/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IDX Equity Screener")

    @patch("research.services.sectors_api.get_screener")
    def test_screener_view_with_preset_banks(self, mock_screener):
        mock_screener.return_value = [
            {"symbol": "BBCA.JK", "company_name": "Bank Central Asia", "sub_sector": "Banks", "market_cap": 1230000000000000, "pe_ratio": 23.4, "pb_ratio": 4.8, "dividend_yield": 2.4}
        ]
        response = self.client.get("/screener/?preset=banks")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screening Results")
        self.assertContains(response, "BBCA.JK")

    @patch("research.services.sectors_api.get_screener")
    def test_screener_view_post_query(self, mock_screener):
        mock_screener.return_value = [
            {"symbol": "BMRI.JK", "company_name": "Bank Mandiri", "sub_sector": "Banks", "market_cap": 640000000000000, "pe_ratio": 11.8, "pb_ratio": 2.1, "dividend_yield": 5.1}
        ]
        response = self.client.post("/screener/", {"query": "banking"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screening Results")
        self.assertContains(response, "BMRI.JK")

    @patch("research.services.sectors_api.get_top_changes")
    @patch("research.services.sectors_api.get_most_traded")
    def test_dashboard_view(self, mock_traded, mock_movers):
        mock_movers.return_value = [
            {"symbol": "BBCA.JK", "company_name": "Bank Central Asia", "price": 9975, "change_pct": 1.79}
        ]
        mock_traded.return_value = [
            {"symbol": "BBRI.JK", "company_name": "Bank Rakyat Indonesia", "value": 444000000000}
        ]
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Market Dashboard")
        self.assertContains(response, "My Watchlist")
        self.assertContains(response, "BBCA")
        self.assertContains(response, "BBRI")

    @patch("research.services.sectors_api.get_company_report")
    @patch("research.services.sectors_api.get_top_changes")
    @patch("research.services.sectors_api.get_most_traded")
    def test_dashboard_view_displays_real_company_name_and_percentage(self, mock_traded, mock_movers, mock_rep):
        mock_movers.return_value = []
        mock_traded.return_value = []
        mock_rep.return_value = {
            "symbol": "BBCA.JK",
            "company_name": "PT Bank Central Asia Tbk.",
            "overview": {
                "symbol": "BBCA.JK",
                "company_name": "PT Bank Central Asia Tbk.",
                "last_close_price": 9975,
                "daily_close_change": 0.0179,
            },
            "valuation": {
                "last_close_price": 9975,
                "daily_close_change": 0.0179,
            },
        }
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PT Bank Central Asia Tbk.")
        self.assertContains(response, "+1.79%")
        self.assertContains(response, "9,975")
        # Verify remove button is present in the watchlist card
        self.assertContains(response, f"/watchlist/remove/{self.sample_watchlist.pk}/")

    @patch("research.services.sectors_api.get_top_changes")
    @patch("research.services.sectors_api.get_most_traded")
    def test_dashboard_view_dict_response(self, mock_traded, mock_movers):
        mock_movers.return_value = {
            "top_gainers": {
                "1d": [
                    {
                        "symbol": "SRAJ.JK",
                        "name": "Sejahteraraya Anugrahjaya Tbk",
                        "last_close_price": 15600,
                        "price_change": 0.2,
                    }
                ]
            }
        }
        mock_traded.return_value = {
            "2026-09-14": [
                {
                    "symbol": "BUMI.JK",
                    "company_name": "Bumi Resources Tbk",
                    "volume": 5685408800,
                    "price": 208,
                }
            ]
        }
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SRAJ")
        self.assertContains(response, "BUMI")
        self.assertContains(response, "20.00%")

    def test_watchlist_view_redirects_to_dashboard(self):
        response = self.client.get("/watchlist/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")

    def test_watchlist_add_valid_symbol(self):
        response = self.client.post("/watchlist/add/", {"symbol": "TLKM"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        self.assertTrue(WatchlistItem.objects.filter(symbol="TLKM").exists())

    def test_watchlist_remove_action_standard_post(self):
        item_id = self.sample_watchlist.pk
        response = self.client.post(f"/watchlist/remove/{item_id}/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
        self.assertFalse(WatchlistItem.objects.filter(pk=item_id).exists())

    def test_watchlist_remove_action_htmx(self):
        item_id = self.sample_watchlist.pk
        response = self.client.post(f"/watchlist/remove/{item_id}/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(WatchlistItem.objects.filter(pk=item_id).exists())

    def test_saved_reports_view_get(self):
        response = self.client.get("/saved-reports/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved AI Research Reports")
        self.assertContains(response, "Equity Research: BBCA")

    def test_saved_reports_search_filter(self):
        response = self.client.get("/saved-reports/?q=BBCA")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Equity Research: BBCA")

    @patch("research.views._client")
    def test_report_ask_view_success(self, mock_client_func):
        from unittest.mock import MagicMock
        mock_resp = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "BBCA exhibits strong net interest margin and consistent ROE above 20%."
        mock_resp.choices = [mock_choice]
        mock_client_func.return_value.chat.completions.create.return_value = mock_resp

        with self.settings(GROQ_API_KEY="gsk_test_key_valid"):
            response = self.client.post(
                f"/report/{self.sample_report.pk}/ask/",
                {"question": "Bagaimana ketahanan profitabilitas BBCA?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bagaimana ketahanan profitabilitas BBCA?")
        self.assertContains(response, "BBCA exhibits strong net interest margin")

    def test_report_ask_view_fallback_without_key(self):
        with self.settings(GROQ_API_KEY=""):
            response = self.client.post(
                f"/report/{self.sample_report.pk}/ask/",
                {"question": "Bagaimana valuasi BBCA?"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berdasarkan data laporan")

    def test_report_ask_view_empty_question(self):
        response = self.client.post(
            f"/report/{self.sample_report.pk}/ask/",
            {"question": "  "},
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Pertanyaan follow-up minimal 3 karakter", status_code=400)

    def test_report_ask_view_404_for_nonexistent_report(self):
        response = self.client.post(
            "/report/999999/ask/",
            {"question": "Any question"},
        )
        self.assertEqual(response.status_code, 404)
