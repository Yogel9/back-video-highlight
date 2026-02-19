from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from main.models import Video, Headline
from logistic.serializers import VideoSerializer, HeadlineSerializer


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


class VideoStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        video = get_object_or_404(Video, pk=pk)
        return Response({"id": video.pk, "status": video.status})
