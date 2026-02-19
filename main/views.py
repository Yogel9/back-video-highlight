import os

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from main.models import Video, Headline
from logistic.serializers import VideoSerializer, HeadlineSerializer
from logistic.service.video_uploader import (
    VideoUploader,
    ResourceNotFoundError,
    NotAVideoError,
)


@api_view(["GET"])
def health_check(request):
    """
    Проверка работоспособности API.
    """
    return Response({"status": "ok", "message": "API работает корректно"})


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


class VideoStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        video = get_object_or_404(Video, pk=pk)
        return Response({
            "id": video.pk,
            "status": video.status,
        })
