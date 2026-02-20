import io
import os
import zipfile

from django.core.files.storage import default_storage
from django.db.models import Count
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers
from rest_framework.decorators import action, api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from logistic.models import ConfigTask
from main.models import Video, Highlight, HighlightFile
from main.serializers import (
    VideoSerializer,
    HighlightSerializer,
    HighlightBulkCreateItemSerializer,
    HighlightFileSerializer,
    HighlightFileUploadSerializer,
)
from logistic.service.video_uploader import (
    VideoUploader,
    ResourceNotFoundError,
    NotAVideoError,
)


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "message": "API работает корректно"})


class HighlightViewSet(ListAPIView):
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = next(
            (self.request.query_params[k] for k in self.request.query_params if k.lower() == "video_id"),
            None,
        )
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset


class HighlightFileZipView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        video_id = request.query_params.get("video_id")
        if not video_id:
            return Response(
                {"error": "Параметр video_id обязателен"},
                status=400,
            )

        video = get_object_or_404(Video, pk=video_id)
        highlight_files = HighlightFile.objects.filter(video=video)

        if not highlight_files.exists():
            return Response(
                {"error": "Нет файлов вырезок для этого видео"},
                status=404,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, hf in enumerate(highlight_files.order_by("created_at")):
                ext = os.path.splitext(hf.file.name)[1] or ".mp4"
                arcname = f"highlight_{i + 1}{ext}"
                with hf.file.open("rb") as f:
                    zf.writestr(arcname, f.read())

        buffer.seek(0)
        safe_title = "".join(
            c if c.isalnum() or c in " -_" else "_" for c in (video.title or f"video_{video_id}")
        )
        filename = f"highlights_{safe_title}_{video_id}.zip"
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class HighlightFileUploadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = HighlightFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = serializer.validated_data["task_id"]
        paths = serializer.validated_data["paths"]

        task = get_object_or_404(ConfigTask, pk=task_id)
        video = task.video

        created = []
        for path in paths:
            if not path or not default_storage.exists(path):
                continue
            filename = os.path.basename(path)
            with default_storage.open(path, "rb") as f:
                content = ContentFile(f.read(), name=filename)
                hf = HighlightFile.objects.create(video=video, file=content)
                created.append(hf)

        return Response(
            HighlightFileSerializer(created, many=True).data,
            status=201,
        )


class HighlightBulkCreateView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"error": "Ожидается массив объектов с полями task_id, event_type, time_start, description, confidence, time_duration"},
                status=400,
            )
        serializer = HighlightBulkCreateItemSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        highlights = []
        for item in serializer.validated_data:
            task_id_int = int(item["task_id"])
            task = get_object_or_404(ConfigTask, pk=task_id_int)
            video = task.video
            highlight = Highlight.objects.create(
                video=video,
                is_custom=bool(task.promt),
                event_type=item["event_type"],
                start_time=item["time_start"],
                end_time=item["time_start"] + item["time_duration"],
                description=item.get("description", "") or "",
                confidence=item["confidence"],
            )
        return Response(
            HighlightSerializer(highlights, many=True).data,
            status=201,
        )


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.annotate(highlights_count=Count("highlights"))
    serializer_class = VideoSerializer
    permission_classes = [permissions.AllowAny]

    def _download_video_from_url(self, source_url):
        uploader = VideoUploader(source_url, low_resolution=True)
        try:
            downloaded_path = uploader.upload()
            filename = os.path.basename(downloaded_path)
            with open(downloaded_path, "rb") as f:
                return ContentFile(f.read(), name=filename)
        finally:
            uploader.cleanup()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        source_url = validated_data.get("source_url")
        file_from_request = validated_data.get("file")

        if source_url and not file_from_request:
            try:
                file_obj = self._download_video_from_url(source_url)
                instance = serializer.save(file=file_obj)
            except ResourceNotFoundError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
            except NotAVideoError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
        else:
            instance = serializer.save()

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        source_url = validated_data.get("source_url")
        file_from_request = validated_data.get("file")
        instance = serializer.instance

        if source_url and not file_from_request and not instance.file:
            try:
                file_obj = self._download_video_from_url(source_url)
                instance = serializer.save(file=file_obj)
            except ResourceNotFoundError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
            except NotAVideoError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
        else:
            instance = serializer.save()

    @action(detail=True, methods=["get"], url_path="highlights/zip")
    def highlights_zip(self, request, pk=None):
        video = self.get_object()
        highlight_files = HighlightFile.objects.filter(video=video)

        if not highlight_files.exists():
            return Response(
                {"error": "Нет файлов вырезок для этого видео"},
                status=404,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, hf in enumerate(highlight_files.order_by("created_at")):
                ext = os.path.splitext(hf.file.name)[1] or ".mp4"
                arcname = f"highlight_{i + 1}{ext}"
                with hf.file.open("rb") as f:
                    zf.writestr(arcname, f.read())

        buffer.seek(0)
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in (video.title or f"video_{pk}"))
        filename = f"highlights_{safe_title}_{pk}.zip"
        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["get", "post"], url_path="promt")
    def custom_promt(self, request, pk=None):
        video = self.get_object()

        if request.method == "GET":
            from logistic.models import ConfigTask

            task_id = request.query_params.get("task_id")
            if not task_id:
                return Response(
                    {"error": "Параметр task_id обязателен"},
                    status=400,
                )
            task = get_object_or_404(ConfigTask, pk=task_id, video=video)
            return Response({
                "task_id": task.pk,
                "status": task.status,
                "promt": task.promt
            })

        # POST
        promt = request.data.get("promt")
        if not promt:
            return Response(
                {"error": "Поле promt обязательно"},
                status=400,
            )
        task_id = video.create_task(promt)
        return Response({"status": "ok", "task_id": task_id})


class VideoStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        video = get_object_or_404(Video, pk=pk)
        return Response({
            "id": video.pk,
            "status": video.status,
        })
