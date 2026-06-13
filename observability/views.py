from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
import django
from ShelfIQ.middleware import get_metrics
class MetricsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        from visits.models import Visit
        from fraud.models import FraudLog
        from analysis.models import ShelfAnalysis
        metrics = get_metrics()
        metrics['db'] = {
            'total_visits':     Visit.objects.count(),
            'total_analyses':   ShelfAnalysis.objects.count(),
            'total_fraud_logs': FraudLog.objects.count(),
            'fraud_confirmed':  FraudLog.objects.filter(is_fraud=True).count(),
        }
        metrics['django_version'] = django.get_version()
        metrics['server_time']    = timezone.now().isoformat()
        return Response(metrics)
