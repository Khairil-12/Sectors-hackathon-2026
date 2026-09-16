from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _safe_num(value: Any) -> float | None:
    if value is None or value == "" or (isinstance(value, float) and value != value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    """Convert a value to int, returning None for None/empty/non-integer."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_str(value: Any) -> str | None:
    """Convert a value to str, returning None for None/empty."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _safe_list(value: Any) -> list[Any] | None:
    """Return list if value is a non-empty list, else None."""
    if isinstance(value, list) and len(value) > 0:
        return value
    return None


def _safe_dict(value: Any) -> dict[str, Any] | None:
    """Return dict if value is a non-empty dict, else None."""
    if isinstance(value, dict) and len(value) > 0:
        return value
    return None


def distill_company_report(data: Any) -> dict[str, Any]:
    """Extracts only critical valuation and financial indicators from company report in compact format."""
    if not isinstance(data, dict) or "error" in data:
        return data if isinstance(data, dict) else {}

    overview = data.get("overview", {}) if isinstance(data.get("overview"), dict) else {}
    valuation = data.get("valuation", {}) if isinstance(data.get("valuation"), dict) else {}
    financials = data.get("financials", {}) if isinstance(data.get("financials"), dict) else {}
    dividend = data.get("dividend", {}) if isinstance(data.get("dividend"), dict) else {}
    management = data.get("management", {}) if isinstance(data.get("management"), dict) else {}
    ownership = data.get("ownership", {}) if isinstance(data.get("ownership"), dict) else {}
    peers = data.get("peers", []) if isinstance(data.get("peers"), list) else []

    # --- overview fields ---
    company_name = overview.get("company_name")
    industry = overview.get("industry")
    sub_sector = overview.get("sub_sector")
    sector = overview.get("sector")
    listing_board = overview.get("listing_board")
    last_close_price = overview.get("last_close_price")
    latest_close_date = overview.get("latest_close_date")

    # --- valuation fields ---
    pe_ratio = valuation.get("pe_ratio")
    intrinsic_value = valuation.get("intrinsic_value")
    forward_pe = valuation.get("forward_pe")
    pb_ratio = valuation.get("pb_ratio")
    ps_ratio = valuation.get("ps_ratio")
    roe = valuation.get("roe")
    roa = valuation.get("roa")

    # --- Compact historical financials (latest 3 periods only) ---
    raw_hist_fin = financials.get("historical_financials", [])
    compact_hist_fin = []
    if isinstance(raw_hist_fin, list):
        for h in raw_hist_fin[:3]:
            if isinstance(h, dict):
                compact_hist_fin.append({
                    "year": _safe_int(h.get("year")),
                    "quarter": h.get("quarter") or h.get("period"),
                    "revenue": _safe_num(h.get("revenue") or h.get("total_revenue")),
                    "net_income": _safe_num(h.get("net_income") or h.get("profit")),
                    "eps": _safe_num(h.get("eps")),
                })

    # --- Compact historical dividends (latest 3 distributions only) ---
    raw_hist_div = dividend.get("historical_dividends", [])
    compact_hist_div = []
    if isinstance(raw_hist_div, list):
        for d in raw_hist_div[:3]:
            if isinstance(d, dict):
                compact_hist_div.append({
                    "year": _safe_int(d.get("year")),
                    "dps": _safe_num(d.get("dps") or d.get("amount")),
                    "yield": _safe_num(d.get("yield") or d.get("dividend_yield")),
                })

    # --- Compact historical valuation (latest 3 entries only) ---
    raw_hist_val = valuation.get("historical_valuation", [])
    compact_hist_val = []
    if isinstance(raw_hist_val, list):
        for v in raw_hist_val[:3]:
            if isinstance(v, dict):
                compact_hist_val.append({
                    "year": _safe_int(v.get("year")),
                    "pe": _safe_num(v.get("pe_ratio") or v.get("pe")),
                    "pb": _safe_num(v.get("pb_ratio") or v.get("pb")),
                })

    # --- Compact major shareholders (top 3 only) ---
    raw_holders = ownership.get("major_shareholders", [])
    compact_holders = []
    if isinstance(raw_holders, list):
        for s in raw_holders[:3]:
            if isinstance(s, dict):
                compact_holders.append({
                    "name": s.get("name") or s.get("shareholder_name"),
                    "pct": _safe_num(s.get("percentage") or s.get("pct")),
                })

    # --- Compact key executives (top 3 only) ---
    raw_execs = management.get("key_executives", [])
    compact_execs = []
    if isinstance(raw_execs, list):
        for ex in raw_execs[:3]:
            if isinstance(ex, dict):
                compact_execs.append({
                    "name": ex.get("name") or ex.get("executive_name"),
                    "title": ex.get("title") or ex.get("position"),
                })

    # --- Compact peers benchmarks (top 3 only) ---
    compact_peers = []
    if isinstance(peers, list):
        for p in peers[:3]:
            if isinstance(p, dict):
                compact_peers.append({
                    "symbol": p.get("symbol"),
                    "pe": _safe_num(p.get("pe_ratio")),
                    "pb": _safe_num(p.get("pb_ratio")),
                })

    return {
        "symbol": overview.get("symbol"),
        "company_name": company_name,
        "name": company_name,
        "industry": industry,
        "sub_sector": sub_sector,
        "sector": sector,
        "listing_board": listing_board,
        "last_close_price": _safe_num(last_close_price),
        "latest_close_date": _safe_str(latest_close_date),
        # --- valuation ---
        "pe_ratio": _safe_num(pe_ratio),
        "pb_ratio": _safe_num(pb_ratio),
        "ps_ratio": _safe_num(ps_ratio),
        "dividend_yield": _safe_num(dividend.get("yield_ttm") or valuation.get("dividend_yield")),
        "roe": _safe_num(roe),
        "roa": _safe_num(roa),
        "intrinsic_value": _safe_num(intrinsic_value),
        "forward_pe": _safe_num(forward_pe),
        "historical_valuation_recent": compact_hist_val,
        # --- financials ---
        "eps": _safe_num(financials.get("eps")),
        "revenue": _safe_num(financials.get("revenue")),
        "net_income": _safe_num(financials.get("net_income")),
        "total_assets": _safe_num(financials.get("total_assets")),
        "historical_financials_recent": compact_hist_fin,
        # --- dividend ---
        "yield_ttm": _safe_num(dividend.get("yield_ttm")),
        "dividend_ttm": _safe_int(dividend.get("dividend_ttm")),
        "payout_ratio": _safe_num(dividend.get("payout_ratio")),
        "historical_dividends_recent": compact_hist_div,
        # --- governance & peers ---
        "major_shareholders": compact_holders,
        "key_executives": compact_execs,
        "peer_benchmarks": compact_peers,
    }


def distill_daily_transactions(data: Any) -> dict[str, Any]:
    """Condenses multi-day daily OHLCV rows into high-level statistical summary."""
    if not isinstance(data, list) or not data:
        return data if isinstance(data, dict) else {"summary": "No transaction data available"}

    valid_records = [r for r in data if isinstance(r, dict) and "close" in r]
    if not valid_records:
        return {"summary": "No valid transaction records"}

    closes = [_safe_num(r.get("close")) for r in valid_records if _safe_num(r.get("close")) is not None]
    volumes = [_safe_num(r.get("volume")) for r in valid_records if _safe_num(r.get("volume")) is not None]

    if not closes:
        return {"summary": "No valid transaction records"}

    latest_close = closes[0]
    start_close = closes[-1]
    change_pct = None
    if latest_close is not None and start_close is not None and start_close != 0:
        change_pct = round(((latest_close - start_close) / start_close) * 100, 2)

    return {
        "record_count": len(valid_records),
        "latest_close": latest_close,
        "period_start_close": start_close,
        "period_change_pct": change_pct,
        "period_high_close": _safe_num(max(closes)) if closes else None,
        "period_low_close": _safe_num(min(closes)) if closes else None,
        "avg_daily_volume": _safe_num(sum(volumes) / len(volumes)) if volumes else None,
        "recent_5_days_close": closes[:5],
    }


def distill_foreign_flow(data: Any) -> dict[str, Any]:
    """Summarizes foreign flow series into net totals, 7-day trend, and buy/sell days."""
    if not isinstance(data, list) or not data:
        return data if isinstance(data, dict) else {"summary": "No foreign flow data"}

    # The API returns list of dicts with keys like: date, symbol, net_foreign_inflow, buy_buy_..., sell_...
    # Use .get() with .get() to safely extract; fall back to generic keys if needed.
    valid = []
    for r in data:
        if isinstance(r, dict):
            # Try net_foreign_inflow first, then fall back to net_foreign
            nf = r.get("net_foreign_inflow") if r.get("net_foreign_inflow") is not None else r.get("net_foreign")
            if nf is not None:
                valid.append(r)

    if not valid:
        return {"summary": "No valid foreign flow records"}

    flows = [_safe_num(r.get("net_foreign_inflow") if r.get("net_foreign_inflow") is not None else r.get("net_foreign")) for r in valid]
    total_net = _safe_num(sum(flows))
    recent_7d_net = _safe_num(sum(flows[:7])) if len(flows) >= 7 else None
    inflow_days = sum(1 for f in flows if _safe_num(f) is not None and _safe_num(f) > 0)
    outflow_days = sum(1 for f in flows if _safe_num(f) is not None and _safe_num(f) < 0)

    largest_inflow = _safe_num(max(flows)) if flows else None
    largest_outflow = _safe_num(min(flows)) if flows else None

    return {
        "period_total_net_foreign_idr": total_net,
        "recent_7d_net_foreign_idr": recent_7d_net,
        "inflow_days": inflow_days,
        "outflow_days": outflow_days,
        "largest_single_inflow_idr": largest_inflow,
        "largest_single_outflow_idr": largest_outflow,
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
            "year": _safe_int(item.get("year")),
            "revenue": _safe_num(item.get("revenue") or item.get("total_revenue")),
            "net_income": _safe_num(item.get("net_income") or item.get("profit")),
            "revenue_growth_yoy": _safe_num(item.get("revenue_growth_yoy") or item.get("revenue_growth")),
            "net_income_growth_yoy": _safe_num(item.get("net_income_growth_yoy") or item.get("profit_growth")),
            "operating_margin": _safe_num(item.get("operating_margin")),
        })
    return distilled if distilled else {"summary": "Quarterly data unavailable"}


