from __future__ import annotations

from typing import Any


def clean_symbol(symbol: Any) -> str:
    """Strip trailing exchange suffixes (e.g. .JK) and whitespace."""
    if not symbol:
        return ""
    sym = str(symbol).strip().upper()
    if sym.endswith(".JK"):
        return sym[:-3]
    return sym


def format_currency(
    value: Any,
    short: bool = True,
    prefix: str = "Rp ",
    decimals: int = 2,
) -> str:
    """
    Format Indonesian Rupiah (or numeric amounts) into readable financial strings.

    Examples:
        format_currency(771917544337500) -> 'Rp 771.92 T'
        format_currency(450500000000) -> 'Rp 450.50 B'
        format_currency(12300000) -> 'Rp 12.30 M'
        format_currency(9500) -> 'Rp 9,500'
        format_currency(771917544337500, short=False) -> 'Rp 771,917,544,337,500'
        format_currency(None) -> 'N/A'
    """
    if value is None or value == "" or value == "N/A":
        return "N/A"

    try:
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("Rp", "").replace("IDR", "").strip()
            num = float(cleaned)
        else:
            num = float(value)
    except (ValueError, TypeError):
        return str(value)

    is_negative = num < 0
    abs_num = abs(num)
    sign = "-" if is_negative else ""

    if not short:
        # Full exact number with comma grouping
        formatted = f"{abs_num:,.0f}" if abs_num.is_integer() else f"{abs_num:,.{decimals}f}"
        return f"{sign}{prefix}{formatted}"

    # Short format with financial suffixes (T = Triliun, B = Miliar/Billion, M = Juta/Million, K = Ribu)
    if abs_num >= 1_000_000_000_000:
        val_str = f"{abs_num / 1_000_000_000_000:.{decimals}f}"
        return f"{sign}{prefix}{val_str} T"
    if abs_num >= 1_000_000_000:
        val_str = f"{abs_num / 1_000_000_000:.{decimals}f}"
        return f"{sign}{prefix}{val_str} B"
    if abs_num >= 1_000_000:
        val_str = f"{abs_num / 1_000_000:.{decimals}f}"
        return f"{sign}{prefix}{val_str} M"
    if abs_num >= 1_000:
        formatted = f"{abs_num:,.0f}" if abs_num.is_integer() else f"{abs_num:,.{decimals}f}"
        return f"{sign}{prefix}{formatted}"

    formatted = f"{abs_num:,.0f}" if abs_num.is_integer() else f"{abs_num:,.{decimals}f}"
    return f"{sign}{prefix}{formatted}"


def format_ratio(value: Any, suffix: str = "x", decimals: int = 2) -> str:
    """
    Format valuation multiples like P/E, P/B, P/S (e.g. 23.40x).
    """
    if value is None or value == "" or value == "N/A":
        return "N/A"

    try:
        if isinstance(value, str):
            cleaned = value.replace(suffix, "").replace(",", "").strip()
            num = float(cleaned)
        else:
            num = float(value)
        return f"{num:.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value: Any, decimals: int = 2) -> str:
    """
    Format decimal or percentage values (e.g. 0.024 -> 2.40%, 5.1 -> 5.10%).
    """
    if value is None or value == "" or value == "N/A":
        return "N/A"

    try:
        if isinstance(value, str):
            cleaned = value.replace("%", "").replace(",", "").strip()
            num = float(cleaned)
        else:
            num = float(value)

        # If value is fractional (e.g. 0.024 for 2.4%), multiply by 100
        # If absolute value is between 0 and 1.0 (non-zero), treat as decimal fraction
        if 0 < abs(num) <= 1.0:
            pct = num * 100.0
        else:
            pct = num

        return f"{pct:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)
