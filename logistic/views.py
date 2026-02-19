from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from logistic.models import ConfigTask, TaskStatus


class ConfigTaskStatusView(APIView):
    """
    Обновление статуса ConfigTask по id.
    Позволяет ML-сервису отправить результат обработки.
    """

    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk):
        task = ConfigTask.objects.filter(pk=pk).first()
        if not task:
            return Response({"error": "Задание не найдено"}, status=404)

        valid_statuses = [c[0] for c in TaskStatus.choices]
        new_status = request.data.get("status")
        if not new_status or new_status not in valid_statuses:
            return Response(
                {"error": f"Недопустимый статус. Допустимые: {valid_statuses}"},
                status=400,
            )

        update_fields = ["status"]
        task.status = new_status

        if new_status in (TaskStatus.SUCCESS, TaskStatus.FAILED):
            task.finished_at = timezone.now()
            update_fields.append("finished_at")

            if new_status == TaskStatus.SUCCESS and "result" in request.data:
                task.result = request.data.get("result")
                update_fields.append("result")
            if new_status == TaskStatus.FAILED and "error_message" in request.data:
                task.error_message = request.data.get("error_message", "")
                update_fields.append("error_message")

        task.save(update_fields=update_fields)

        return Response({"id": task.pk, "status": task.status})
