from django.db import migrations


def update_student_ids(apps, schema_editor):
    from apps.users.preset_accounts import PRESET_ACCOUNTS

    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")

    for account in PRESET_ACCOUNTS:
        login = account["login"].strip()
        student_id = account.get("student_id") or None
        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            continue
        UserProfile.objects.filter(user=user).update(student_id=student_id)


def clear_student_ids(apps, schema_editor):
    from apps.users.preset_accounts import PRESET_ACCOUNTS

    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")
    logins = [account["login"].strip() for account in PRESET_ACCOUNTS]
    UserProfile.objects.filter(user__username__in=logins).update(student_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_userprofile_student_id"),
    ]

    operations = [
        migrations.RunPython(update_student_ids, clear_student_ids),
    ]
