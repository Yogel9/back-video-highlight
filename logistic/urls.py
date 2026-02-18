from django.urls import path

from .views import VideoUploadView

urlpatterns = [
    path("videos/upload/", VideoUploadView.as_view(), name="video-upload"),
]
