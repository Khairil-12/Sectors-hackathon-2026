from django.urls import path
from research import views

app_name = "research"

urlpatterns = [
    path("", views.workspace, name="workspace"),
    path("report/<str:id>/", views.report_detail, name="report_detail"),
    path("report/<str:id>/delete/", views.report_delete, name="report_delete"),
    path("compare/", views.comparison, name="comparison"),
    path("screener/", views.screener, name="screener"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/add/", views.watchlist_add, name="watchlist_add"),
    path("watchlist/remove/<int:id>/", views.watchlist_remove, name="watchlist_remove"),
    path("saved-reports/", views.saved_reports, name="saved_reports"),
]
