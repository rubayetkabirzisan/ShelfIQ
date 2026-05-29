from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Outlet
from .serializers import OutletSerializer


class OutletListView(generics.ListAPIView):
    """
    GET /api/visits/outlets/

    Returns the list of all active retail outlets.

    Why AllowAny? The rep needs to see the outlet list on the
    login/check-in screen before they are authenticated.

    generics.ListAPIView is a DRF shortcut — it gives you a fully
    working GET list endpoint in 3 lines. No need to write get(),
    serializer instantiation, or Response() yourself.
    """
    permission_classes = [AllowAny]
    queryset           = Outlet.objects.filter(is_active=True)
    serializer_class   = OutletSerializer