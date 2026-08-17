from django.db import migrations


def load_presets(apps, schema_editor):
    from apps.users.preset_accounts import PRESET_ACCOUNTS

    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")
    StudentProfile = apps.get_model("profiles", "StudentProfile")
    EmployerProfile = apps.get_model("profiles", "EmployerProfile")
    AdminProfile = apps.get_model("profiles", "AdminProfile")

    for account in PRESET_ACCOUNTS:
        login = account["login"].strip()
        first_name = account["first_name"]
        last_name = account["last_name"]
        name = f"{last_name} {first_name}"
        role = account["role"]

        user, _ = User.objects.get_or_create(
            username=login,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": role == "admin",
                "is_superuser": role == "admin",
                "password": account["password_md5"],
            },
        )
        user.first_name = first_name
        user.last_name = last_name
        user.email = ""
        user.is_staff = role == "admin"
        user.is_superuser = role == "admin"
        user.password = account["password_md5"]
        user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": role, "email_verified": True},
        )
        profile.role = role
        profile.email_verified = True
        profile.save()

        if role == "student":
            StudentProfile.objects.get_or_create(user=user, defaults={"name": name})
        elif role == "employer":
            EmployerProfile.objects.get_or_create(user=user, defaults={"full_name": name})
        elif role == "admin":
            AdminProfile.objects.get_or_create(user=user, defaults={"full_name": name})


def unload_presets(apps, schema_editor):
    from apps.users.preset_accounts import PRESET_ACCOUNTS

    User = apps.get_model("auth", "User")
    logins = [account["login"].strip() for account in PRESET_ACCOUNTS]
    User.objects.filter(username__in=logins).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_emailverificationtoken_loginhistory_and_more"),
        ("profiles", "0002_adminprofile_employerprofile"),
    ]

    operations = [
        migrations.RunPython(load_presets, unload_presets),
    ]
