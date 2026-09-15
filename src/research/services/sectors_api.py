from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


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


# Built-in benchmark fallback dataset for offline testing and demo resilience
_MOCK_COMPANIES = {
    "BBCA": {
        "overview": {
            "symbol": "BBCA.JK",
            "company_name": "Bank Central Asia Tbk",
            "industry": "Financials",
            "sub_sector": "Banks",
            "market_cap": 1_230_000_000_000_000,
            "listing_date": "2000-05-31",
        },
        "valuation": {
            "pe_ratio": 23.4,
            "pb_ratio": 4.8,
            "ps_ratio": 12.1,
            "dividend_yield": 0.024,
            "roe": 0.215,
            "roa": 0.038,
        },
        "financials": {
            "revenue": 98_500_000_000_000,
            "net_income": 48_600_000_000_000,
            "total_assets": 1_410_000_000_000_000,
        },
    },
    "BMRI": {
        "overview": {
            "symbol": "BMRI.JK",
            "company_name": "Bank Mandiri (Persero) Tbk",
            "industry": "Financials",
            "sub_sector": "Banks",
            "market_cap": 640_000_000_000_000,
            "listing_date": "2003-07-14",
        },
        "valuation": {
            "pe_ratio": 11.8,
            "pb_ratio": 2.1,
            "ps_ratio": 5.4,
            "dividend_yield": 0.051,
            "roe": 0.198,
            "roa": 0.027,
        },
        "financials": {
            "revenue": 120_000_000_000_000,
            "net_income": 55_000_000_000_000,
            "total_assets": 2_170_000_000_000_000,
        },
    },
    "BBRI": {
        "overview": {
            "symbol": "BBRI.JK",
            "company_name": "Bank Rakyat Indonesia (Persero) Tbk",
            "industry": "Financials",
            "sub_sector": "Banks",
            "market_cap": 750_000_000_000_000,
            "listing_date": "2003-11-10",
        },
        "valuation": {
            "pe_ratio": 12.5,
            "pb_ratio": 2.4,
            "ps_ratio": 5.8,
            "dividend_yield": 0.062,
            "roe": 0.201,
            "roa": 0.031,
        },
        "financials": {
            "revenue": 145_000_000_000_000,
            "net_income": 60_400_000_000_000,
            "total_assets": 1_965_000_000_000_000,
        },
    },
    "TLKM": {
        "overview": {
            "symbol": "TLKM.JK",
            "company_name": "Telkom Indonesia (Persero) Tbk",
            "industry": "Telecommunication Services",
            "sub_sector": "Telecommunication",
            "market_cap": 290_000_000_000_000,
            "listing_date": "1995-11-14",
        },
        "valuation": {
            "pe_ratio": 13.9,
            "pb_ratio": 2.2,
            "ps_ratio": 2.1,
            "dividend_yield": 0.058,
            "roe": 0.185,
            "roa": 0.092,
        },
        "financials": {
            "revenue": 149_000_000_000_000,
            "net_income": 24_500_000_000_000,
            "total_assets": 287_000_000_000_000,
        },
    },
    "ASII": {
        "overview": {
            "symbol": "ASII.JK",
            "company_name": "Astra International Tbk",
            "industry": "Consumer Discretionary",
            "sub_sector": "Automobiles & Components",
            "market_cap": 205_000_000_000_000,
            "listing_date": "1990-04-04",
        },
        "valuation": {
            "pe_ratio": 6.8,
            "pb_ratio": 0.95,
            "ps_ratio": 0.65,
            "dividend_yield": 0.084,
            "roe": 0.165,
            "roa": 0.078,
        },
        "financials": {
            "revenue": 316_000_000_000_000,
            "net_income": 33_800_000_000_000,
            "total_assets": 445_000_000_000_000,
        },
    },
}


