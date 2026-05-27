from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login requests.

    A Serializer is Django REST Framework's way of:
    1. Validating incoming JSON data (is username present? is it a string?)
    2. Converting Python objects to JSON (for responses)

    This serializer expects JSON like:
    { "username": "rep", "password": "rep123" }

    It will raise a validation error automatically if either field is missing
    or the wrong type — you don't write that validation yourself.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    # write_only=True means password will never appear in response JSON


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning user info (used in /auth/me/ endpoint).

    ModelSerializer automatically creates fields from the model.
    We declare exactly which fields to include — never expose password_hash.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        # 'password' is intentionally excluded