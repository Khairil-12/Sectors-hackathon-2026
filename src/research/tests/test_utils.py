from __future__ import annotations

from django.test import SimpleTestCase
from django.template import Context, Template
from research.utils import clean_symbol, format_currency, format_percent, format_ratio
from research.templatetags.research_tags import (
    currency_filter,
    percent_filter,
    ratio_filter,
    ticker_filter,
)


class ResearchUtilsTests(SimpleTestCase):
    def test_clean_symbol(self):
        self.assertEqual(clean_symbol("BBCA.JK"), "BBCA")
        self.assertEqual(clean_symbol("bbri.jk"), "BBRI")
        self.assertEqual(clean_symbol("TLKM"), "TLKM")
        self.assertEqual(clean_symbol("  GOTO.JK  "), "GOTO")
        self.assertEqual(clean_symbol(None), "")
        self.assertEqual(clean_symbol(""), "")

    def test_format_currency_short(self):
        self.assertEqual(format_currency(771_917_544_337_500), "Rp 771.92 T")
        self.assertEqual(format_currency(450_500_000_000), "Rp 450.50 B")
        self.assertEqual(format_currency(12_300_000), "Rp 12.30 M")
        self.assertEqual(format_currency(9_500), "Rp 9,500")
        self.assertEqual(format_currency(500), "Rp 500")
        self.assertEqual(format_currency(-1_500_000_000_000), "-Rp 1.50 T")
        self.assertEqual(format_currency("771917544337500"), "Rp 771.92 T")
        self.assertEqual(format_currency("Rp 450,500,000,000"), "Rp 450.50 B")
        self.assertEqual(format_currency(None), "N/A")
        self.assertEqual(format_currency("N/A"), "N/A")
        self.assertEqual(format_currency(""), "N/A")

    def test_format_currency_full(self):
        self.assertEqual(
            format_currency(771_917_544_337_500, short=False),
            "Rp 771,917,544,337,500",
        )
        self.assertEqual(format_currency(9500, short=False), "Rp 9,500")
        self.assertEqual(format_currency(9500.5, short=False), "Rp 9,500.50")

    def test_format_ratio(self):
        self.assertEqual(format_ratio(23.4), "23.40x")
        self.assertEqual(format_ratio("23.4x"), "23.40x")
        self.assertEqual(format_ratio(4.815, decimals=1), "4.8x")
        self.assertEqual(format_ratio(None), "N/A")
        self.assertEqual(format_ratio("N/A"), "N/A")
        self.assertEqual(format_ratio("invalid"), "invalid")

    def test_format_percent(self):
        self.assertEqual(format_percent(0.024), "2.40%")
        self.assertEqual(format_percent(0.155), "15.50%")
        self.assertEqual(format_percent(5.1), "5.10%")
        self.assertEqual(format_percent("2.4%"), "2.40%")
        self.assertEqual(format_percent(None), "N/A")
        self.assertEqual(format_percent("N/A"), "N/A")
        self.assertEqual(format_percent(0), "0.00%")
        self.assertEqual(format_percent("invalid"), "invalid")

    def test_template_tags_rendering(self):
        template_str = (
            "{% load research_tags %}"
            "{{ ticker|clean_ticker }} | "
            "{{ cap|format_currency }} | "
            "{{ cap|format_currency:False }} | "
            "{{ pe|format_ratio }} | "
            "{{ dy|format_percent }}"
        )
        template = Template(template_str)
        context = Context({
            "ticker": "BBCA.JK",
            "cap": 771917544337500,
            "pe": 23.4,
            "dy": 0.024,
        })
        rendered = template.render(context)
        self.assertEqual(
            rendered,
            "BBCA | Rp 771.92 T | Rp 771,917,544,337,500 | 23.40x | 2.40%",
        )

    def test_sparkline_points_filter(self):
        from research.templatetags.research_tags import sparkline_points
        prices = [
            {"date": "2026-09-01", "close": 100},
            {"date": "2026-09-02", "close": 150},
            {"date": "2026-09-03", "close": 200},
        ]
        points = sparkline_points(prices, "140,40")
        self.assertTrue(isinstance(points, str))
        self.assertTrue(len(points.split(" ")) == 3)
        self.assertTrue(points.startswith("4.0,"))

    def test_sparkline_points_invalid_input(self):
        from research.templatetags.research_tags import sparkline_points
        self.assertEqual(sparkline_points([]), "")
        self.assertEqual(sparkline_points([{"close": 100}]), "")
        self.assertEqual(sparkline_points("invalid"), "")

    def test_get_item_filter(self):
        from research.templatetags.research_tags import get_item
        data = {"name": "BBCA", "valuation": {"pe": 23.4}}
        self.assertEqual(get_item(data, "name"), "BBCA")
        self.assertEqual(get_item(data, "nonexistent"), None)
        self.assertEqual(get_item("string", "name"), "")
