from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel — useful for debugging data
    path('admin/', admin.site.urls),

    # Our API routes — each app gets its own prefix
    path('api/auth/', include('accounts.urls')),
    # We'll add more apps here as we build them:
    path('api/visits/', include('visits.urls')),
    path('api/visits/', include('outlets.urls')),
    path('api/fraud/',  include('fraud.urls')),   # ← add this
    # path('api/fraud/', include('fraud.urls')),
    # path('api/analysis/', include('analysis.urls')),
    # path('api/chat/', include('chat.urls')),
]

# Serve uploaded media files in development
# In production, a real web server (nginx) handles this
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)