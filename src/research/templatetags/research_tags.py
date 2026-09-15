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
