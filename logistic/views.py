from pathlib import Path
from urllib.parse import urlparse

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from .models import Video, Headline
from .serializers import VideoSerializer, HeadlineSerializer


class HeadlineViewSet(ListAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.request.query_params.get("video_id")
        if video_id is not None:
            queryset = queryset.filter(video_id=video_id)
        return queryset

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.AllowAny]


class VideoStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        video = get_object_or_404(Video, pk=pk)
        return Response({"id": video.pk, "status": video.status})


class VideoDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        file_param = request.query_params.get("file")
        if not file_param:
            return Response(
                {"detail": "Параметр 'file' обязателен."},
                status=400,
            )

        storage_path = self._get_storage_path(file_param)

        if not default_storage.exists(storage_path):
            raise Http404("Файл не найден.")

        file_obj = default_storage.open(storage_path, "rb")
        filename = Path(storage_path).name

        return FileResponse(
            file_obj,
            as_attachment=True,
            filename=filename,
        )

    @staticmethod
    def _get_storage_path(file_param: str) -> str:
        parsed = urlparse(file_param)

        # Если прилетел полный URL, парсим путь и отрезаем имя бакета
        if parsed.scheme and parsed.netloc:
            path = parsed.path.lstrip("/")  # например: "video/videos/xxx.mp4"
            bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
            if bucket_name and path.startswith(bucket_name + "/"):
                return path[len(bucket_name) + 1 :]
            return path

        # Если прилетело просто имя файла / относительный путь
        return file_param.lstrip("/")
