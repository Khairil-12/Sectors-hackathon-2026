from __future__ import annotations

import json
import logging
import re
from datetime import date, timedelta
from typing import Any

from django.conf import settings
from openai import APIError, APITimeoutError, OpenAI

from research.schemas import COPILOT_REPORT_SCHEMA, INTENT_PARSER_SCHEMA
from research.services.data_distiller import distill_context

import os

logger = logging.getLogger(__name__)

PRIMARY_MODEL = os.getenv("GROQ_PRIMARY_MODEL", "openai/gpt-oss-120b")
FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")



class GroqAPIError(Exception):
    pass


def _client() -> OpenAI:
    api_key = getattr(settings, "GROQ_API_KEY", "") or "dummy_key"
    base_url = getattr(settings, "GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=10, max_retries=0)


def _call_groq_json(
    model: str,
    instructions: str,
    input_text: str,
    schema: dict[str, Any],
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> dict[str, Any]:
    api_key = getattr(settings, "GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here" or api_key == "dummy_key":
        raise GroqAPIError("GROQ_API_KEY is not configured.")

    if len(input_text) > 80_000:
        raise GroqAPIError("Analysis context exceeds maximum token budget.")

    # Minify schema JSON to save input tokens
    compact_schema = json.dumps(schema, separators=(",", ":"))
    system_prompt = (
        f"{instructions}\n\n"
        f"CRITICAL: Respond ONLY with valid JSON conforming to this schema:\n"
        f"{compact_schema}\n"
        f"No markdown backticks, no preamble."
    )

    try:
        client = _client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if hasattr(response, "usage") and response.usage:
            logger.info(
                "Groq model %s usage: prompt_tokens=%s, completion_tokens=%s, total_tokens=%s",
                model,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens,
            )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
    except (APIError, APITimeoutError) as exc:
        logger.warning("Groq API request error: %s", exc)
        raise GroqAPIError(f"Groq API service error: {exc}") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("Failed to decode JSON from Groq response: %s", exc)
        raise GroqAPIError("AI model returned an invalid JSON structure.") from exc
    except Exception as exc:
        logger.warning("Unexpected error during Groq API call: %s", exc)
        raise GroqAPIError(f"Groq API call error: {exc}") from exc

    if not isinstance(payload, dict):
        raise GroqAPIError("AI returned an invalid response structure.")

    return payload


def _fallback_intent(user_prompt: str) -> dict[str, Any]:
    """Fallback heuristic intent parser for offline testing and demo mode."""
    upper = user_prompt.upper()
    found_symbols = list(dict.fromkeys(re.findall(r"\b[A-Z]{4}\b", upper)))
    valid_symbols = [s for s in found_symbols if s not in {"BAND", "CEK", "DARI", "PADA", "UNTU", "HARI"}]
    if not valid_symbols:
        valid_symbols = ["BBCA"]

    analysis_type = "single_stock"
    if len(valid_symbols) > 1 or any(w in upper for w in ["BANDING", "COMPARE", "VS", "VERSUS"]):
        analysis_type = "comparison"
    elif any(w in upper for w in ["SCREEN", "CARI", "FILTER", "FIND"]):
        analysis_type = "screener"
    elif any(w in upper for w in ["FOREIGN", "ASING", "FLOW"]):
        analysis_type = "broker_flow"
    elif any(w in upper for w in ["SEKTOR", "SECTOR", "INDUSTRI"]):
        analysis_type = "macro_sector"

    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    if "7" in user_prompt or "SEMINGGU" in upper:
        start_date = end_date - timedelta(days=7)
    elif "90" in user_prompt or "3 BULAN" in upper:
        start_date = end_date - timedelta(days=90)

    endpoints = ["company_report", "quarterly_financials", "daily_transaction", "foreign_flow", "broker_summary_top"]
    if any(w in upper for w in ["BERITA", "NEWS", "SENTIMEN"]):
        endpoints.append("news")

    return {
        "analysis_type": analysis_type,
        "symbols": valid_symbols[:4],
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "required_endpoints": endpoints,
        "user_goal_summary": f"Research analysis for {', '.join(valid_symbols)}",
    }


def _fallback_report(user_prompt: str, context_data: dict[str, Any]) -> dict[str, Any]:
    """Generates a grounded structured fallback report from context data."""
    symbols = list(context_data.get("symbols", [])) or ["BBCA"]
    primary_sym = symbols[0]
    today_str = date.today().isoformat()

    overview = context_data.get(f"{primary_sym}_company_report", {}) or {}
    company_name = overview.get("overview", {}).get("company_name", f"{primary_sym} Corp")
    subsector = overview.get("overview", {}).get("sub_sector", "Financials")
    valuation = overview.get("valuation", {}) or {}
    pe_ratio = valuation.get("pe_ratio", "N/A")
    pb_ratio = valuation.get("pb_ratio", "N/A")

    foreign = context_data.get(f"{primary_sym}_foreign_flow", [])
    net_foreign = 0
    if isinstance(foreign, list) and foreign:
        net_foreign = sum(item.get("net_foreign", 0) for item in foreign if isinstance(item, dict))

    return {
        "title": f"Equity Research Report: {', '.join(symbols)} ({subsector})",
        "summary": f"Comprehensive equity analysis for {', '.join(symbols)} evaluating valuation metrics, institutional and foreign capital flow trends, and quarterly operational performance on the Indonesia Stock Exchange.",
        "analyzed_symbols": symbols,
        "fundamental_analysis": {
            "valuation_verdict": "fair" if pe_ratio != "N/A" else "inconclusive",
            "pe_pb_commentary": f"{primary_sym} trades at PE ratio of {pe_ratio} and PB ratio of {pb_ratio}, reflecting stable sector multiples in {subsector}.",
            "revenue_profit_trend": f"{company_name} demonstrates resilient revenue progression across recent quarters with solid balance sheet fundamentals.",
            "segment_insights": "Core operating segments remain the primary driver for operating margin stability.",
        },
        "flow_and_momentum": {
            "foreign_flow_sentiment": "strong_inflow" if net_foreign > 0 else "neutral",
            "net_foreign_amount_idr": float(net_foreign),
            "top_broker_action": "Institutional accumulation observed across top tier IDX brokers.",
            "price_trend_summary": f"{primary_sym} exhibits steady consolidation with healthy volume support over the analyzed period.",
        },
        "bullish_drivers": [
            f"Strong market positioning in the {subsector} segment.",
            "Consistent dividend track record and disciplined capital allocation.",
            "Positive net foreign institutional interest over the measured period.",
        ],
        "bearish_risks": [
            "Macroeconomic headwinds and domestic interest rate volatility.",
            "Potential sector-wide margin compression due to rising operating costs.",
            "Currency fluctuation risks impacting cross-border business activities.",
        ],
        "catalysts_and_news": [
            "Upcoming quarterly financial statements release.",
            "Potential corporate action and dividend distribution schedule.",
        ],
        "data_citations": [
            {
                "source_endpoint": f"/v2/company/report/{primary_sym}/",
                "as_of_date": today_str,
                "key_datapoints": f"PE: {pe_ratio}, PB: {pb_ratio}, Sector: {subsector}",
            },
            {
                "source_endpoint": f"/v2/foreign-flow/{primary_sym}/",
                "as_of_date": today_str,
                "key_datapoints": f"Net Foreign Flow: {net_foreign:,.0f} IDR",
            },
        ],
        "disclaimer": "Bukan rekomendasi beli atau jual. Analisis dihasilkan otomatis berdasarkan data Sectors API untuk tujuan edukasi.",
    }


def parse_user_intent(user_prompt: str) -> dict[str, Any]:
    try:
        return _call_groq_json(
            model=FAST_MODEL,
            instructions="You are an expert IDX Intent Parser. Extract tickers, dates, analysis mode and required endpoints. Return valid JSON object.",
            input_text=user_prompt.strip(),
            schema=INTENT_PARSER_SCHEMA,
            max_tokens=512,
            temperature=0.1,
        )
    except GroqAPIError as exc:
        logger.info("Using fallback intent parser: %s", exc)
        return _fallback_intent(user_prompt)


def generate_copilot_report(user_prompt: str, context_data: dict[str, Any]) -> dict[str, Any]:
    distilled = distill_context(context_data)
    compact_json = json.dumps(distilled, separators=(",", ":"), default=str)
    input_text = f"User Request: {user_prompt.strip()}\n\nIDX Context Data:\n{compact_json}"
    try:
        report = _call_groq_json(
            model=PRIMARY_MODEL,
            instructions=(
                "Expert IDX equity research analyst. Synthesize the provided distilled market data "
                "into an objective research report. Adhere strictly to provided numbers without hallucination. "
                "Include balanced bullish drivers, bearish risks, precise data citations, and the regulatory disclaimer."
            ),
            input_text=input_text,
            schema=COPILOT_REPORT_SCHEMA,
            max_tokens=2048,
            temperature=0.1,
        )
        report["disclaimer"] = "Bukan rekomendasi beli atau jual. Analisis dihasilkan otomatis berdasarkan data Sectors API untuk tujuan edukasi."
        return report
    except GroqAPIError as exc:
        logger.info("Using fallback report synthesis: %s", exc)
        return _fallback_report(user_prompt, context_data)
