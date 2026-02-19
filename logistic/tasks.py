import time
from typing import Any, Dict, Optional

from celery import shared_task

from .models import ConfigTask, TaskStatus


@shared_task(queue="ml")
def run_ml_task(task_id: int, extra_payload: Optional[Dict[str, Any]] = None) -> None:
    task = ConfigTask.objects.get(pk=task_id)
    task.start(extra_payload=extra_payload)

    while task.status not in (TaskStatus.SUCCESS, TaskStatus.FAILED):
        time.sleep(1)
        task.refresh_from_db()

