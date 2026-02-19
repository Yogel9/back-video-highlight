import os

from django.db import models


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
        blank=True,
    )
    source_url = models.CharField(
        max_length=1024,
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
        verbose_name = "Видео"
        verbose_name_plural = "Видео"

    def __str__(self) -> str:
        return self.title or f"Video #{self.pk}"

    def save(self, *args, **kwargs):
        if self.file and not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)


class Headline(models.Model):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="headlines",
        help_text="Видео, к которому относится хедлайн",
    )
    event_type = models.CharField(
        max_length=32,
        help_text='Категория события',
    )
    start_time = models.PositiveIntegerField(
        help_text="Начало события в секундах от начала видео",
    )
    end_time = models.PositiveIntegerField(
        help_text="Конец события в секундах от начала видео",
    )
    confidence = models.FloatField(
        help_text="Уверенность",
    )
    description = models.TextField(
        blank=True,
        help_text="Краткое текстовое описание события",
    )
    highlight = models.URLField(
        max_length=500,
        blank=True,
        help_text="Ссылка на вырезку/плейлист/диапазон",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Хедлайн"
        verbose_name_plural = "Хедлайны"

    def __str__(self) -> str:
        return f"{self.video} [{self.start_time}-{self.end_time}]"
