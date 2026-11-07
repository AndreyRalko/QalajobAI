from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_adminprofile_employerprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentprofile",
            name="name",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="employerprofile",
            name="full_name",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name="adminprofile",
            name="full_name",
            field=models.CharField(blank=True, max_length=512),
        ),
    ]
