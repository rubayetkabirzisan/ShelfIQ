from rest_framework import serializers
from .models import ShelfAnalysis


class ShelfAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializes ShelfAnalysis for API responses.
    Adds visit context fields via dot-traversal.
    """
    visit_id    = serializers.IntegerField(source='visit.id',          read_only=True)
    outlet_name = serializers.CharField(source='visit.outlet.name',    read_only=True)
    rep_name    = serializers.CharField(source='visit.rep_name',       read_only=True)

    class Meta:
        model  = ShelfAnalysis
        fields = [
            'id', 'visit_id', 'outlet_name', 'rep_name',
            'our_count', 'competitor_count', 'compliance_score',
            'supervisor_summary', 'analysis_successful', 'analyzed_at',
        ]
        # raw_response excluded — internal debugging field, not for frontend