from django.db import models


# class Domain(models.Model):
#class Domain(models.TextChoices):
#    TRAFFIC = "traffic", "ДТП"
#    FACTORY = "factory", "Производство"
#    FIGHT = "fight", "Драки"


#    name = models.CharField(max_length=255)

class Video(models.Model):
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
        help_text="URL, для загрузки видео",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or f"Video #{self.pk}"
