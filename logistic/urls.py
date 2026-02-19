from django.urls import path

from logistic.views import ConfigTaskStatusView

urlpatterns = [
    path(
        "tasks/<int:pk>/status/",
        ConfigTaskStatusView.as_view(),
        name="config-task-status",
    ),
]
