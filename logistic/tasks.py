from typing import Any, Dict, Optional

from celery import shared_task

from .models import Task


@shared_task(queue="ml")
def run_ml_task(task_id: int, extra_payload: Optional[Dict[str, Any]] = None) -> None:
    task = Task.objects.get(pk=task_id)
    task.start(extra_payload=extra_payload)

