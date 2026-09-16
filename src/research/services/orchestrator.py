from __future__ import annotations

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Any

from research.services import sectors_api
from research.services.groq_client import generate_copilot_report, parse_user_intent
from research.services.sectors_api import SectorsAPIError
from research.utils import clean_symbol, format_currency

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
    return values[:10]


def _error_payload(error: Exception) -> dict:
    if isinstance(error, SectorsAPIError):
        return {"error": error.code, "message": error.message}
    return {"error": "UNAVAILABLE", "message": "Requested data is unavailable."}


def detect_flow_divergence(context: dict[str, Any], symbols: list[str]) -> list[dict[str, Any]]:
    """
    Evaluates price momentum vs institutional foreign and broker flow to detect divergence signals.
    """
    signals = []
    for sym in symbols:
        daily_data = context.get(f"{sym}_daily_transaction", [])
        foreign_data = context.get(f"{sym}_foreign_flow", [])
        broker_data = context.get(f"{sym}_broker_summary_top", {})

        price_change_pct = 0.0
        if isinstance(daily_data, list) and len(daily_data) > 1:
            first = daily_data[0] if isinstance(daily_data[0], dict) else {}
            last = daily_data[-1] if isinstance(daily_data[-1], dict) else {}
            c_latest = first.get("close")
            c_old = last.get("close")
            if c_latest and c_old:
                price_change_pct = round(((c_latest - c_old) / c_old) * 100, 2)

        net_foreign_val = 0.0
        if isinstance(foreign_data, list):
            net_foreign_val = sum(
                float(f.get("net_foreign_inflow") or f.get("net_foreign") or 0)
                for f in foreign_data
                if isinstance(f, dict)
            )

        top_buyer_val = 0.0
        top_seller_val = 0.0
        if isinstance(broker_data, dict):
            buyers = broker_data.get("top_buyers") or broker_data.get("buyers") or []
            sellers = broker_data.get("top_sellers") or broker_data.get("sellers") or []
            if isinstance(buyers, list):
                top_buyer_val = sum(float(b.get("buy_value") or b.get("value") or 0) for b in buyers if isinstance(b, dict))
            if isinstance(sellers, list):
                top_seller_val = sum(float(s.get("sell_value") or s.get("value") or 0) for s in sellers if isinstance(s, dict))

        # Divergence rules
        # 1. Accumulation Divergence: Price down <= -1.5% while Foreign flow is strongly positive (> Rp 15B)
        if price_change_pct <= -1.5 and net_foreign_val > 15_000_000_000:
            signals.append({
                "symbol": sym,
                "type": "ACCUMULATION_DIVERGENCE",
                "badge_label": "Smart Money Accumulation Divergence",
                "badge_color": "emerald",
                "description": f"{sym} corrected {price_change_pct:.2f}% over the period, yet foreign institutions accumulated {format_currency(net_foreign_val, short=True)} in net buying.",
                "price_change_pct": price_change_pct,
                "net_foreign_idr": net_foreign_val,
            })
        # 2. Distribution Warning: Price gained >= +4.0% while Foreign flow is negative (< -Rp 15B)
        elif price_change_pct >= 4.0 and net_foreign_val < -15_000_000_000:
            signals.append({
                "symbol": sym,
                "type": "DISTRIBUTION_WARNING",
                "badge_label": "Institutional Distribution Alert",
                "badge_color": "red",
                "description": f"{sym} gained +{price_change_pct:.2f}%, but foreign institutions distributed {format_currency(abs(net_foreign_val), short=True)} in net selling.",
                "price_change_pct": price_change_pct,
                "net_foreign_idr": net_foreign_val,
            })
        # 3. Confirmed Momentum: Price up and Foreign flow strongly positive
        elif price_change_pct > 2.0 and net_foreign_val > 25_000_000_000:
            signals.append({
                "symbol": sym,
                "type": "CONFIRMED_MOMENTUM",
                "badge_label": "Confirmed Institutional Inflow",
                "badge_color": "blue",
                "description": f"{sym} price up +{price_change_pct:.2f}% supported by {format_currency(net_foreign_val, short=True)} net foreign inflow.",
                "price_change_pct": price_change_pct,
                "net_foreign_idr": net_foreign_val,
            })

    return signals


