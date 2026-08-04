# Generated manually for CareerCoachChat.mode mock_interview

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0002_careercoachchat_mode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="careercoachchat",
            name="mode",
            field=models.CharField(
                choices=[
                    ("resume", "Resume"),
                    ("cover_letter", "Cover letter"),
                    ("interview", "Interview prep"),
                    ("mock_interview", "Mock interview"),
                ],
                db_index=True,
                default="resume",
                max_length=32,
            ),
        ),
    ]
