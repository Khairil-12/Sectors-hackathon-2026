from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache


@dataclass
class SectorsAPIError(Exception):
    code: str
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        return self.message


CACHE_TTLS = {
    "daily": 900,
    "company": 86400,
    "quarterly": 86400,
    "broker": 900,
    "news": 1800,
    "screener": 300,
    "reference": 86400,
}


def _cache_key(endpoint: str, params: dict[str, Any]) -> str:
    payload = repr((endpoint, sorted(params.items()))).encode()
    return f"sectors:{hashlib.sha256(payload).hexdigest()}"


def _get(endpoint: str, params: dict[str, Any] | None = None, ttl_key: str = "daily") -> dict | list:
    params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
    cache_key = _cache_key(endpoint, params)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        response = requests.get(
            f"{settings.SECTORS_BASE_URL}{endpoint}",
            headers={"Authorization": settings.SECTORS_API_KEY},
            params=params,
            timeout=15,
        )
    except requests.Timeout as exc:
        raise SectorsAPIError("UPSTREAM_TIMEOUT", "Sectors API timed out.") from exc
    except requests.RequestException as exc:
        raise SectorsAPIError("UPSTREAM_UNAVAILABLE", "Sectors API is unavailable.") from exc

    if response.status_code == 400:
        raise SectorsAPIError("BAD_REQUEST", "Sectors API rejected request parameters.", 400)
    if response.status_code in (401, 403):
        raise SectorsAPIError("AUTH_FAILED", "Sectors API authentication failed.", response.status_code)
    if response.status_code == 404:
        raise SectorsAPIError("NOT_FOUND", "Requested IDX data was not found.", 404)
    if response.status_code == 429:
        raise SectorsAPIError("RATE_LIMITED", "Sectors API rate limit reached. Try again shortly.", 429)
    if response.status_code >= 500:
        raise SectorsAPIError("UPSTREAM_ERROR", "Sectors API failed. Try again shortly.", response.status_code)

    try:
        response.raise_for_status()
        data = response.json()
    except ValueError as exc:
        raise SectorsAPIError("INVALID_RESPONSE", "Sectors API returned invalid JSON.") from exc
    except requests.RequestException as exc:
        raise SectorsAPIError("UPSTREAM_ERROR", "Sectors API request failed.", response.status_code) from exc

    cache.set(cache_key, data, CACHE_TTLS[ttl_key])
    return data


def get_company_report(symbol: str, sections: str = "overview,valuation,financials") -> dict:
    return _get(f"/v2/company/report/{symbol}/", {"sections": sections}, "company")


def get_quarterly(symbol: str, report_date: str | None = None) -> dict | list:
    return _get(f"/v2/financials/quarterly/{symbol}/", {"report_date": report_date}, "quarterly")


def get_daily(symbol: str, start: str, end: str) -> dict | list:
    return _get(f"/v2/daily/{symbol}/", {"start": start, "end": end}, "daily")


def get_broker_summary_top(symbol: str, start: str, end: str) -> dict:
    return _get(f"/v2/broker-summary/{symbol}/top/", {"start": start, "end": end}, "broker")


def get_foreign_flow(symbol: str, start: str, end: str) -> dict | list:
    return _get(f"/v2/foreign-flow/{symbol}/", {"start": start, "end": end}, "daily")


def get_news(symbols: str | None = None, start: str | None = None, end: str | None = None) -> dict | list:
    return _get("/v2/news/", {"extension": "idx", "symbols": symbols, "start": start, "end": end}, "news")


def get_corporate_actions(symbol: str) -> dict | list:
    return _get(f"/v2/company/corporate-actions/{symbol}/", {}, "company")


def get_screener(q: str | None = None, where: str | None = None, order_by: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    if q and (where or order_by):
        raise SectorsAPIError("BAD_REQUEST", "Use either natural-language or structured screening.")
    return _get("/v2/companies/", {"q": q, "where": where, "order_by": order_by, "limit": limit, "offset": offset}, "screener")


def get_sector_report(sub_sector: str, sections: str | None = None) -> dict:
    return _get(f"/v2/subsector/report/{sub_sector}/", {"sections": sections}, "company")


def get_free_float(**filters: str) -> dict | list:
    return _get("/v2/free-float/", filters, "reference")


def get_top_changes(**params: str) -> dict | list:
    return _get("/v2/companies/top-changes/", params, "daily")


def get_most_traded(**params: str) -> dict | list:
    return _get("/v2/most-traded/", params, "daily")


def get_filings(**params: str) -> dict | list:
    return _get("/v2/filings/", params, "news")


def get_suspensions(**params: str) -> dict | list:
    return _get("/v2/suspensions/", params, "news")


def get_brokers(**params: str) -> dict | list:
    return _get("/v2/brokers/", params, "reference")


def get_brokers_top(**params: str) -> dict | list:
    return _get("/v2/brokers/top/", params, "broker")


def get_reference_list(name: str) -> dict | list:
    if name not in {"industries", "subindustries", "subsectors", "tags"}:
        raise SectorsAPIError("BAD_REQUEST", "Unknown reference list.")
    return _get(f"/v2/{name}/", {}, "reference")