def distill_broker_summary(data: Any) -> dict[str, Any]:
    """Distills top buyer and seller broker transactions."""
    if not isinstance(data, (dict, list)) or "error" in (data if isinstance(data, dict) else {}):
        return data if isinstance(data, dict) else {}

    buyers: list[dict[str, Any]] = []
    sellers: list[dict[str, Any]] = []

    if isinstance(data, dict):
        # API may use top_buyers/buyers or top_sellers/sellers; also top_buyer_amount/seller_amount
        top_buyers = data.get("top_buyers", data.get("buyers", []))
        top_sellers = data.get("top_sellers", data.get("sellers", []))

        if isinstance(top_buyers, list):
            for b in top_buyers[:3]:
                if isinstance(b, dict):
                    # API may use broker_code, broker, buy_value, value, net_idr, etc.
                    buyers.append({
                        "broker": b.get("broker_code") or b.get("broker"),
                        "buy_val": _safe_num(b.get("buy_value") or b.get("value")),
                    })

        if isinstance(top_sellers, list):
            for s in top_sellers[:3]:
                if isinstance(s, dict):
                    sellers.append({
                        "broker": s.get("broker_code") or s.get("broker"),
                        "sell_val": _safe_num(s.get("sell_value") or s.get("value")),
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
                    "pe": _safe_num(item.get("pe_ratio")),
                    "pb": _safe_num(item.get("pb_ratio")),
                    "market_cap": _safe_num(item.get("market_cap")),
                }
                for item in value[:8]
                if isinstance(item, dict)
            ]
        elif key == "sector_report" and isinstance(value, dict):
            compact_context["sector_report"] = {
                "sector": _safe_str(value.get("sector_name") or value.get("sector")),
                "top_companies": [
                    _safe_str(c.get("symbol")) for c in value.get("top_companies", [])[:5] if isinstance(c, dict)
                ] if isinstance(value.get("top_companies"), list) else [],
                "perf_summary": _safe_str(value.get("performance_summary") or value.get("summary")),
            }
        else:
            compact_context[key] = value

    return compact_context