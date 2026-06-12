from django.utils import timezone
from django.db.models import Avg, Count, Q
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
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            outlet = Outlet.objects.get(id=data['outlet_id'], is_active=True)
        except Outlet.DoesNotExist:
            return Response(
                {'detail': 'Outlet not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND
            )

        within_geofence, distance_m = is_within_geofence(
            rep_lat=data['latitude'],
            rep_lon=data['longitude'],
            outlet_lat=outlet.latitude,
            outlet_lon=outlet.longitude,
        )

        visit_status = Visit.STATUS_SYNCED if within_geofence else Visit.STATUS_FLAGGED

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

        response_data = VisitSerializer(visit, context={'request': request}).data
        response_data['gps_distance_metres'] = distance_m
        response_data['gps_flagged'] = not within_geofence

        return Response(response_data, status=status.HTTP_201_CREATED)


class VisitListView(generics.ListAPIView):
    """
    GET /api/visits/
    GET /api/visits/?outlet_id=1
    GET /api/visits/?rep_name=John
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = VisitSerializer

    def get_queryset(self):
        queryset = Visit.objects.select_related('outlet').all()

        outlet_id = self.request.query_params.get('outlet_id')
        rep_name  = self.request.query_params.get('rep_name')

        if outlet_id:
            queryset = queryset.filter(outlet_id=outlet_id)
        if rep_name:
            queryset = queryset.filter(rep_name__icontains=rep_name)

        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class VisitDetailView(generics.RetrieveAPIView):
    """
    GET /api/visits/<id>/
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = VisitSerializer
    queryset           = Visit.objects.select_related('outlet').all()

    def get_serializer_context(self):
        return {'request': self.request}


class VisitStatsView(APIView):
    """
    GET /api/visits/stats/
    Returns aggregated statistics for the supervisor dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from analysis.models import ShelfAnalysis
        from fraud.models import FraudLog

        total_visits = Visit.objects.count()

        status_counts = Visit.objects.values('status').annotate(
            count=Count('id')
        )

        avg_compliance = ShelfAnalysis.objects.aggregate(
            avg=Avg('compliance_score')
        )['avg']

        total_fraud = FraudLog.objects.filter(is_fraud=True).count()

        low_compliance_count = ShelfAnalysis.objects.filter(
            compliance_score__lt=40.0
        ).count()

        outlet_stats = Visit.objects.values(
            'outlet__name'
        ).annotate(
            visit_count=Count('id'),
            fraud_count=Count('id', filter=Q(status='gps_flagged'))
        ).order_by('outlet__name')

        return Response({
            'total_visits':     total_visits,
            'total_fraud':      total_fraud,
            'low_compliance':   low_compliance_count,
            'avg_compliance':   round(avg_compliance or 0, 2),
            'status_breakdown': list(status_counts),
            'outlet_stats':     list(outlet_stats),
        })