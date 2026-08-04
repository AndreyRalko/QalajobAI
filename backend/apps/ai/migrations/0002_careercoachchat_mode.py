# Generated manually for CareerCoachChat.mode

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="careercoachchat",
            name="mode",
            field=models.CharField(
                choices=[
                    ("resume", "Resume"),
                    ("cover_letter", "Cover letter"),
                    ("interview", "Interview prep"),
                ],
                db_index=True,
                default="resume",
                max_length=32,
            ),
        ),
    ]
