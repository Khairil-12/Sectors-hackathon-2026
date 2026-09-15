from __future__ import annotations

import logging
import re
from datetime import date, timedelta
from typing import Any

from research.services import sectors_api
from research.services.groq_client import generate_copilot_report, parse_user_intent
from research.services.sectors_api import SectorsAPIError

logger = logging.getLogger(__name__)

SYMBOL_RE = re.compile(r"^[A-Z]{4}$")
SYMBOL_ENDPOINTS = {
    "company_report": lambda symbol, dates: sectors_api.get_company_report(symbol),
    "quarterly_financials": lambda symbol, dates: sectors_api.get_quarterly(symbol),
    "daily_transaction": lambda symbol, dates: sectors_api.get_daily(symbol, **dates),
    "broker_summary_top": lambda symbol, dates: sectors_api.get_broker_summary_top(symbol, **dates),
    "foreign_flow": lambda symbol, dates: sectors_api.get_foreign_flow(symbol, **dates),
    "news": lambda symbol, dates: sectors_api.get_news(symbols=symbol, **dates),
    "corporate_actions": lambda symbol, dates: sectors_api.get_corporate_actions(symbol),
}


def _safe_dates(intent: dict) -> dict[str, str]:
    end = date.today()
    start = end - timedelta(days=30)
    value = intent.get("date_range") or {}
    try:
        start = date.fromisoformat(value.get("start", ""))
        end = date.fromisoformat(value.get("end", ""))
    except (ValueError, TypeError):
        pass
    if start > end:
        start, end = end - timedelta(days=30), end
    if (end - start).days > 90:
        start = end - timedelta(days=90)
    return {"start": start.isoformat(), "end": end.isoformat()}


def _symbols(intent: dict) -> list[str]:
    values = []
    for value in intent.get("symbols", []):
        symbol = str(value).upper().strip().removesuffix(".JK")
        if not SYMBOL_RE.fullmatch(symbol):
            continue
        if symbol not in values:
            values.append(symbol)
    if not values:
        values = ["BBCA"]
    return values[:4]


def _error_payload(error: Exception) -> dict:
    if isinstance(error, SectorsAPIError):
        return {"error": error.code, "message": error.message}
    return {"error": "UNAVAILABLE", "message": "Requested data is unavailable."}


def run_analysis(user_prompt: str) -> dict[str, Any]:
    intent = parse_user_intent(user_prompt)
    dates = _safe_dates(intent)
    symbols = _symbols(intent)
    endpoints = set(intent.get("required_endpoints", []))
    if not endpoints:
        endpoints = {"company_report", "daily_transaction", "foreign_flow", "broker_summary_top"}

    context: dict[str, Any] = {"symbols": symbols, "dates": dates}

    for symbol in symbols:
        for endpoint in endpoints & SYMBOL_ENDPOINTS.keys():
            key = f"{symbol}_{endpoint}"
            try:
                context[key] = SYMBOL_ENDPOINTS[endpoint](symbol, dates)
            except SectorsAPIError as error:
                logger.warning("Error fetching %s for %s: %s", endpoint, symbol, error)
                context[key] = _error_payload(error)
            except Exception as error:
                logger.warning("Unexpected error fetching %s for %s: %s", endpoint, symbol, error)
                context[key] = _error_payload(error)

    if "sector_report" in endpoints:
        slug = intent.get("sector_slug") or "banks"
        try:
            context["sector_report"] = sectors_api.get_sector_report(slug)
        except Exception as error:
            context["sector_report"] = _error_payload(error)

    if "screener" in endpoints:
        try:
            context["screener"] = sectors_api.get_screener(q=user_prompt)
        except Exception as error:
            context["screener"] = _error_payload(error)

    report = generate_copilot_report(user_prompt, context)
    return {"intent": intent, "report": report, "raw_context": context}


def run_comparison(symbols: list[str]) -> list[dict[str, Any]]:
    """Gathers comparative financial metrics across multiple IDX stock symbols."""
    clean_symbols = []
    for s in symbols:
        sym = s.upper().strip().removesuffix(".JK")
        if SYMBOL_RE.fullmatch(sym) and sym not in clean_symbols:
            clean_symbols.append(sym)

    if not clean_symbols:
        clean_symbols = ["BBCA", "BMRI"]

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=30)).isoformat()
    results = []

    for sym in clean_symbols[:4]:
        item: dict[str, Any] = {
            "symbol": sym,
            "company_name": f"{sym} Tbk",
            "industry": "N/A",
            "sub_sector": "N/A",
            "market_cap": None,
            "pe_ratio": None,
            "pb_ratio": None,
            "dividend_yield": None,
            "roe": None,
            "net_foreign_30d": 0,
            "last_price": None,
            "price_change_pct": 0.0,
        }

        try:
            rep = sectors_api.get_company_report(sym)
            if isinstance(rep, dict):
                overview = rep.get("overview", {})
                valuation = rep.get("valuation", {})
                item["company_name"] = overview.get("company_name", item["company_name"])
                item["industry"] = overview.get("industry", "N/A")
                item["sub_sector"] = overview.get("sub_sector", "N/A")
                item["market_cap"] = overview.get("market_cap")
                item["pe_ratio"] = valuation.get("pe_ratio")
                item["pb_ratio"] = valuation.get("pb_ratio")
                item["dividend_yield"] = valuation.get("dividend_yield")
                item["roe"] = valuation.get("roe")
        except Exception as exc:
            logger.warning("Error fetching company report for comparison %s: %s", sym, exc)

        try:
            foreign = sectors_api.get_foreign_flow(sym, start_date, end_date)
            if isinstance(foreign, list):
                item["net_foreign_30d"] = sum(f.get("net_foreign", 0) for f in foreign if isinstance(f, dict))
        except Exception as exc:
            logger.warning("Error fetching foreign flow for %s: %s", sym, exc)

        try:
            daily = sectors_api.get_daily(sym, start_date, end_date)
            if isinstance(daily, list) and daily:
                latest = daily[0] if isinstance(daily[0], dict) else {}
                item["last_price"] = latest.get("close")
                if len(daily) > 1 and isinstance(daily[-1], dict):
                    old_price = daily[-1].get("close", 0)
                    new_price = latest.get("close", 0)
                    if old_price and new_price:
                        item["price_change_pct"] = round(((new_price - old_price) / old_price) * 100, 2)
        except Exception as exc:
            logger.warning("Error fetching daily prices for %s: %s", sym, exc)

        results.append(item)

    return results
