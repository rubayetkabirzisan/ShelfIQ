from django.contrib import admin
from .models import FraudLog

@admin.register(FraudLog)
class FraudLogAdmin(admin.ModelAdmin):
    list_display  = ['visit', 'is_fraud', 'is_duplicate',
                     'is_blurry', 'is_gps_flagged',
                     'is_timestamp_bad', 'created_at']
    list_filter   = ['is_fraud', 'is_duplicate', 'is_blurry',
                     'is_gps_flagged', 'is_timestamp_bad']
    readonly_fields = ['created_at']