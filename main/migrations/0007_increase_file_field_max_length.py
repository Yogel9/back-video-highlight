from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_add_highlightfile_remove_highlight_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="file",
            field=models.FileField(blank=True, help_text="Загружаемый файл", max_length=255, upload_to="videos/"),
        ),
        migrations.AlterField(
            model_name="highlightfile",
            name="file",
            field=models.FileField(help_text="Файл вырезки", max_length=255, upload_to="highlights/"),
        ),
    ]
