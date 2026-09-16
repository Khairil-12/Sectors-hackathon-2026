import json
import logging
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from research.forms import PromptForm, ScreenerSearchForm, WatchlistAddForm
from research.models import SavedReport, WatchlistItem
from research.services import sectors_api
from research.services.groq_client import FAST_MODEL, GroqAPIError, _client
from research.services.orchestrator import run_analysis, run_comparison
from research.services.sectors_api import SectorsAPIError

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def workspace(request):
    if request.method == "GET":
        recent_reports = SavedReport.objects.all()[:3]
        return render(
            request,
            "research/workspace.html",
            {
                "form": PromptForm(),
                "recent_reports": recent_reports,
            },
        )

    form = PromptForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors["prompt"][0]}, status=400)

    try:
        analysis = run_analysis(form.cleaned_data["prompt"])
    except (SectorsAPIError, GroqAPIError) as error:
        logger.warning("Analysis failed with upstream error: %s", error)
        return JsonResponse({"error": str(error)}, status=503)
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)
    except Exception as error:
        logger.error("Unexpected error in workspace analysis: %s", error, exc_info=True)
        return JsonResponse({"error": "Terjadi kesalahan internal saat analisis."}, status=500)

    if analysis.get("is_out_of_scope"):
        return JsonResponse(
            {
                "is_out_of_scope": True,
                "error": analysis.get("message", "Pertanyaan di luar lingkup riset saham IDX."),
                "suggestions": analysis.get("suggestions", []),
            },
            status=422,
        )

    report = analysis.get("report", {})
    saved = SavedReport.objects.create(
        title=report.get("title", "Equity Research Report"),
        symbols=report.get("analyzed_symbols", []),
        user_prompt=form.cleaned_data["prompt"],
        report_data=report,
    )
    return JsonResponse({"redirect": f"/report/{saved.pk}/", "reportId": saved.pk})


def report_detail(request, id):
    saved = get_object_or_404(SavedReport, pk=id)
    return render(
        request,
        "research/report.html",
        {
            "report": saved.report_data,
            "saved": saved,
        },
    )


@require_http_methods(["POST"])
def report_ask(request, id):
    """Answers a focused follow-up inquiry regarding an existing generated research report."""
    saved = get_object_or_404(SavedReport, pk=id)
    question = request.POST.get("question", "").strip()

    if len(question) < 3:
        return render(
            request,
            "research/partials/followup_response.html",
            {
                "error": "Pertanyaan follow-up minimal 3 karakter.",
                "question": question,
            },
            status=400,
        )

    lang = "id" if any(w in question.lower() for w in ["apakah", "bagaimana", "mengapa", "kenapa", "berapa", "dividen", "laba", "saham", "kinerja", "target"]) else "en"

    prompt_context = {
        "report_title": saved.title,
        "analyzed_symbols": saved.symbols,
        "original_prompt": saved.user_prompt,
        "fundamental_analysis": saved.report_data.get("fundamental_analysis", {}),
        "flow_and_momentum": saved.report_data.get("flow_and_momentum", {}),
        "bullish_drivers": saved.report_data.get("bullish_drivers", []),
        "bearish_risks": saved.report_data.get("bearish_risks", []),
        "flow_divergences": saved.report_data.get("flow_divergences", []),
    }

    system_instruction = (
        "You are an IDX Equity Research Copilot answering a follow-up inquiry on an existing research report. "
        "Strictly base your answer on the provided report context and numbers. Keep your response concise (2-4 paragraphs maximum), "
        "direct, and actionable without speculating. "
        + ("Respond in Indonesian." if lang == "id" else "Respond in English.")
    )

    try:
        api_key = getattr(settings, "GROQ_API_KEY", "")
        if not api_key or api_key == "your_groq_api_key_here":
            answer = f"Berdasarkan data laporan untuk {', '.join(saved.symbols)}, emiten ini memiliki status valuasi {saved.report_data.get('fundamental_analysis', {}).get('valuation_verdict', 'fair')} dengan sentimen arus modal {saved.report_data.get('flow_and_momentum', {}).get('foreign_flow_sentiment', 'neutral')}."
        else:
            client = _client()
            response = client.chat.completions.create(
                model=FAST_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Existing Report Context:\n{json.dumps(prompt_context, default=str)}\n\nFollow-up Question: {question}"},
                ],
                max_tokens=600,
                temperature=0.2,
            )
            answer = response.choices[0].message.content or "Tidak ada jawaban yang dihasilkan."
    except Exception as exc:
        logger.warning("Follow-up Q&A failed: %s", exc)
        answer = f"Berdasarkan data laporan, emiten menunjukkan valuasi {saved.report_data.get('fundamental_analysis', {}).get('valuation_verdict', 'fair')} dengan sentimen {saved.report_data.get('flow_and_momentum', {}).get('foreign_flow_sentiment', 'neutral')}."

    return render(
        request,
        "research/partials/followup_response.html",
        {
            "question": question,
            "answer": answer,
        },
    )


