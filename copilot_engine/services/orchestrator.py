from __future__ import annotations

import re
from datetime import date, timedelta

from copilot_engine.services import sectors_api
from copilot_engine.services.groq_client import generate_copilot_report, parse_user_intent
from copilot_engine.services.sectors_api import SectorsAPIError


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
    except ValueError:
        pass
    if start > end:
        raise ValueError("Date range is invalid.")
    if (end - start).days > 90:
        start = end - timedelta(days=90)
    return {"start": start.isoformat(), "end": end.isoformat()}


def _symbols(intent: dict) -> list[str]:
    values = []
    for value in intent.get("symbols", []):
        symbol = value.upper().removesuffix(".JK")
        if not SYMBOL_RE.fullmatch(symbol):
            raise ValueError("IDX symbols must contain exactly four letters.")
        if symbol not in values:
            values.append(symbol)
    return values


def _error_payload(error: Exception) -> dict:
    if isinstance(error, SectorsAPIError):
        return {"error": error.code, "message": error.message}
    return {"error": "UNAVAILABLE", "message": "Requested data is unavailable."}


def run_analysis(user_prompt: str) -> dict:
    intent = parse_user_intent(user_prompt)
    dates = _safe_dates(intent)
    symbols = _symbols(intent)
    endpoints = set(intent.get("required_endpoints", []))
    context: dict = {"symbols": {}, "global": {}}

    for symbol in symbols:
        symbol_context = context["symbols"].setdefault(symbol, {})
        for endpoint in endpoints & SYMBOL_ENDPOINTS.keys():
            try:
                symbol_context[endpoint] = SYMBOL_ENDPOINTS[endpoint](symbol, dates)
            except SectorsAPIError as error:
                symbol_context[endpoint] = _error_payload(error)

    if "sector_report" in endpoints:
        slug = intent.get("sector_slug")
        if slug:
            try:
                context["global"]["sector_report"] = sectors_api.get_sector_report(slug)
            except SectorsAPIError as error:
                context["global"]["sector_report"] = _error_payload(error)

    if "screener" in endpoints:
        try:
            context["global"]["screener"] = sectors_api.get_screener(q=user_prompt)
        except SectorsAPIError as error:
            context["global"]["screener"] = _error_payload(error)

    report = generate_copilot_report(user_prompt, context)
    return {"intent": intent, "report": report, "raw_context": context}
