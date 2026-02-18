from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "file",
            "source_url",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "status"]


