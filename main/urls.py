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
from .views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Health check
    path("api/health/", health_check, name="health-check"),
    
    # API документация
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Подключение других приложений
    path("api/logistic/", include("logistic.urls")),
]
