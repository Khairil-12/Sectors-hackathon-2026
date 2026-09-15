from __future__ import annotations

import logging
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from research.forms import PromptForm, ScreenerSearchForm, WatchlistAddForm
from research.models import SavedReport, WatchlistItem
from research.services import sectors_api
from research.services.groq_client import GroqAPIError
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
    symbols = [s.strip().upper() for s in symbols_param.split(",") if s.strip()]

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
            data = sectors_api.get_screener(q="top banks with strong return on equity and growing assets")
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "Top IDX Banking Institutions"
        elif preset == "dividends":
            data = sectors_api.get_screener(q="companies with high dividend yield and stable cash flow")
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "High Dividend Yield Stocks"
        elif preset == "value":
            data = sectors_api.get_screener(q="undervalued companies with low price to earnings and low price to book")
            results = data.get("results", data) if isinstance(data, dict) else data
            query = "Undervalued Value Opportunities"
        elif query:
            data = sectors_api.get_screener(q=query)
            results = data.get("results", data) if isinstance(data, dict) else data
        else:
            # Default initial screener view
            data = sectors_api.get_screener()
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
                clean_results.append({
                    "symbol": item.get("symbol", ""),
                    "company_name": item.get("company_name", ""),
                    "sub_sector": item.get("sub_sector") or item.get("industry") or qv.get("sub_sector") or "General",
                    "market_cap": item.get("market_cap"),
                    "pe_ratio": item.get("pe_ratio"),
                    "pb_ratio": item.get("pb_ratio"),
                    "dividend_yield": item.get("dividend_yield"),
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
        top_movers = sectors_api.get_top_changes()
        if not isinstance(top_movers, list):
            top_movers = []
    except Exception as exc:
        logger.warning("Failed to fetch top changes for dashboard: %s", exc)

    try:
        most_traded = sectors_api.get_most_traded()
        if not isinstance(most_traded, list):
            most_traded = []
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
