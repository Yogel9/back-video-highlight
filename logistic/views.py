from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer


class VideoUploadView(CreateAPIView):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.AllowAny]