@require_http_methods(["POST", "DELETE"])
def report_delete(request, id):
    saved = get_object_or_404(SavedReport, pk=id)
    saved.delete()
    if request.headers.get("HX-Request"):
        return HttpResponse("")
    messages.success(request, "Report deleted successfully.")
    return redirect("research:saved_reports")



@require_http_methods(["GET", "POST"])
def comparison(request):
    symbols_param = request.GET.get("symbols", "") or request.POST.get("symbols", "")
    symbols = [s.strip().upper() for s in symbols_param.split(",") if s.strip()][:10]

    comparison_data = []
    if symbols:
        try:
            comparison_data = run_comparison(symbols)
        except Exception as error:
            logger.warning("Error running comparison for %s: %s", symbols, error)
            messages.error(request, "Failed to load comparison data for requested symbols.")

    return render(
        request,
        "research/comparison.html",
        {
            "symbols_param": ", ".join(symbols) if symbols else "",
            "comparison_data": comparison_data,
            "selected_symbols": symbols,
        },
    )


@require_http_methods(["GET", "POST"])
def screener(request):
    query = ""
    results = None
    preset = request.GET.get("preset", "") or request.POST.get("preset", "")

    if request.method == "POST":
        query = request.POST.get("query", "").strip()

    if not query and request.GET.get("q"):
        query = request.GET.get("q", "").strip()

    try:
        if preset == "banks":
            data = sectors_api.get_screener(
                q="top banks with strong return on equity and growing assets. Show market cap, forward PE, PB ratio, dividend yield, and sub sector for each company."
            )
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "Top IDX Banking Institutions"
        elif preset == "dividends":
            data = sectors_api.get_screener(
                q="companies with high dividend yield and stable cash flow. Show market cap, forward PE, PB ratio, dividend yield, and sub sector for each company."
            )
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "High Dividend Yield Stocks"
        elif preset == "value":
            data = sectors_api.get_screener(
                q="undervalued companies with low price to earnings and low price to book. Show market cap, forward PE, PB ratio, dividend yield, and sub sector for each company."
            )
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "Undervalued Value Opportunities"
        elif query:
            data = sectors_api.get_screener(
                q=f"{query}. Show market cap, PE ratio, PB ratio, dividend yield, and subsector for each company."
            )
            results = data.get("results", data) if isinstance(data, dict) else data
        else:
            data = sectors_api.get_screener(
                q="top 20 companies by market cap, PE ratio, PB ratio, dividend yield, and subsector"
            )
            results = data.get("results", data) if isinstance(data, dict) else data
    except SectorsAPIError as error:
        messages.error(request, error.message)
    except Exception as error:
        logger.warning("Screener failed: %s", error)

    clean_results = []
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                qv = item.get("query_values", {}) if isinstance(item.get("query_values"), dict) else {}
                
                market_cap = item.get("market_cap") or qv.get("market_cap")
                pe_ratio = (
                    item.get("pe_ttm")
                    or item.get("forward_pe")
                    or item.get("pe_ratio")
                    or item.get("pe")
                    or qv.get("pe_ttm")
                    or qv.get("forward_pe")
                    or qv.get("pe_ratio")
                    or qv.get("pe")
                )
                pb_ratio = (
                    item.get("pb_mrq")
                    or item.get("pb_ratio")
                    or item.get("pb")
                    or qv.get("pb_mrq")
                    or qv.get("pb_ratio")
                    or qv.get("pb")
                )
                div_yield = (
                    item.get("yield_ttm")
                    or item.get("dividend_yield")
                    or item.get("total_yield")
                    or item.get("yield")
                    or qv.get("yield_ttm")
                    or qv.get("dividend_yield")
                    or qv.get("total_yield")
                    or qv.get("yield")
                    or next((value for key, value in qv.items() if key.startswith("total_yield[")), None)
                )
                if isinstance(div_yield, (int, float)) and abs(div_yield) <= 1:
                    div_yield *= 100
                sub_sec = (
                    item.get("sub_sector")
                    or item.get("sub_industry")
                    or item.get("industry")
                    or item.get("sector")
                    or qv.get("sub_sector")
                    or qv.get("sub_industry")
                    or qv.get("industry")
                    or qv.get("sector")
                    or "General"
                )

                clean_results.append({
                    "symbol": item.get("symbol", ""),
                    "company_name": item.get("company_name", ""),
                    "sub_sector": sub_sec,
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "dividend_yield": div_yield,
                })

    return render(
        request,
        "research/screener.html",
        {
            "query": query,
            "preset": preset,
            "results": clean_results,
        },
    )


