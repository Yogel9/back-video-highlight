import logging

from django.db import models

from main.models import Video

logger = logging.getLogger(__name__)


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
                    f"Не удалось поставить задачу ML в очередь (брокер недоступен). ",
                    f"Ошибка: {e}"
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

        video_filename = f"/{self.video.file.name}" if self.video.file else ""
        if not video_filename:
            self.status = TaskStatus.FAILED
            self.error_message = "У видео нет загруженного файла"
            self.finished_at = timezone.now()
            self.save(update_fields=["status", "error_message", "finished_at"])
            return

        adapter = MLAdapter(api_url=api_url)
        try:
            response = adapter.send_request(
                task_id=str(self.pk),
                video_filename=video_filename,
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