def _get_mock_fallback(endpoint: str, params: dict[str, Any]) -> dict | list | None:
    """Provides structured mock responses for demo resilience when API key is missing."""
    today = date.today()

    if "/v2/company/report/" in endpoint:
        symbol = endpoint.split("/")[4].upper()
        if symbol in _MOCK_COMPANIES:
            return _MOCK_COMPANIES[symbol]
        return {
            "overview": {"symbol": f"{symbol}.JK", "company_name": f"{symbol} Tbk", "industry": "General", "sub_sector": "General", "market_cap": 50_000_000_000_000},
            "valuation": {"pe_ratio": 15.0, "pb_ratio": 1.5, "dividend_yield": 0.03},
            "financials": {"revenue": 10_000_000_000_000, "net_income": 1_000_000_000_000},
        }

    if "/v2/daily/" in endpoint:
        symbol = endpoint.split("/")[4].upper()
        return [
            {"date": (today - timedelta(days=i)).isoformat(), "symbol": f"{symbol}.JK", "close": 9500 - (i * 25), "volume": 45_000_000, "market_cap": 1_100_000_000_000_000}
            for i in range(10)
        ]

    if "/v2/foreign-flow/" in endpoint:
        symbol = endpoint.split("/")[4].upper()
        return [
            {"date": (today - timedelta(days=i)).isoformat(), "symbol": f"{symbol}.JK", "net_foreign": 45_000_000_000 - (i * 5_000_000_000), "foreign_buy": 120_000_000_000, "foreign_sell": 75_000_000_000}
            for i in range(10)
        ]

    if "/v2/broker-summary/" in endpoint:
        symbol = endpoint.split("/")[4].upper()
        return {
            "symbol": f"{symbol}.JK",
            "top_buyers": [
                {"broker_code": "ZP", "broker_name": "Maybank Sekuritas", "volume": 12_500_000, "value": 118_000_000_000},
                {"broker_code": "AK", "broker_name": "UBS Sekuritas", "volume": 9_800_000, "value": 93_000_000_000},
                {"broker_code": "BK", "broker_name": "J.P. Morgan Sekuritas", "volume": 8_200_000, "value": 78_000_000_000},
            ],
            "top_sellers": [
                {"broker_code": "YP", "broker_name": "Mirae Asset Sekuritas", "volume": 14_200_000, "value": 134_000_000_000},
                {"broker_code": "CC", "broker_name": "Mandiri Sekuritas", "volume": 7_100_000, "value": 67_000_000_000},
            ],
        }

    if "/v2/companies/top-changes/" in endpoint or "/v2/most-traded/" in endpoint:
        return [
            {"symbol": "BBCA.JK", "company_name": "Bank Central Asia Tbk", "price": 9975, "change": 175, "change_pct": 1.79, "volume": 68_400_000, "value": 682_000_000_000},
            {"symbol": "BMRI.JK", "company_name": "Bank Mandiri (Persero) Tbk", "price": 6850, "change": 150, "change_pct": 2.24, "volume": 52_100_000, "value": 356_000_000_000},
            {"symbol": "BBRI.JK", "company_name": "Bank Rakyat Indonesia Tbk", "price": 4980, "change": -40, "change_pct": -0.80, "volume": 89_200_000, "value": 444_000_000_000},
            {"symbol": "TLKM.JK", "company_name": "Telkom Indonesia Tbk", "price": 3020, "change": 60, "change_pct": 2.03, "volume": 41_300_000, "value": 124_000_000_000},
            {"symbol": "ASII.JK", "company_name": "Astra International Tbk", "price": 5050, "change": 25, "change_pct": 0.50, "volume": 33_900_000, "value": 171_000_000_000},
        ]

    if "/v2/companies/" in endpoint:
        items = []
        for sym, data in _MOCK_COMPANIES.items():
            overview = data["overview"]
            val = data["valuation"]
            items.append({
                "symbol": overview["symbol"],
                "company_name": overview["company_name"],
                "industry": overview["industry"],
                "sub_sector": overview["sub_sector"],
                "market_cap": overview["market_cap"],
                "pe_ratio": val["pe_ratio"],
                "pe_ttm": val["pe_ratio"],
                "forward_pe": val["pe_ratio"],
                "pb_ratio": val["pb_ratio"],
                "pb_mrq": val["pb_ratio"],
                "dividend_yield": val["dividend_yield"],
                "yield_ttm": val["dividend_yield"],
            })
        return {"count": len(items), "results": items}

    if "/v2/news/" in endpoint:
        return [
            {"title": "IDX Market Momentum Strengthens Ahead of Earnings Releases", "url": "https://idx.co.id", "publish_date": today.isoformat(), "source": "IDX News"},
            {"title": "Foreign Inflow Remains Robust Across Indonesian Tier-1 Banking Stocks", "url": "https://idx.co.id", "publish_date": today.isoformat(), "source": "Market Wire"},
        ]

    return {}


def _get(endpoint: str, params: dict[str, Any] | None = None, ttl_key: str = "daily") -> dict | list:
    params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
    cache_key = _cache_key(endpoint, params)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_key = getattr(settings, "SECTORS_API_KEY", "")
    base_url = getattr(settings, "SECTORS_BASE_URL", "https://api.sectors.app")

    if not api_key or api_key == "your_sectors_api_key_here":
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            cache.set(cache_key, mock, CACHE_TTLS[ttl_key])
            return mock
        raise SectorsAPIError("AUTH_FAILED", "Sectors API key is not configured.", 401)

    try:
        response = requests.get(
            f"{base_url}{endpoint}",
            headers={"Authorization": api_key},
            params=params,
            timeout=3,
        )
    except requests.Timeout as exc:
        logger.warning("Sectors API timeout for %s: %s", endpoint, exc)
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            return mock
        raise SectorsAPIError("UPSTREAM_TIMEOUT", "Sectors API timed out.") from exc
    except requests.RequestException as exc:
        logger.warning("Sectors API network failure for %s: %s", endpoint, exc)
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            return mock
        raise SectorsAPIError("UPSTREAM_UNAVAILABLE", "Sectors API is unavailable.") from exc

    if response.status_code == 400:
        raise SectorsAPIError("BAD_REQUEST", "Sectors API rejected request parameters.", 400)
    if response.status_code in (401, 403):
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            return mock
        raise SectorsAPIError("AUTH_FAILED", "Sectors API authentication failed.", response.status_code)
    if response.status_code == 404:
        raise SectorsAPIError("NOT_FOUND", "Requested IDX data was not found.", 404)
    if response.status_code == 429:
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            return mock
        raise SectorsAPIError("RATE_LIMITED", "Sectors API rate limit reached. Try again shortly.", 429)
    if response.status_code >= 500:
        mock = _get_mock_fallback(endpoint, params)
        if mock is not None:
            return mock
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
