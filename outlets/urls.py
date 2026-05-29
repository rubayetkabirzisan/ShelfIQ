from django.urls import path
from .views import OutletListView

urlpatterns = [
    path('outlets/', OutletListView.as_view(), name='outlet-list'),
]