from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FraudLog
from .serializers import FraudCheckRequestSerializer, FraudLogSerializer
from .engine import run_all_checks
from .permissions import IsSupervisor
from visits.models import Visit


class FraudCheckView(APIView):
    """
    POST /api/fraud/check/

    Accepts a visit_id, runs all 4 fraud checks,
    saves the result as a FraudLog, returns the result.

    Any authenticated user (rep or supervisor) can trigger this.
    Typically called immediately after a check-in.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FraudCheckRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        visit_id = serializer.validated_data['visit_id']

        # Load the visit with outlet data (needed for GPS check)
        try:
            visit = Visit.objects.select_related('outlet').get(id=visit_id)
        except Visit.DoesNotExist:
            return Response(
                {'detail': f'Visit {visit_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the image file if the visit has one
        image_file = None
        if visit.image:
            try:
                image_file = visit.image.open('rb')
            except (FileNotFoundError, OSError):
                image_file = None

        # Run all 4 checks
        results = run_all_checks(visit, image_file)

        if image_file:
            image_file.close()

        # Save or update the FraudLog
        # update_or_create: if a FraudLog for this visit exists, update it.
        # If not, create it. This makes the endpoint safely re-runnable.
        fraud_log, created = FraudLog.objects.update_or_create(
            visit=visit,
            defaults=results
        )

        return Response(
            FraudLogSerializer(fraud_log).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class FraudLogListView(generics.ListAPIView):
    """
    GET /api/fraud/logs/

    Returns all fraud logs. Supervisor only.
    Supervisors use this to see the full fraud audit dashboard.
    """
    permission_classes = [IsAuthenticated, IsSupervisor]
    serializer_class   = FraudLogSerializer

    def get_queryset(self):
        queryset = FraudLog.objects.select_related(
            'visit', 'visit__outlet'
            # select_related can follow chains with double underscores
            # 'visit__outlet' = JOIN visits JOIN outlets in one query
        ).all()

        # Optional filter: only show confirmed fraud
        fraud_only = self.request.query_params.get('fraud_only')
        if fraud_only and fraud_only.lower() == 'true':
            queryset = queryset.filter(is_fraud=True)

        return queryset


class FraudLogByVisitView(generics.RetrieveAPIView):
    """
    GET /api/fraud/visit/<visit_id>/

    Returns the fraud log for a specific visit.
    Uses visit_id in the URL instead of fraud_log_id.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = FraudLogSerializer

    def get_object(self):
        visit_id = self.kwargs['visit_id']
        # get_object_or_404 raises a 404 response automatically if not found
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            FraudLog.objects.select_related('visit', 'visit__outlet'),
            visit_id=visit_id
        )