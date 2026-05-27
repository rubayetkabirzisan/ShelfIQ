from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add 'role' to the display columns in the admin list
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role']
    # Add 'role' to the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('RetailOS Role', {'fields': ('role',)}),
    )