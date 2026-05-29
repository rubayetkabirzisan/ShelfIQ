from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Visit
from .serializers import CheckInSerializer, VisitSerializer
from .utils import is_within_geofence
from outlets.models import Outlet


class CheckInView(APIView):
    """
    POST /api/visits/checkin/

    The main rep workflow endpoint. Accepts multipart form data
    (so it can receive both JSON fields AND a file upload in one request).

    Flow:
    1. Validate fields with CheckInSerializer
    2. Look up the outlet
    3. Run GPS geofence check
    4. Save the Visit with status (synced or gps_flagged)
    5. Return the created visit
    """
    permission_classes = [IsAuthenticated]
    # MultiPartParser handles file uploads (image)
    # FormParser handles regular form fields alongside files
    # JSONParser handles pure JSON requests (when no file is sent)
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Step 1: Look up the outlet
        try:
            outlet = Outlet.objects.get(id=data['outlet_id'], is_active=True)
        except Outlet.DoesNotExist:
            return Response(
                {'detail': 'Outlet not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Step 2: GPS geofence validation
        within_geofence, distance_m = is_within_geofence(
            rep_lat=data['latitude'],
            rep_lon=data['longitude'],
            outlet_lat=outlet.latitude,
            outlet_lon=outlet.longitude,
        )

        visit_status = Visit.STATUS_SYNCED if within_geofence else Visit.STATUS_FLAGGED

        # Step 3: Create the Visit record
        # request.FILES.get('image') returns the uploaded file object, or None
        visit = Visit.objects.create(
            outlet=outlet,
            rep_name=data['rep_name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            posm_ok=data['posm_ok'],
            checkin_time=data['checkin_time'],
            notes=data.get('notes', ''),
            status=visit_status,
            image=request.FILES.get('image'),
        )

        # Step 4: Return response
        response_data = VisitSerializer(visit, context={'request': request}).data
        response_data['gps_distance_metres'] = distance_m
        response_data['gps_flagged'] = not within_geofence

        return Response(response_data, status=status.HTTP_201_CREATED)


class VisitListView(generics.ListAPIView):
    """
    GET /api/visits/
    GET /api/visits/?outlet_id=1
    GET /api/visits/?rep_name=John

    Returns all visits, newest first.
    Supervisors use this to see the full dashboard.
    Optional query parameter filtering by outlet or rep.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = VisitSerializer

    def get_queryset(self):
        """
        get_queryset() is called by ListAPIView to get the data.
        Overriding it lets us add filtering logic.

        select_related('outlet') is a performance optimization:
        instead of making a separate DB query for each visit's outlet,
        Django fetches everything in a single JOIN query.
        """
        queryset = Visit.objects.select_related('outlet').all()

        # Optional filters from query parameters
        outlet_id = self.request.query_params.get('outlet_id')
        rep_name  = self.request.query_params.get('rep_name')

        if outlet_id:
            queryset = queryset.filter(outlet_id=outlet_id)
        if rep_name:
            queryset = queryset.filter(rep_name__icontains=rep_name)
            # __icontains = case-insensitive LIKE '%name%'

        return queryset

    def get_serializer_context(self):
        """Pass request to serializer so image_url can build absolute URLs."""
        return {'request': self.request}


class VisitDetailView(generics.RetrieveAPIView):
    """
    GET /api/visits/<id>/

    Returns a single visit by ID.
    Used when the frontend needs full details for one check-in.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = VisitSerializer
    queryset           = Visit.objects.select_related('outlet').all()

    def get_serializer_context(self):
        return {'request': self.request}