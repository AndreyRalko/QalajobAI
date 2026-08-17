from django.db import migrations


def set_lms_student_id(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")
    try:
        user = User.objects.get(username="Иванов_Иван")
    except User.DoesNotExist:
        return
    UserProfile.objects.filter(user=user).update(student_id="48958")


def revert_student_id(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")
    try:
        user = User.objects.get(username="Иванов_Иван")
    except User.DoesNotExist:
        return
    UserProfile.objects.filter(user=user).update(student_id="STU-100001")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_preset_student_ids"),
    ]

    operations = [
        migrations.RunPython(set_lms_student_id, revert_student_id),
    ]
