from django.db import migrations, models


def encrypt_existing_users(apps, schema_editor):
    # Import real crypto helpers (need SECRET_KEY + Fernet).
    from apps.users.crypto import (
        encrypt_password_hash,
        encrypt_value,
        is_encrypted,
        is_login_digest,
        login_to_username,
    )

    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("users", "UserProfile")
    StudentProfile = apps.get_model("profiles", "StudentProfile")
    EmployerProfile = apps.get_model("profiles", "EmployerProfile")
    AdminProfile = apps.get_model("profiles", "AdminProfile")

    for user in User.objects.all().iterator():
        plain_login = user.username
        if not is_login_digest(plain_login):
            user.username = login_to_username(plain_login)
        if user.first_name and not is_encrypted(user.first_name):
            user.first_name = encrypt_value(user.first_name)
        if user.last_name and not is_encrypted(user.last_name):
            user.last_name = encrypt_value(user.last_name)
        if user.password and not (
            user.password.startswith("unsalted_md5$") and is_encrypted(user.password.split("$", 1)[-1])
        ):
            from apps.users.hashers import format_encrypted_md5_password

            pwd = user.password
            if pwd.startswith("unsalted_md5$"):
                pwd = pwd.split("$", 1)[1]
            if pwd.startswith("md5$$"):
                pwd = pwd[5:]
            if is_encrypted(pwd):
                user.password = f"unsalted_md5${pwd}"
            elif len(pwd) == 32:
                user.password = format_encrypted_md5_password(pwd)
            else:
                user.password = format_encrypted_md5_password(
                    __import__("hashlib").md5(pwd.encode("utf-8")).hexdigest()
                )
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user_id=user.id)
        if not profile.login_encrypted and not is_login_digest(plain_login):
            profile.login_encrypted = encrypt_value(plain_login)
            profile.save(update_fields=["login_encrypted"])

    for model in (StudentProfile, EmployerProfile, AdminProfile):
        name_field = "name" if model is StudentProfile else "full_name"
        for row in model.objects.all().iterator():
            value = getattr(row, name_field) or ""
            if value and not is_encrypted(value):
                setattr(row, name_field, encrypt_value(value))
                row.save(update_fields=[name_field])

    # Re-seed presets with encrypted identity after column exists.
    from apps.users.services.preset_users import load_preset_users

    load_preset_users()


def noop_reverse(apps, schema_editor):
    # Irreversible without storing the previous SECRET_KEY mapping.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_student_id_help_text"),
        ("profiles", "0003_widen_encrypted_name_fields"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="login_encrypted",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Fernet-encrypted login (SECRET_KEY)",
            ),
        ),
        migrations.RunPython(encrypt_existing_users, noop_reverse),
    ]
