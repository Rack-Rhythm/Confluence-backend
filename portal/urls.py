import time
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from apps.users.urls import auth_urlpatterns, user_urlpatterns

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "confluence-backend",
        "timestamp": int(time.time()),
    }, status=200)

urlpatterns = [
    path('', health_check, name='root-health'),
    path('healthz/', health_check, name='healthz'),
    path('api/health/', health_check, name='api-health'),
    path('admin/', admin.site.urls),
    path('api/auth/', include(auth_urlpatterns)),
    path('api/users/', include(user_urlpatterns)),
    path('api/issues/', include('apps.issues.urls')),
    path('api/pitches/', include('apps.pitches.urls')),
    path('api/engagements/', include('apps.engagements.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
