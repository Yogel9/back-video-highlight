import time
from typing import Any, Dict, Optional

from django.utils import timezone

from celery import shared_task

from .models import ConfigTask, TaskStatus

TIMEOUT_SECONDS = 600  # 10 минут


@shared_task(queue="ml")
def run_ml_task(task_id: int, extra_payload: Optional[Dict[str, Any]] = None) -> None:
    task = ConfigTask.objects.get(pk=task_id)
    task.start(extra_payload=extra_payload)

    start_time = time.monotonic()
    while task.status not in (TaskStatus.SUCCESS, TaskStatus.FAILED):
        if time.monotonic() - start_time >= TIMEOUT_SECONDS:
            task.status = TaskStatus.FAILED
            task.error_message = "Timeout: задача не завершилась за 10 минут"
            task.finished_at = timezone.now()
            task.save(update_fields=["status", "error_message", "finished_at"])
            return
        time.sleep(1)
        task.refresh_from_db()