def _build_programmatic_citations(raw_context: dict[str, Any], symbols: list[str]) -> list[dict[str, Any]]:
    """Builds genuine, verified citation records from actual Sectors API calls."""
    today_str = date.today().isoformat()
    citations = []

    for sym in symbols:
        rep = raw_context.get(f"{sym}_company_report")
        if isinstance(rep, dict) and "error" not in rep:
            val = rep.get("valuation", {})
            pe = val.get("pe_ratio") or val.get("forward_pe") or "N/A"
            pb = val.get("pb_ratio") or "N/A"
            citations.append({
                "source_endpoint": f"/v2/company/report/{sym}/",
                "as_of_date": today_str,
                "key_datapoints": f"Verified Fundamentals for {sym}: P/E: {pe}, P/B: {pb}, Market Cap: {format_currency(rep.get('overview', {}).get('market_cap'), short=True)}",
            })

        foreign = raw_context.get(f"{sym}_foreign_flow")
        if isinstance(foreign, list) and foreign:
            net = sum(float(f.get("net_foreign_inflow") or f.get("net_foreign") or 0) for f in foreign if isinstance(f, dict))
            citations.append({
                "source_endpoint": f"/v2/foreign-flow/{sym}/",
                "as_of_date": today_str,
                "key_datapoints": f"30-Day Foreign Institutional Order Flow: {len(foreign)} trading sessions, Cumulative Net: {format_currency(net, short=True)}",
            })

        broker = raw_context.get(f"{sym}_broker_summary_top")
        if isinstance(broker, dict) and "error" not in broker:
            buyers = [b.get("broker_code") or b.get("broker") for b in (broker.get("top_buyers") or [])[:3] if isinstance(b, dict)]
            citations.append({
                "source_endpoint": f"/v2/broker-summary/{sym}/top/",
                "as_of_date": today_str,
                "key_datapoints": f"Top Institutional Accumulation Brokers: {', '.join(buyers) if buyers else 'N/A'}",
            })

        daily = raw_context.get(f"{sym}_daily_transaction")
        if isinstance(daily, list) and daily:
            citations.append({
                "source_endpoint": f"/v2/daily/{sym}/",
                "as_of_date": today_str,
                "key_datapoints": f"Historical OHLCV Series: {len(daily)} sessions tracked",
            })

    return citations


def _extract_charts_data(raw_context: dict[str, Any], symbols: list[str]) -> dict[str, Any]:
    """Prepares structured series data for zero-dependency template charts/sparklines."""
    charts: dict[str, Any] = {}
    for sym in symbols:
        daily = raw_context.get(f"{sym}_daily_transaction", [])
        foreign = raw_context.get(f"{sym}_foreign_flow", [])

        price_series = []
        if isinstance(daily, list):
            for d in reversed(daily[:20]):
                if isinstance(d, dict) and d.get("close") is not None:
                    price_series.append({
                        "date": str(d.get("date", ""))[-5:],
                        "close": float(d.get("close")),
                    })

        flow_series = []
        if isinstance(foreign, list):
            for f in reversed(foreign[:14]):
                if isinstance(f, dict):
                    val = float(f.get("net_foreign_inflow") or f.get("net_foreign") or 0)
                    flow_series.append({
                        "date": str(f.get("date", ""))[-5:],
                        "net_foreign": val,
                        "formatted": format_currency(val, short=True),
                        "is_positive": val >= 0,
                    })

        charts[sym] = {
            "prices": price_series,
            "flows": flow_series,
        }
    return charts


