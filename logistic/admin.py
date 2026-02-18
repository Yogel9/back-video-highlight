from django.contrib import admin

from .models import Headline, Task, Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    search_fields = ("title", "source_url")
    list_filter = ("status", "created_at")


@admin.register(Headline)
class HeadlineAdmin(admin.ModelAdmin):
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video",
        "status",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "created_at", "started_at", "finished_at")
    search_fields = ("video__title",)
