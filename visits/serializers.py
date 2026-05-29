from rest_framework import serializers
from .models import Visit
from outlets.models import Outlet
from outlets.serializers import OutletSerializer


class CheckInSerializer(serializers.Serializer):
    """
    Validates the incoming check-in request.

    We use a plain Serializer (not ModelSerializer) here because
    the incoming data shape doesn't exactly match the model —
    we need to validate the fields, run GPS logic, then build
    the Visit object ourselves in the view.
    """
    outlet_id    = serializers.IntegerField()
    rep_name     = serializers.CharField(max_length=200)
    latitude     = serializers.FloatField()
    longitude    = serializers.FloatField()
    posm_ok      = serializers.BooleanField(default=False)
    checkin_time = serializers.DateTimeField()
    notes        = serializers.CharField(required=False, allow_blank=True, default='')
    # Image is handled separately as a file upload via request.FILES


class VisitSerializer(serializers.ModelSerializer):
    """
    Serializes a Visit for API responses.

    We include the nested outlet object (not just outlet_id)
    so the frontend gets the outlet name and address in one request.

    read_only=True on outlet means it's only used for output,
    never for input — you can't change the outlet by passing
    outlet data in a POST body.
    """
    outlet = OutletSerializer(read_only=True)

    # SerializerMethodField lets you add computed fields
    # The method name must be get_<field_name>
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Visit
        fields = [
            'id', 'outlet', 'rep_name',
            'latitude', 'longitude',
            'posm_ok', 'checkin_time',
            'status', 'notes', 'image_url',
            'created_at'
        ]

    def get_image_url(self, obj):
        """Return the full URL to the shelf image, or None if no image."""
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url