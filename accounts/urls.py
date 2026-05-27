from django.urls import path
from .views import LoginView, MeView

# These URL patterns will be mounted at /api/auth/ by the root urls.py
urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('me/', MeView.as_view(), name='auth-me'),
]