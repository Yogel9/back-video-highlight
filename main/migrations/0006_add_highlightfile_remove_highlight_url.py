# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_highlight_is_custom"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="highlight",
            name="highlight",
        ),
        migrations.CreateModel(
            name="HighlightFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(help_text="Файл вырезки", upload_to="highlights/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "video",
                    models.ForeignKey(
                        help_text="Видео, к которому относится вырезка",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="highlight_files",
                        to="main.video",
                    ),
                ),
            ],
            options={
                "verbose_name": "Файл вырезки",
                "verbose_name_plural": "Файлы вырезок",
                "ordering": ["-created_at"],
            },
        ),
    ]
