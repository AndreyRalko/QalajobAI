# Generated manually for hybrid LLM provider field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0004_aiactionlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="aiactionlog",
            name="provider",
            field=models.CharField(blank=True, db_index=True, max_length=16),
        ),
    ]
