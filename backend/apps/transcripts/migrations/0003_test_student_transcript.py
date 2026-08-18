from django.db import migrations


def load_rows(apps, schema_editor):
    from apps.transcripts.seed_data import TEST_STUDENT_ID, load_lms_transcript

    load_lms_transcript(TEST_STUDENT_ID)


def unload_rows(apps, schema_editor):
    from apps.transcripts.seed_data import TEST_STUDENT_ID

    Transcript = apps.get_model("transcripts", "Transcript")
    Transcript.objects.filter(student_id=TEST_STUDENT_ID).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("transcripts", "0002_load_lms_transcript"),
        ("users", "0008_test_student_alieva"),
    ]

    operations = [
        migrations.RunPython(load_rows, unload_rows),
    ]
