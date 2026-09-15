from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def distill_company_report(data: Any) -> dict[str, Any]:
    """Extracts only critical valuation and financial indicators from company report."""
    if not isinstance(data, dict) or "error" in data:
        return data if isinstance(data, dict) else {}

    overview = data.get("overview", {}) if isinstance(data.get("overview"), dict) else {}
    valuation = data.get("valuation", {}) if isinstance(data.get("valuation"), dict) else {}
    financials = data.get("financials", {}) if isinstance(data.get("financials"), dict) else {}

    return {
        "symbol": overview.get("symbol"),
        "name": overview.get("company_name"),
        "sector": overview.get("industry") or overview.get("sector"),
        "sub_sector": overview.get("sub_sector"),
        "market_cap": overview.get("market_cap"),
        "pe_ratio": valuation.get("pe_ratio"),
        "pb_ratio": valuation.get("pb_ratio"),
        "ps_ratio": valuation.get("ps_ratio"),
        "dividend_yield": valuation.get("dividend_yield"),
        "roe": valuation.get("roe"),
        "roa": valuation.get("roa"),
        "revenue": financials.get("revenue"),
        "net_income": financials.get("net_income"),
        "total_assets": financials.get("total_assets"),
    }


def distill_daily_transactions(data: Any) -> dict[str, Any]:
    """Condenses multi-day daily OHLCV rows into high-level statistical summary."""
    if not isinstance(data, list) or not data:
        return data if isinstance(data, dict) else {"summary": "No transaction data available"}

    valid_records = [r for r in data if isinstance(r, dict) and "close" in r]
    if not valid_records:
        return {"summary": "No valid transaction records"}

    closes = [r["close"] for r in valid_records if r.get("close") is not None]
    volumes = [r.get("volume", 0) for r in valid_records if r.get("volume") is not None]

    latest_close = closes[0] if closes else None
    start_close = closes[-1] if closes else None
    change_pct = None
    if latest_close is not None and start_close and start_close > 0:
        change_pct = round(((latest_close - start_close) / start_close) * 100, 2)

    return {
        "record_count": len(valid_records),
        "latest_close": latest_close,
        "period_start_close": start_close,
        "period_change_pct": change_pct,
        "period_high_close": max(closes) if closes else None,
        "period_low_close": min(closes) if closes else None,
        "avg_daily_volume": round(sum(volumes) / len(volumes)) if volumes else None,
        "recent_5_days_close": closes[:5],
    }


def distill_foreign_flow(data: Any) -> dict[str, Any]:
    """Summarizes foreign flow series into net totals, 7-day trend, and buy/sell days."""
    if not isinstance(data, list) or not data:
        return data if isinstance(data, dict) else {"summary": "No foreign flow data"}

    valid = [r for r in data if isinstance(r, dict) and "net_foreign" in r]
    if not valid:
        return {"summary": "No valid foreign flow records"}

    flows = [r.get("net_foreign", 0) for r in valid]
    total_net = sum(flows)
    recent_7d_net = sum(flows[:7])
    inflow_days = sum(1 for f in flows if f > 0)
    outflow_days = sum(1 for f in flows if f < 0)

    return {
        "period_total_net_foreign_idr": total_net,
        "recent_7d_net_foreign_idr": recent_7d_net,
        "inflow_days": inflow_days,
        "outflow_days": outflow_days,
        "largest_single_inflow_idr": max(flows) if flows else 0,
        "largest_single_outflow_idr": min(flows) if flows else 0,
    }


def distill_quarterly(data: Any) -> list[dict[str, Any]] | dict[str, Any]:
    """Extracts top 4 recent quarters with key growth and margin metrics."""
    if isinstance(data, dict) and "error" in data:
        return data

    items = data if isinstance(data, list) else [data] if isinstance(data, dict) else []
    distilled = []
    for item in items[:4]:
        if not isinstance(item, dict):
            continue
        distilled.append({
            "quarter": item.get("quarter") or item.get("period"),
            "year": item.get("year"),
            "revenue": item.get("revenue") or item.get("total_revenue"),
            "net_income": item.get("net_income") or item.get("profit"),
            "revenue_growth_yoy": item.get("revenue_growth_yoy") or item.get("revenue_growth"),
            "net_income_growth_yoy": item.get("net_income_growth_yoy") or item.get("profit_growth"),
            "operating_margin": item.get("operating_margin"),
        })
    return distilled if distilled else {"summary": "Quarterly data unavailable"}


