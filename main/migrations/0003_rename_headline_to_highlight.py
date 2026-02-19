# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_video_download_error_video_duration_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Headline',
            new_name='Highlight',
        ),
    ]
