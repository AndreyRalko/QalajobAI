from django.db import migrations


def load_rows(apps, schema_editor):
    from apps.transcripts.seed_data import load_lms_transcript

    load_lms_transcript()


def unload_rows(apps, schema_editor):
    from apps.transcripts.seed_data import STUDENT_ID

    Transcript = apps.get_model("transcripts", "Transcript")
    Transcript.objects.filter(student_id=STUDENT_ID).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("transcripts", "0001_transcript_lms_schema"),
    ]

    operations = [
        migrations.RunPython(load_rows, unload_rows),
    ]