def distill_broker_summary(data: Any) -> dict[str, Any]:
    """Distills top buyer and seller broker transactions."""
    if not isinstance(data, (dict, list)) or "error" in (data if isinstance(data, dict) else {}):
        return data if isinstance(data, dict) else {}

    buyers: list[dict[str, Any]] = []
    sellers: list[dict[str, Any]] = []

    if isinstance(data, dict):
        top_buyers = data.get("top_buyers", data.get("buyers", []))
        top_sellers = data.get("top_sellers", data.get("sellers", []))
        if isinstance(top_buyers, list):
            for b in top_buyers[:3]:
                if isinstance(b, dict):
                    buyers.append({
                        "broker": b.get("broker_code") or b.get("broker"),
                        "buy_val": b.get("buy_value") or b.get("value"),
                    })
        if isinstance(top_sellers, list):
            for s in top_sellers[:3]:
                if isinstance(s, dict):
                    sellers.append({
                        "broker": s.get("broker_code") or s.get("broker"),
                        "sell_val": s.get("sell_value") or s.get("value"),
                    })

    return {
        "top_buyers": buyers,
        "top_sellers": sellers,
    }


def distill_news(data: Any) -> list[dict[str, Any]] | dict[str, Any]:
    """Filters news articles to top 3 headlines and dates."""
    if not isinstance(data, list):
        return data if isinstance(data, dict) else []

    articles = []
    for item in data[:3]:
        if isinstance(item, dict):
            articles.append({
                "date": str(item.get("published_at") or item.get("date", ""))[:10],
                "title": str(item.get("title", ""))[:100],
            })
    return articles


def distill_context(raw_context: dict[str, Any]) -> dict[str, Any]:
    """Transforms raw multi-endpoint context into a compact, token-efficient payload for LLMs."""
    symbols = raw_context.get("symbols", [])
    dates = raw_context.get("dates", {})

    compact_context: dict[str, Any] = {
        "symbols": symbols,
        "dates": dates,
    }

    for key, value in raw_context.items():
        if key in ("symbols", "dates"):
            continue

        if key.endswith("_company_report"):
            compact_context[key] = distill_company_report(value)
        elif key.endswith("_daily_transaction"):
            compact_context[key] = distill_daily_transactions(value)
        elif key.endswith("_foreign_flow"):
            compact_context[key] = distill_foreign_flow(value)
        elif key.endswith("_quarterly_financials"):
            compact_context[key] = distill_quarterly(value)
        elif key.endswith("_broker_summary_top"):
            compact_context[key] = distill_broker_summary(value)
        elif key.endswith("_news"):
            compact_context[key] = distill_news(value)
        elif key == "screener" and isinstance(value, list):
            compact_context["screener"] = [
                {
                    "symbol": item.get("symbol"),
                    "name": item.get("company_name"),
                    "pe": item.get("pe_ratio"),
                    "pb": item.get("pb_ratio"),
                    "market_cap": item.get("market_cap"),
                }
                for item in value[:8]
                if isinstance(item, dict)
            ]
        elif key == "sector_report" and isinstance(value, dict):
            compact_context["sector_report"] = {
                "sector": value.get("sector_name") or value.get("sector"),
                "top_companies": [
                    c.get("symbol") for c in value.get("top_companies", [])[:5] if isinstance(c, dict)
                ] if isinstance(value.get("top_companies"), list) else [],
                "perf_summary": value.get("performance_summary") or value.get("summary"),
            }
        else:
            # Fallback for simple scalar or already small items
            compact_context[key] = value

    return compact_context
