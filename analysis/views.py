from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ShelfAnalysis
from .serializers import ShelfAnalysisSerializer
from .services import analyze_shelf_image
from visits.models import Visit
from alerts.services import send_low_compliance_alert


class AnalyzeView(APIView):
    """
    POST /api/analysis/analyze/
    Sends the visit's shelf image to Gemini and saves the result.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        visit_id = request.data.get('visit_id')
        if not visit_id:
            return Response(
                {'detail': 'visit_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            visit = Visit.objects.select_related('outlet').get(id=visit_id)
        except Visit.DoesNotExist:
            return Response(
                {'detail': f'Visit {visit_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not visit.image:
            return Response(
                {'detail': 'This visit has no image. Upload an image first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with visit.image.open('rb') as image_file:
                results = analyze_shelf_image(
                    image_file=image_file,
                    outlet_name=visit.outlet.name
                )
        except (FileNotFoundError, OSError):
            return Response(
                {'detail': 'Image file not found on disk.'},
                status=status.HTTP_404_NOT_FOUND
            )

        analysis, created = ShelfAnalysis.objects.update_or_create(
            visit=visit,
            defaults=results
        )

        if analysis.compliance_score < 40.0 and analysis.analysis_successful:
            send_low_compliance_alert(
                outlet_name=visit.outlet.name,
                score=analysis.compliance_score
            )

        return Response(
            ShelfAnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class AnalysisByVisitView(generics.RetrieveAPIView):
    """
    GET /api/analysis/visit/<visit_id>/
    Returns the analysis result for a specific visit.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = ShelfAnalysisSerializer

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            ShelfAnalysis.objects.select_related('visit', 'visit__outlet'),
            visit_id=self.kwargs['visit_id']
        )


class AnalysisListView(generics.ListAPIView):
    """
    GET /api/analysis/
    GET /api/analysis/?low_compliance=true
    Returns all analyses, optionally filtered by low compliance.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = ShelfAnalysisSerializer

    def get_queryset(self):
        queryset = ShelfAnalysis.objects.select_related(
            'visit', 'visit__outlet'
        ).all()

        low_compliance = self.request.query_params.get('low_compliance')
        if low_compliance and low_compliance.lower() == 'true':
            queryset = queryset.filter(compliance_score__lt=40.0)

        return queryset