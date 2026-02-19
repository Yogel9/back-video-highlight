from django.contrib import admin

from .models import ConfigTask


@admin.register(ConfigTask)
class ConfigTaskAdmin(admin.ModelAdmin):
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
