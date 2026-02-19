from rest_framework import serializers

from logistic.utils import get_public_media_url
from main.models import Video, Headline


class VideoSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file and data.get("file"):
            data["file"] = get_public_media_url(instance.file.url)
        return data

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "file",
            "source_url",
            "status",
            "duration",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "status", "duration"]


class HeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headline
        fields = [
            "id",
            "video",
            "event_type",
            "start_time",
            "end_time",
            "confidence",
            "description",
            "highlight",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

