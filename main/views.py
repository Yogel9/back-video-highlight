import os

from django.db.models import Count
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers
from rest_framework.decorators import action, api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from logistic.models import ConfigTask
from main.models import Video, Highlight
from main.serializers import (
    VideoSerializer,
    HighlightSerializer,
    HighlightBulkCreateItemSerializer,
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
            highlights.append(highlight)
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
                serializer.save(file=file_obj)
            except ResourceNotFoundError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
            except NotAVideoError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
        else:
            serializer.save()

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        source_url = validated_data.get("source_url")
        file_from_request = validated_data.get("file")
        instance = serializer.instance

        if source_url and not file_from_request and not instance.file:
            try:
                file_obj = self._download_video_from_url(source_url)
                serializer.save(file=file_obj)
            except ResourceNotFoundError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
            except NotAVideoError as e:
                raise serializers.ValidationError({"source_url": str(e)}) from e
        else:
            serializer.save()

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
