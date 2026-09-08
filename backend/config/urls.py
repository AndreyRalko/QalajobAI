from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({"status": "ok", "service": "qalajob-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path(
        "api/v1/",
        include(
            [
                path("", include("apps.users.urls")),
                path("", include("apps.profiles.urls")),
                path("", include("apps.companies.urls")),
                path("", include("apps.vacancies.urls")),
                path("", include("apps.resumes.urls")),
                path("", include("apps.saved_jobs.urls")),
                path("", include("apps.notifications.urls")),
                path("", include("apps.applications.urls")),
                path("subscriptions/", include("apps.subscriptions.urls")),
                path("payments/", include("apps.payments.urls")),
                path("admin-api/", include("apps.admin_api.urls")),
                path("ai/", include("apps.ai.urls")),
                path("messaging/", include("apps.messaging.urls")),
                path("analytics/", include("apps.analytics.urls")),
                path("audit/", include("apps.audit.urls")),
            ]
        ),
    ),
]

if getattr(settings, "ENABLE_API_DOCS", settings.DEBUG):
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
