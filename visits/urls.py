from django.urls import path
from .views import CheckInView, VisitListView, VisitDetailView

urlpatterns = [
    path('checkin/',  CheckInView.as_view(),    name='visit-checkin'),
    path('',          VisitListView.as_view(),  name='visit-list'),
    path('<int:pk>/', VisitDetailView.as_view(), name='visit-detail'),
]