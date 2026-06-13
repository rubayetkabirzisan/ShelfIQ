from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatRequestSerializer, ChatMessageSerializer
from .services import get_retailgpt_response
from fraud.permissions import IsSupervisor
class ChatView(APIView):
    permission_classes = [IsAuthenticated, IsSupervisor]
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        user_message = serializer.validated_data['message']
        ai_response  = get_retailgpt_response(
            user_message=user_message,
            username=request.user.username
        )
        chat_message = ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            response=ai_response
        )
        return Response(
            ChatMessageSerializer(chat_message).data,
            status=status.HTTP_201_CREATED
        )
class ChatHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSupervisor]
    serializer_class   = ChatMessageSerializer
    def get_queryset(self):
        return ChatMessage.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:50]
