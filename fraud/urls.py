from django.urls import path
from .views import FraudCheckView, FraudLogListView, FraudLogByVisitView

urlpatterns = [
    path('check/',             FraudCheckView.as_view(),     name='fraud-check'),
    path('logs/',              FraudLogListView.as_view(),   name='fraud-logs'),
    path('visit/<int:visit_id>/', FraudLogByVisitView.as_view(), name='fraud-by-visit'),
]