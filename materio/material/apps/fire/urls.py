from django.urls import path
from .views import (
    DashboardsView,
    PieCountbySeverity,
    LineCountbyMonth,
    MultilineIncidentTop3Country,
    multipleBarbySeverity
)

urlpatterns = [
    path(
        "",
        DashboardsView.as_view(template_name="dashboard_analytics.html"),
        name="index",
    ),
    path('chart/pie/', PieCountbySeverity, name='chart_pie'),
    path('chart/line/', LineCountbyMonth, name='chart_line'),
    path('chart/multiline/', MultilineIncidentTop3Country, name='chart_multiline'),
    path('chart/multibar/', multipleBarbySeverity, name='chart_multibar'),
]
