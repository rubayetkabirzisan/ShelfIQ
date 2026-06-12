from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ShelfAnalysis
from .serializers import ShelfAnalysisSerializer
from .services import analyze_shelf_image
from visits.models import Visit


class AnalyzeView(APIView):
    """
    POST /api/analysis/analyze/

    Accepts a visit_id, loads the visit's image,
    sends it to Gemini, saves the result, returns it.

    Flow:
    1. Validate visit_id
    2. Load visit + check it has an image
    3. Call analyze_shelf_image() service
    4. Save result with update_or_create
    5. Return serialized result
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        visit_id = request.data.get('visit_id')
        if not visit_id:
            return Response(
                {'detail': 'visit_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Load visit with outlet (needed for outlet name in prompt)
        try:
            visit = Visit.objects.select_related('outlet').get(id=visit_id)
        except Visit.DoesNotExist:
            return Response(
                {'detail': f'Visit {visit_id} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the visit has an image
        if not visit.image:
            return Response(
                {'detail': 'This visit has no image. Upload an image first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Open the image file and call Gemini
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

        # Save or update the analysis result
        analysis, created = ShelfAnalysis.objects.update_or_create(
            visit=visit,
            defaults=results
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

    Returns all analyses — supervisor dashboard use.
    Optional filter: ?low_compliance=true returns only scores below 40.
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