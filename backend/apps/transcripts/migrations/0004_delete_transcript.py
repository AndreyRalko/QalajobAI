from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transcripts", "0003_test_student_transcript"),
    ]

    operations = [
        migrations.DeleteModel(name="Transcript"),
    ]
