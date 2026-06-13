from rest_framework import serializers
from .models import ChatMessage
class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model  = ChatMessage
        fields = ['id', 'username', 'message', 'response', 'created_at']
