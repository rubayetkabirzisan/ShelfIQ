from rest_framework import serializers
from .models import Outlet


class OutletSerializer(serializers.ModelSerializer):
    """
    Serializes an Outlet for API responses.

    ModelSerializer automatically creates fields matching the model.
    We list every field we want the frontend to receive.
    """
    class Meta:
        model  = Outlet
        fields = [
            'id', 'name', 'address',
            'latitude', 'longitude',
            'target_posm', 'is_active'
        ]