from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "service",
            "file",
            "source_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


