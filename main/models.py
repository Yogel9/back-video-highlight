import os

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

class VideoStatus(models.TextChoices):
    NOT_PROCESSED = "not_processed", "Не обработан"
    DOWNLOADING = "downloading", "Идёт загрузка"
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
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Длительность видео в секундах",
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
    
    def create_task(self, promt=None):
        from logistic.models import ConfigTask
        return ConfigTask.objects.create(video=self, promt=promt).id


@receiver(post_save, sender=Video)
def first_standart_task(sender, instance, created, **kwargs):
    if created:
        instance.create_task()




class Highlight(models.Model):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="highlights",
        help_text="Видео, к которому относится хайлайт",
    )
    is_custom = models.BooleanField(
        default=False,
        help_text="Является ли хайлайт собственным промтом пользователя",
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
        verbose_name = "Хайлайт"
        verbose_name_plural = "Хайлайты"

    def __str__(self) -> str:
        return f"{self.video} [{self.start_time}-{self.end_time}]"
