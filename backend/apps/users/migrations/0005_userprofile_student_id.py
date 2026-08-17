from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_load_preset_users"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="student_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="LMS StudentID used to load academic transcript",
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
    ]
