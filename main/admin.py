from django.contrib import admin

from .models import Video, Highlight


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    search_fields = ("title", "source_url")
    list_filter = ("status", "created_at")


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "event_type",
        "start_time",
        "end_time",
        "confidence",
        "created_at",
    )
    list_filter = ("event_type", "created_at")
    search_fields = ("description", "video__title")
