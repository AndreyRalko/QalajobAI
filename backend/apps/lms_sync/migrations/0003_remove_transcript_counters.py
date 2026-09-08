from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lms_sync", "0002_lmssyncschedule"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lmssynclog",
            name="transcripts_created",
        ),
        migrations.RemoveField(
            model_name="lmssynclog",
            name="transcripts_updated",
        ),
    ]
