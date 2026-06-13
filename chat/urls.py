from django.urls import path
from .views import ChatView, ChatHistoryView
urlpatterns = [
    path('message/', ChatView.as_view(),        name='chat-message'),
    path('history/', ChatHistoryView.as_view(),  name='chat-history'),
]
