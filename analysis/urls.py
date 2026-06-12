from django.urls import path
from .views import AnalyzeView, AnalysisByVisitView, AnalysisListView

urlpatterns = [
    path('analyze/',              AnalyzeView.as_view(),        name='analysis-analyze'),
    path('',                      AnalysisListView.as_view(),   name='analysis-list'),
    path('visit/<int:visit_id>/', AnalysisByVisitView.as_view(), name='analysis-by-visit'),
]