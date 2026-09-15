import os
from unittest.mock import patch

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

import django
django.setup()

from django.core.cache import cache
from django.test import TestCase

from research.services.sectors_api import (
    get_broker_summary_top,
    get_company_report,
    get_corporate_actions,
    get_daily,
    get_foreign_flow,
    get_news,
    get_quarterly,
    get_screener,
    get_sector_report,
)


class SectorsAPIModuleTest(TestCase):
    def test_module_has_all_functions(self):
        self.assertTrue(callable(get_company_report))
        self.assertTrue(callable(get_daily))
        self.assertTrue(callable(get_quarterly))
        self.assertTrue(callable(get_broker_summary_top))
        self.assertTrue(callable(get_foreign_flow))
        self.assertTrue(callable(get_news))
        self.assertTrue(callable(get_corporate_actions))
        self.assertTrue(callable(get_screener))
        self.assertTrue(callable(get_sector_report))


class CompanyReportEndpointTest(TestCase):
    def test_company_report_uses_official_v2_path(self):
        with patch("research.services.sectors_api.requests.get") as request_get:
            request_get.return_value.status_code = 200
            request_get.return_value.json.return_value = {"symbol": "BBCA.JK"}
            with self.settings(SECTORS_API_KEY="test_key_123"):
                cache.clear()
                get_company_report("BBCA", "overview")

            self.assertIn("/v2/company/report/BBCA/", request_get.call_args.args[0])
            self.assertEqual(request_get.call_args.kwargs["params"], {"sections": "overview"})


class CacheTest(TestCase):
    def test_cache_set_and_get(self):
        cache.set("test_key", {"data": "hello"}, 60)
        result = cache.get("test_key")
        self.assertEqual(result["data"], "hello")

    def test_cache_miss(self):
        result = cache.get("nonexistent_key_xyz")
        self.assertIsNone(result)

    def test_cache_overwrite(self):
        cache.set("ow_key", "first", 60)
        cache.set("ow_key", "second", 60)
        result = cache.get("ow_key")
        self.assertEqual(result, "second")
