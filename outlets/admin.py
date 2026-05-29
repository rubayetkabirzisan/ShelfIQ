from django.contrib import admin
from .models import Outlet

@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display  = ['name', 'address', 'latitude', 'longitude', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['name', 'address']