import logging

from django.db import models

from .service.video_uploader import VideoUploader

logger = logging.getLogger(__name__)

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
        if self.source_url and not self.file:
            uploader = VideoUploader(self.source_url)
            uploaded_file = uploader.upload()
            if uploaded_file is not None:
                self.file = uploaded_file
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


class TaskStatus(models.TextChoices):
    PENDING = "pending", "Ожидает запуска"
    RUNNING = "running", "Выполняется"
    SUCCESS = "success", "Успешно завершено"
    FAILED = "failed", "Завершено с ошибкой"


class ConfigTask(models.Model):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Видео",
    )
    status = models.CharField(
        max_length=32,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        help_text="Статус выполнения задания",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Ответ от ML-сервиса",
    )
    error_message = models.TextField(
        blank=True,
        help_text="Текст ошибки",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Задание"
        verbose_name_plural = "Задания"

    def __str__(self) -> str:
        return f"Задание #{self.pk} для {self.video}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            try:
                from .tasks import run_ml_task
                run_ml_task.apply_async(args=[self.pk])
            except Exception as e:
                logger.warning(
                    "Не удалось поставить задачу ML в очередь (брокер недоступен?). "
                    "Задание #%s сохранено, задачу можно запустить вручную. Ошибка: %s",
                    self.pk,
                    e,
                    exc_info=True,
                )

    def start(self, extra_payload=None) -> None:
        from django.conf import settings
        from django.utils import timezone

        from .service.ml_adapter import MLAdapter

        if self.status != TaskStatus.PENDING:
            return

        self.status = TaskStatus.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

        api_url = getattr(settings, "ML_API_URL", None)
        if not api_url:
            self.status = TaskStatus.FAILED
            self.error_message = "ML_API_URL не настроен в settings"
            self.finished_at = timezone.now()
            self.save(update_fields=["status", "error_message", "finished_at"])
            return

        file_url = self.video.file.url if self.video.file else ""
        adapter = MLAdapter(api_url=api_url)

        try:
            response = adapter.send_request(
                minio_file_url=file_url,
                extra_payload=extra_payload,
            )
            self.result = response
            self.status = TaskStatus.SUCCESS
        except Exception as exc:  # noqa: BLE001
            self.error_message = str(exc)
            self.status = TaskStatus.FAILED
        finally:
            self.finished_at = timezone.now()
            self.save(
                update_fields=[
                    "status",
                    "finished_at",
                    "result",
                    "error_message",
                ]
            )
