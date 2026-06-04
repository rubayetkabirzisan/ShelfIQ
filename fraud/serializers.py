from rest_framework import serializers
from .models import FraudLog


class FraudCheckRequestSerializer(serializers.Serializer):
    """
    Validates the incoming fraud check request.
    Only needs the visit_id — we load everything else from the DB.
    """
    visit_id = serializers.IntegerField()


class FraudLogSerializer(serializers.ModelSerializer):
    """
    Serializes a FraudLog for API responses.
    Includes a nested summary of the visit it belongs to.
    """
    visit_id     = serializers.IntegerField(source='visit.id', read_only=True)
    outlet_name  = serializers.CharField(source='visit.outlet.name', read_only=True)
    rep_name     = serializers.CharField(source='visit.rep_name', read_only=True)
    checkin_time = serializers.DateTimeField(source='visit.checkin_time', read_only=True)

    # source='visit.outlet.name' means: follow visit → outlet → name
    # This is called dot-traversal in DRF serializers

    class Meta:
        model  = FraudLog
        fields = [
            'id', 'visit_id', 'outlet_name', 'rep_name', 'checkin_time',
            'is_duplicate', 'is_blurry', 'is_gps_flagged', 'is_timestamp_bad',
            'is_fraud',
            'duplicate_detail', 'blur_detail', 'gps_detail', 'timestamp_detail',
            'created_at',
        ]