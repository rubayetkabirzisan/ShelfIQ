from django.urls import path
from .views import CheckInView, VisitListView, VisitDetailView, VisitStatsView

urlpatterns = [
    path('checkin/',  CheckInView.as_view(),    name='visit-checkin'),
    path('stats/',    VisitStatsView.as_view(), name='visit-stats'),
    path('',          VisitListView.as_view(),  name='visit-list'),
    path('<int:pk>/', VisitDetailView.as_view(), name='visit-detail'),
]