from django.urls import path
from .views import DashboardStatsView, ChartDataView, GrowthMetricsView

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('charts/', ChartDataView.as_view(), name='chart-data'),
    path('growth/', GrowthMetricsView.as_view(), name='growth-metrics'),
]
