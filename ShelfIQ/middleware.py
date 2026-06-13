import time
import threading
from collections import deque
from django.utils.deprecation import MiddlewareMixin
_local = threading.local()
_metrics = {
    'total_requests':     0,
    'total_errors':       0,
    'total_checkins':     0,
    'total_analyses':     0,
    'total_fraud_checks': 0,
    'request_log':        deque(maxlen=100),
    'response_times':     deque(maxlen=100),
}
_metrics_lock = threading.Lock()
class ObservabilityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _local.start_time = time.time()
        return None
    def process_response(self, request, response):
        duration_ms = (
            time.time() - getattr(_local, 'start_time', time.time())
        ) * 1000
        path   = request.path
        method = request.method
        status = response.status_code
        with _metrics_lock:
            _metrics['total_requests'] += 1
            if status >= 400:
                _metrics['total_errors'] += 1
            if 'checkin' in path and method == 'POST':
                _metrics['total_checkins'] += 1
            if 'analysis' in path and method == 'POST':
                _metrics['total_analyses'] += 1
            if 'fraud/check' in path and method == 'POST':
                _metrics['total_fraud_checks'] += 1
            _metrics['request_log'].appendleft({
                'method':      method,
                'path':        path,
                'status':      status,
                'duration_ms': round(duration_ms, 2),
            })
            _metrics['response_times'].appendleft(duration_ms)
        return response
def get_metrics() -> dict:
    with _metrics_lock:
        times = list(_metrics['response_times'])
        avg_response = round(sum(times) / len(times), 2) if times else 0
        return {
            'total_requests':     _metrics['total_requests'],
            'total_errors':       _metrics['total_errors'],
            'total_checkins':     _metrics['total_checkins'],
            'total_analyses':     _metrics['total_analyses'],
            'total_fraud_checks': _metrics['total_fraud_checks'],
            'avg_response_ms':    avg_response,
            'recent_requests':    list(_metrics['request_log'])[:20],
        }
