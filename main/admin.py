import os

from django.contrib import admin
from django.contrib import messages
from django.core.files.base import ContentFile

from .models import Video, Highlight
from logistic.service.video_uploader import (
    VideoUploader,
    ResourceNotFoundError,
    NotAVideoError,
)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created_at")
    search_fields = ("title", "source_url")
    list_filter = ("status", "created_at")

    def save_model(self, request, obj, form, change):
        source_url = form.cleaned_data.get("source_url")
        has_file = bool(obj.file)

        if source_url and not has_file:
            try:
                uploader = VideoUploader(source_url, low_resolution=True)
                try:
                    downloaded_path = uploader.upload()
                    filename = os.path.basename(downloaded_path)
                    with open(downloaded_path, "rb") as f:
                        obj.file.save(filename, ContentFile(f.read()), save=False)
                finally:
                    uploader.cleanup()
            except ResourceNotFoundError as e:
                messages.error(request, f"Не удалось загрузить видео по URL: {e}")
                return
            except NotAVideoError as e:
                messages.error(request, f"Ошибка URL: {e}")
                return

        super().save_model(request, obj, form, change)


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
