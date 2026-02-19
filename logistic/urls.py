from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    VideoViewSet,
    VideoStatusView,
    HeadlineViewSet,
)

router = DefaultRouter()
router.register(r"video", VideoViewSet, basename="video")

urlpatterns = [
    path(
        "video/<int:pk>/status/",
        VideoStatusView.as_view(),
        name="video-status",
    ),
    # path(
    #     "videos/download/",
    #     VideoDownloadView.as_view(),
    #     name="video-download",
    # ),
    path(
        "headlines/",
        HeadlineViewSet.as_view(),
        name="headlines",
    ),
]

urlpatterns += router.urls
