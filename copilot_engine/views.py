from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from copilot_engine.forms import PromptForm
from copilot_engine.models import SavedReport
from copilot_engine.services.groq_client import GroqAPIError
from copilot_engine.services.orchestrator import run_analysis
from copilot_engine.services.sectors_api import SectorsAPIError


@require_http_methods(["GET", "POST"])
def workspace(request):
    if request.method == "GET":
        return render(request, "copilot_engine/workspace.html", {"form": PromptForm()})

    form = PromptForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors["prompt"][0]}, status=400)

    try:
        analysis = run_analysis(form.cleaned_data["prompt"])
    except (SectorsAPIError, GroqAPIError) as error:
        return JsonResponse({"error": str(error)}, status=503)
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=400)

    report = analysis["report"]
    saved = SavedReport.objects.create(
        title=report["title"],
        symbols=report["analyzed_symbols"],
        user_prompt=form.cleaned_data["prompt"],
        report_data=report,
    )
    return JsonResponse({"redirect": f"/report/{saved.pk}/"})


def report_detail(request, id):
    saved = get_object_or_404(SavedReport, pk=id)
    return render(request, "copilot_engine/report.html", {"report": saved.report_data, "saved": saved})


def comparison(request):
    return render(request, "copilot_engine/comparison.html")


@require_http_methods(["GET", "POST"])
def screener(request):
    results = None
    query = ""
    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            from copilot_engine.services import sectors_api
            try:
                results = sectors_api.get_screener(q=query)
            except SectorsAPIError as error:
                messages.error(request, error.message)
    return render(request, "copilot_engine/screener.html", {"query": query, "results": results})


def dashboard(request):
    return render(request, "copilot_engine/dashboard.html", {"report_count": SavedReport.objects.count()})


def watchlist(request):
    return render(request, "copilot_engine/watchlist.html")


def saved_reports(request):
    return render(request, "copilot_engine/saved_reports.html", {"reports": SavedReport.objects.all()})
