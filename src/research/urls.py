from django.urls import path
from research import views

app_name = "research"

urlpatterns = [
    path("", views.workspace, name="workspace"),
    path("report/<str:id>/", views.report_detail, name="report_detail"),
    path("compare/", views.comparison, name="comparison"),
    path("screener/", views.screener, name="screener"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("saved-reports/", views.saved_reports, name="saved_reports"),
]
