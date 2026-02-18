from django.db import models


# class Domain(models.Model):
#    name = models.CharField(max_length=255)

class Video(models.Model):

    class Domain(models.TextChoices):
        TRAFFIC = "traffic", "ДТП"
        FACTORY = "factory", "Производство"
        FIGHT = "fight", "Драки"

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Название видео",
    )
    file = models.FileField(
        upload_to="videos/",
        help_text="Загружаемый файл",
    )
    source_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL, по которому можно скачать видео (альтернатива прямой загрузке файла).",
    )
    domain = models.CharField(
        max_length=32,
        choices=Domain.choices,
        help_text="Домен",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = getattr(self.file, "name", "") or ""
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title or self.original_filename or f"Video #{self.pk}"
