from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import Video, Headline
from .serializers import VideoSerializer, HeadlineSerializer


class HeadlineViewSet(ListAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer
    permission_classes = [permissions.AllowAny]

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.AllowAny]


class VideoStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        video = get_object_or_404(Video, pk=pk)
        return Response({"id": video.pk, "status": video.status})
