from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display  = ['rep_name', 'outlet', 'checkin_time', 'status', 'posm_ok']
    list_filter   = ['status', 'outlet']
    search_fields = ['rep_name']
    readonly_fields = ['created_at']