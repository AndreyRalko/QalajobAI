from django.db import migrations


def load_test_student(apps, schema_editor):
    # Preset accounts (including Демо_Алина) are seeded/encrypted in 0010.
    # Avoid calling live load_preset_users() here — it expects login_encrypted.
    pass


def unload_test_student(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(username="Демо_Алина").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_demo_student_id_48958"),
    ]

    operations = [
        migrations.RunPython(load_test_student, unload_test_student),
    ]
