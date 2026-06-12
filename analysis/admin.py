from django.contrib import admin
from .models import ShelfAnalysis

@admin.register(ShelfAnalysis)
class ShelfAnalysisAdmin(admin.ModelAdmin):
    list_display  = [
        'visit', 'compliance_score', 'our_count',
        'competitor_count', 'analysis_successful', 'analyzed_at'
    ]
    list_filter   = ['analysis_successful']
    readonly_fields = ['analyzed_at', 'raw_response']