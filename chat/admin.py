from django.contrib import admin
from .models import ChatMessage
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ['user', 'created_at']
    list_filter   = ['user']
    readonly_fields = ['created_at']
