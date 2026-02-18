from rest_framework import serializers

from .models import Video, Headline


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

