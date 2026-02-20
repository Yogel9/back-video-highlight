# Serializers для основного приложения

from rest_framework import serializers

from logistic.utils import get_public_media_url
from main.models import Video, Highlight, HighlightFile


class VideoSerializer(serializers.ModelSerializer):
    highlights_count = serializers.SerializerMethodField()

    def get_highlights_count(self, instance):
        return instance.highlights.count() if hasattr(instance, "highlights") else 0

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
            "highlights_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "status", "duration", "highlights_count"]


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = [
            "id",
            "video",
            "event_type",
            "start_time",
            "end_time",
            "confidence",
            "description",
            "created_at",
            "is_custom",
        ]
        read_only_fields = ["id", "created_at"]


class HighlightFileSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file and data.get("file"):
            data["file"] = get_public_media_url(instance.file.url)
        return data

    class Meta:
        model = HighlightFile
        fields = ["id", "video", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class HighlightFileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов вырезок по путям."""

    task_id = serializers.IntegerField()
    paths = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
    )


class HighlightBulkCreateItemSerializer(serializers.Serializer):
    """Сериализатор для элемента входящего массива при массовом создании хайлайтов."""

    task_id = serializers.CharField()
    event_type = serializers.CharField(max_length=32)
    time_start = serializers.IntegerField(min_value=0)
    description = serializers.CharField(allow_blank=True, default="")
    confidence = serializers.FloatField()
    time_duration = serializers.IntegerField(min_value=0)

    def to_internal_value(self, data):
        # Поддержка строковых значений (парсим числа)
        if isinstance(data.get("time_start"), str):
            data = data.copy()
            try:
                data["time_start"] = int(data["time_start"])
            except ValueError:
                data["time_start"] = int(float(data["time_start"]))
        if isinstance(data.get("time_duration"), str):
            data = data.copy()
            try:
                data["time_duration"] = int(data["time_duration"])
            except ValueError:
                data["time_duration"] = int(float(data["time_duration"]))
        if isinstance(data.get("confidence"), str):
            data = data.copy()
            data["confidence"] = float(data["confidence"])
        return super().to_internal_value(data)
