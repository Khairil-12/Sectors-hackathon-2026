from __future__ import annotations

from typing import Any
from django import template
from research.utils import clean_symbol, format_currency, format_percent, format_ratio

register = template.Library()


@register.filter(name="format_currency")
def currency_filter(value: Any, short: bool = True) -> str:
    """Template filter to format amounts into readable Rupiah (e.g. Rp 771.92 T)."""
    return format_currency(value, short=short)


@register.filter(name="format_ratio")
def ratio_filter(value: Any, suffix: str = "x") -> str:
    """Template filter to format ratios (e.g. 23.40x)."""
    return format_ratio(value, suffix=suffix)


@register.filter(name="format_percent")
def percent_filter(value: Any) -> str:
    """Template filter to format percentage or decimal ratios (e.g. 2.40%)."""
    return format_percent(value)


@register.filter(name="clean_ticker")
def ticker_filter(value: Any) -> str:
    """Template filter to strip .JK suffix for clean ticker badges."""
    return clean_symbol(value)


@register.filter(name="sparkline_points")
def sparkline_points(series: Any, dimensions: str = "140,40") -> str:
    """
    Converts list of price dicts into SVG polyline points: 'x1,y1 x2,y2 ...'
    """
    if not isinstance(series, list) or len(series) < 2:
        return ""
    try:
        w_str, h_str = dimensions.split(",")
        width, height = float(w_str), float(h_str)
    except Exception:
        width, height = 140.0, 40.0

    closes = [float(s.get("close")) for s in series if isinstance(s, dict) and s.get("close") is not None]
    if len(closes) < 2:
        return ""

    min_v = min(closes)
    max_v = max(closes)
    span = max_v - min_v if max_v != min_v else 1.0
    n = len(closes)
    points = []
    for idx, val in enumerate(closes):
        x = round((idx / (n - 1)) * (width - 8) + 4, 1)
        y = round((height - 6) - ((val - min_v) / span) * (height - 12), 1)
        points.append(f"{x},{y}")
    return " ".join(points)


@register.filter(name="get_item")
def get_item(dictionary: Any, key: Any) -> Any:
    """Template filter to look up a key from a dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return ""
