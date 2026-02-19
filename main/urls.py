"""
Основной URL конфигуратор проекта.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    health_check,
    VideoViewSet,
    VideoStatusView,
    HighlightViewSet,
    HighlightBulkCreateView,
)

router = DefaultRouter()
router.register(r"video", VideoViewSet, basename="video")

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Health check
    path("api/health/", health_check, name="health-check"),
    
    # API документация
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # API видео
    path("api/", include(router.urls)),
    path(
        "api/video/<int:pk>/status/",
        VideoStatusView.as_view(),
        name="video-status",
    ),
    path(
        "api/highlights/",
        HighlightViewSet.as_view(),
        name="highlights",
    ),
    path(
        "api/highlights/bulk/",
        HighlightBulkCreateView.as_view(),
        name="highlight-bulk-create",
    ),
    
    # Таски (logistic)
    path("api/logistic/", include("logistic.urls")),
]
