from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserSerializer
from .models import User


class LoginView(APIView):
    """
    POST /api/auth/login/

    Accepts username + password, returns JWT tokens + user info.

    permission_classes = [AllowAny] means this endpoint does NOT require
    authentication — of course, because the user hasn't logged in yet.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Step 1: Validate the incoming JSON
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Step 2: Check credentials against the database
        # authenticate() handles password hashing — never compare raw passwords
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Step 3: Generate JWT tokens
        # RefreshToken.for_user() creates a token pair linked to this user
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),   # short-lived (24h)
            'refresh': str(refresh),                # long-lived (7 days)
            'role': user.role,
            'username': user.username,
        })


class MeView(APIView):
    """
    GET /api/auth/me/

    Returns info about the currently logged-in user.
    permission_classes = [IsAuthenticated] means you must send a valid
    JWT Bearer token in the Authorization header to reach this endpoint.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user is automatically set by JWT authentication middleware
        # It's the User object from the database, decoded from the token
        serializer = UserSerializer(request.user)
        return Response(serializer.data)