def run_analysis(user_prompt: str) -> dict[str, Any]:
    start_total_time = time.perf_counter()
    intent = parse_user_intent(user_prompt)

    # Short-circuit out-of-scope or non-financial inquiries
    if intent.get("analysis_type") == "out_of_scope" or intent.get("is_valid_query") is False:
        lang = intent.get("response_language", "en")
        is_id = lang == "id"
        return {
            "is_out_of_scope": True,
            "intent": intent,
            "message": intent.get("rejection_reason") or ("Pertanyaan di luar lingkup riset saham dan pasar modal IDX." if is_id else "Question is out of IDX stock research scope."),
            "suggestions": [
                "Analisis fundamental BBCA" if is_id else "Analyze BBCA fundamentals",
                "Bandingkan BMRI dan BBRI 30 hari" if is_id else "Compare BMRI and BBRI for 30 days",
                "Screening saham perbankan undervalue" if is_id else "Screen undervalued banking stocks",
                "Bagaimana foreign flow TLKM minggu ini?" if is_id else "How is TLKM's foreign flow this week?",
            ],
        }

    symbols = _symbols(intent)
    analysis_type = intent.get("analysis_type", "single_stock")

    if not symbols and analysis_type not in ("screener", "macro_sector"):
        lang = intent.get("response_language", "en")
        is_id = lang == "id"
        return {
            "is_out_of_scope": True,
            "intent": intent,
            "message": "Mohon sebutkan minimal satu kode saham IDX (contoh: BBCA, BMRI, TLKM, ASII)." if is_id else "Please mention at least one IDX stock ticker (e.g., BBCA, BMRI, TLKM, ASII).",
            "suggestions": [
                "Analisis fundamental BBCA" if is_id else "Analyze BBCA fundamentals",
                "Bandingkan BMRI dan BBRI 30 hari" if is_id else "Compare BMRI and BBRI for 30 days",
                "Screening saham perbankan undervalue" if is_id else "Screen undervalued banking stocks",
                "Bagaimana foreign flow TLKM minggu ini?" if is_id else "How is TLKM's foreign flow this week?",
            ],
        }

    dates = _safe_dates(intent)
    endpoints = set(intent.get("required_endpoints", []))
    if not endpoints:
        endpoints = {"company_report", "daily_transaction", "foreign_flow", "broker_summary_top"}

    context: dict[str, Any] = {"symbols": symbols, "dates": dates, "response_language": intent.get("response_language", "en")}
    endpoint_traces: list[dict[str, Any]] = []

    # Concurrent parallel execution of all symbol endpoints
    fetch_tasks = []
    for symbol in symbols:
        for endpoint in endpoints & SYMBOL_ENDPOINTS.keys():
            key = f"{symbol}_{endpoint}"
            fetch_tasks.append((key, endpoint, symbol, lambda sym=symbol, ep=endpoint: SYMBOL_ENDPOINTS[ep](sym, dates)))

    if "sector_report" in endpoints:
        slug = intent.get("sector_slug") or "banks"
        fetch_tasks.append(("sector_report", "sector_report", slug, lambda: sectors_api.get_sector_report(slug)))

    if "screener" in endpoints:
        fetch_tasks.append(("screener", "screener", "ALL", lambda: sectors_api.get_screener(q=user_prompt)))

    def _execute_task(task_tuple):
        k, ep, sym, fn = task_tuple
        t0 = time.perf_counter()
        try:
            val = fn()
            dur = round((time.perf_counter() - t0) * 1000, 1)
            return k, val, {"endpoint": ep, "symbol": sym, "status": "200 OK", "latency_ms": dur}
        except SectorsAPIError as err:
            dur = round((time.perf_counter() - t0) * 1000, 1)
            logger.warning("Error fetching %s for %s: %s", ep, sym, err)
            return k, _error_payload(err), {"endpoint": ep, "symbol": sym, "status": f"Error: {err.code}", "latency_ms": dur}
        except Exception as err:
            dur = round((time.perf_counter() - t0) * 1000, 1)
            logger.warning("Unexpected error fetching %s for %s: %s", ep, sym, err)
            return k, _error_payload(err), {"endpoint": ep, "symbol": sym, "status": "Unavailable", "latency_ms": dur}

    # Execute all tasks in parallel thread pool
    if fetch_tasks:
        with ThreadPoolExecutor(max_workers=min(len(fetch_tasks), 10)) as executor:
            futures = [executor.submit(_execute_task, task) for task in fetch_tasks]
            for future in as_completed(futures):
                k, res_data, trace = future.result()
                context[k] = res_data
                endpoint_traces.append(trace)

    # Detect flow divergence
    flow_divergences = detect_flow_divergence(context, symbols)

    # Generate LLM synthesis report
    report = generate_copilot_report(user_prompt, context)

    # Programmatic citation injection & agent trail
    programmatic_citations = _build_programmatic_citations(context, symbols)
    if programmatic_citations:
        report["data_citations"] = programmatic_citations

    total_latency_ms = round((time.perf_counter() - start_total_time) * 1000, 1)

    agent_execution_trail = {
        "user_goal": intent.get("user_goal_summary", "Equity Research Analysis"),
        "analysis_type": analysis_type,
        "symbols": symbols,
        "date_range": dates,
        "total_endpoints_queried": len(fetch_tasks),
        "endpoint_traces": endpoint_traces,
        "divergences_detected": len(flow_divergences),
        "total_latency_ms": total_latency_ms,
    }

    report["agent_execution_trail"] = agent_execution_trail
    report["flow_divergences"] = flow_divergences
    report["charts_data"] = _extract_charts_data(context, symbols)

    return {"intent": intent, "report": report, "raw_context": context}


