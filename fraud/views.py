from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FraudLog
from .serializers import FraudCheckRequestSerializer, FraudLogSerializer
from .engine import run_all_checks
from .permissions import IsSupervisor
from visits.models import Visit
from alerts.services import send_fraud_alert


class FraudCheckView(APIView):
    """
    POST /api/fraud/check/
    Runs all 4 fraud checks on a visit and saves the result.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FraudCheckRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        visit_id = serializer.validated_data['visit_id']

        try:
            visit = Visit.objects.select_related('outlet').get(id=visit_id)
        except Visit.DoesNotExist:
            return Response(
                {'detail': f'Visit {visit_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        image_file = None
        if visit.image:
            try:
                image_file = visit.image.open('rb')
            except (FileNotFoundError, OSError):
                image_file = None

        results = run_all_checks(visit, image_file)

        if image_file:
            image_file.close()

        fraud_log, created = FraudLog.objects.update_or_create(
            visit=visit,
            defaults=results
        )

        if fraud_log.is_fraud:
            fraud_types = []
            if fraud_log.is_duplicate:     fraud_types.append('Duplicate Image')
            if fraud_log.is_blurry:        fraud_types.append('Blurry Image')
            if fraud_log.is_gps_flagged:   fraud_types.append('GPS Spoofing')
            if fraud_log.is_timestamp_bad: fraud_types.append('Timestamp Anomaly')
            send_fraud_alert(
                rep_name=visit.rep_name,
                outlet_name=visit.outlet.name,
                fraud_types=fraud_types
            )

        return Response(
            FraudLogSerializer(fraud_log).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class FraudLogListView(generics.ListAPIView):
    """
    GET /api/fraud/logs/
    Supervisor only — returns all fraud logs.
    """
    permission_classes = [IsAuthenticated, IsSupervisor]
    serializer_class   = FraudLogSerializer

    def get_queryset(self):
        queryset = FraudLog.objects.select_related(
            'visit', 'visit__outlet'
        ).all()

        fraud_only = self.request.query_params.get('fraud_only')
        if fraud_only and fraud_only.lower() == 'true':
            queryset = queryset.filter(is_fraud=True)

        return queryset


class FraudLogByVisitView(generics.RetrieveAPIView):
    """
    GET /api/fraud/visit/<visit_id>/
    Returns the fraud log for a specific visit.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = FraudLogSerializer

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            FraudLog.objects.select_related('visit', 'visit__outlet'),
            visit_id=self.kwargs['visit_id']
        )