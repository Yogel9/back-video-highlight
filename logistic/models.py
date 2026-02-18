from django.db import models


# class Domain(models.Model):
#class Domain(models.TextChoices):
#    TRAFFIC = "traffic", "ДТП"
#    FACTORY = "factory", "Производство"
#    FIGHT = "fight", "Драки"


#    name = models.CharField(max_length=255)


class VideoStatus(models.TextChoices):
    NOT_PROCESSED = "not_processed", "Не обработан"
    PROCESSING = "processing", "В обработке"
    PROCESSED = "processed", "Обработан"


class Video(models.Model):
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Название видео",
    )
    file = models.FileField(
        upload_to="videos/",
        help_text="Загружаемый файл",
    )
    source_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL, для загрузки видео",
    )
    status = models.CharField(
        max_length=32,
        choices=VideoStatus.choices,
        default=VideoStatus.NOT_PROCESSED,
        help_text="Статус обработки видео",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or f"Video #{self.pk}"
