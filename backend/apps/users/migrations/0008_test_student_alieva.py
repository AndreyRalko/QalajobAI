from django.db import migrations


def load_test_student(apps, schema_editor):
    from apps.users.services.preset_users import load_preset_users

    load_preset_users()


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
