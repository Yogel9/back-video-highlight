# Подключаем Celery при старте Django, чтобы использовались настройки из settings (в т.ч. Redis).
from .celery import app as celery_app

__all__ = ("celery_app",)