def run_comparison(symbols: list[str]) -> list[dict[str, Any]]:
    """Gathers comparative financial metrics across multiple IDX stock symbols concurrently."""
    clean_symbols = []
    for s in symbols:
        sym = s.upper().strip().removesuffix(".JK")
        if SYMBOL_RE.fullmatch(sym) and sym not in clean_symbols:
            clean_symbols.append(sym)

    if not clean_symbols:
        clean_symbols = ["BBCA", "BMRI"]

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=30)).isoformat()

    def _fetch_symbol_data(sym: str) -> dict[str, Any]:
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
                dividend = rep.get("dividend", {})
                financials = rep.get("financials", {})
                item["company_name"] = rep.get("company_name") or overview.get("company_name", item["company_name"])
                item["industry"] = overview.get("industry", "N/A")
                item["sub_sector"] = overview.get("sub_sector", "N/A")
                item["market_cap"] = overview.get("market_cap")
                item["pe_ratio"] = valuation.get("forward_pe") or valuation.get("pe_ratio")
                history = valuation.get("historical_valuation", [])
                if isinstance(history, list) and history:
                    item["pb_ratio"] = history[0].get("pb")
                item["dividend_yield"] = dividend.get("yield_ttm") or valuation.get("dividend_yield")
                ratios = financials.get("historical_financial_ratio", [])
                if isinstance(ratios, list) and ratios:
                    item["roe"] = ratios[0].get("profitability", {}).get("roe")
                else:
                    item["roe"] = valuation.get("roe")
        except Exception as exc:
            logger.warning("Error fetching company report for comparison %s: %s", sym, exc)

        try:
            foreign = sectors_api.get_foreign_flow(sym, start_date, end_date)
            if isinstance(foreign, list):
                item["net_foreign_30d"] = sum(
                    float(f.get("net_foreign_inflow") or f.get("net_foreign") or 0)
                    for f in foreign
                    if isinstance(f, dict)
                )
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

        return item

    # Concurrently fetch comparison metrics for all symbols
    results_map: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(len(clean_symbols[:10]), 8)) as executor:
        future_to_sym = {executor.submit(_fetch_symbol_data, sym): sym for sym in clean_symbols[:10]}
        for future in as_completed(future_to_sym):
            sym = future_to_sym[future]
            try:
                results_map[sym] = future.result()
            except Exception as exc:
                logger.warning("Failed fetching comparison for %s: %s", sym, exc)

    # Preserve original order of symbols
    return [results_map[sym] for sym in clean_symbols[:10] if sym in results_map]