def dashboard(request):
    top_movers = []
    most_traded = []
    watchlist_items = WatchlistItem.objects.all()[:6]
    saved_reports = SavedReport.objects.all()[:5]

    try:
        raw_movers = sectors_api.get_top_changes(
            classifications="top_gainers",
            periods="1d",
            n_stock=5,
        )
        movers_raw = []
        if isinstance(raw_movers, dict):
            tg = raw_movers.get("top_gainers", {})
            if isinstance(tg, dict):
                movers_raw = tg.get("1d", []) or (next(iter(tg.values())) if tg else [])
            elif isinstance(tg, list):
                movers_raw = tg
            elif "results" in raw_movers and isinstance(raw_movers["results"], list):
                movers_raw = raw_movers["results"]
            else:
                for v in raw_movers.values():
                    if isinstance(v, list):
                        movers_raw = v
                        break
        elif isinstance(raw_movers, list):
            movers_raw = raw_movers

        for m in movers_raw:
            if not isinstance(m, dict):
                continue
            sym = m.get("symbol", "")
            name = m.get("company_name") or m.get("name") or sym
            price = m.get("price") or m.get("last_close_price") or m.get("close") or 0
            change_pct = m.get("change_pct")
            if change_pct is None and "price_change" in m:
                pc = float(m["price_change"] or 0)
                change_pct = pc * 100.0 if abs(pc) <= 1.0 and pc != 0 else pc
            top_movers.append({
                "symbol": sym,
                "company_name": name,
                "price": price,
                "change_pct": float(change_pct or 0.0),
            })
    except Exception as exc:
        logger.warning("Failed to fetch top changes for dashboard: %s", exc)

    try:
        raw_traded = sectors_api.get_most_traded(n_stock=5)
        traded_raw = []
        if isinstance(raw_traded, dict):
            if raw_traded:
                latest_date = sorted(raw_traded.keys(), reverse=True)[0]
                date_val = raw_traded.get(latest_date, [])
                if isinstance(date_val, list):
                    traded_raw = date_val
                elif "results" in raw_traded and isinstance(raw_traded["results"], list):
                    traded_raw = raw_traded["results"]
        elif isinstance(raw_traded, list):
            traded_raw = raw_traded

        for t in traded_raw:
            if not isinstance(t, dict):
                continue
            sym = t.get("symbol", "")
            name = t.get("company_name") or t.get("name") or sym
            vol = t.get("volume") or 0
            price = t.get("price") or t.get("last_close_price") or 0
            val = t.get("value")
            if val is None:
                val = vol * price if vol and price else 0
            most_traded.append({
                "symbol": sym,
                "company_name": name,
                "volume": vol,
                "price": price,
                "value": val,
            })
    except Exception as exc:
        logger.warning("Failed to fetch most traded for dashboard: %s", exc)

    return render(
        request,
        "research/dashboard.html",
        {
            "report_count": SavedReport.objects.count(),
            "watchlist_count": WatchlistItem.objects.count(),
            "top_movers": top_movers[:5],
            "most_traded": most_traded[:5],
            "watchlist_items": watchlist_items,
            "saved_reports": saved_reports,
        },
    )


def watchlist(request):
    watchlist_items = WatchlistItem.objects.all()
    enriched_items = []

    for item in watchlist_items:
        data = {
            "id": item.pk,
            "symbol": item.symbol,
            "company_name": f"{item.symbol} Tbk",
            "price": "N/A",
            "pe_ratio": "N/A",
            "added_at": item.added_at,
        }
        try:
            rep = sectors_api.get_company_report(item.symbol)
            if isinstance(rep, dict):
                data["company_name"] = rep.get("overview", {}).get("company_name", data["company_name"])
                data["pe_ratio"] = rep.get("valuation", {}).get("pe_ratio", "N/A")
        except Exception:
            pass
        enriched_items.append(data)

    return render(
        request,
        "research/watchlist.html",
        {
            "form": WatchlistAddForm(),
            "watchlist_items": enriched_items,
        },
    )


@require_http_methods(["POST"])
def watchlist_add(request):
    form = WatchlistAddForm(request.POST)
    if form.is_valid():
        symbol = form.cleaned_data["symbol"]
        WatchlistItem.objects.get_or_create(symbol=symbol)
        messages.success(request, f"Added {symbol} to your watchlist.")
    else:
        for error in form.errors.values():
            messages.error(request, error[0])

    if request.headers.get("HX-Request"):
        return redirect("research:watchlist")
    return redirect("research:watchlist")


@require_http_methods(["POST", "DELETE"])
def watchlist_remove(request, id):
    item = get_object_or_404(WatchlistItem, pk=id)
    item.delete()
    if request.headers.get("HX-Request"):
        return HttpResponse("")
    messages.success(request, "Removed from watchlist.")
    return redirect("research:watchlist")


def saved_reports(request):
    query = request.GET.get("q", "").strip()
    reports = SavedReport.objects.all()
    if query:
        reports = reports.filter(title__icontains=query) | reports.filter(user_prompt__icontains=query)

    return render(
        request,
        "research/saved_reports.html",
        {
            "reports": reports,
            "query": query,
        },
    )
