from django.contrib.auth.models import User

from apps.profiles.models import AdminProfile, EmployerProfile, StudentProfile
from apps.users.crypto import login_to_username
from apps.users.identity import (
    encrypt_display_name,
    set_encrypted_identity,
    store_encrypted_login,
)
from apps.users.models import UserProfile
from apps.users.preset_accounts import OLD_PRESET_USERNAMES, PRESET_ACCOUNTS


def load_preset_users():
    # Remove legacy plaintext + new digest usernames for old presets.
    digest_names = [login_to_username(name) for name in OLD_PRESET_USERNAMES]
    User.objects.filter(username__in=list(OLD_PRESET_USERNAMES) + digest_names).delete()
    User.objects.filter(email__in=OLD_PRESET_USERNAMES).delete()

    created = 0
    updated = 0

    for account in PRESET_ACCOUNTS:
        login = account["login"].strip()
        first_name = account["first_name"]
        last_name = account["last_name"]
        name = f"{last_name} {first_name}"
        role = account["role"]
        password_md5 = account["password_md5"]
        username = login_to_username(login)

        user, was_created = User.objects.get_or_create(username=username)
        set_encrypted_identity(
            user,
            login=login,
            first_name=first_name,
            last_name=last_name,
            password_md5=password_md5,
        )
        user.email = ""
        user.is_staff = role == "admin"
        user.is_superuser = role == "admin"
        user.save()

        profile_defaults = {"role": role, "email_verified": True}
        student_id = account.get("student_id") or None
        taken = UserProfile.objects.filter(student_id=student_id) if student_id else None
        if user.pk and taken is not None:
            taken = taken.exclude(user=user)
        if student_id and taken is not None and not taken.exists():
            profile_defaults["student_id"] = student_id

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults=profile_defaults,
        )
        profile.role = role
        profile.email_verified = True
        store_encrypted_login(profile, login)
        if student_id and not UserProfile.objects.filter(student_id=student_id).exclude(user=user).exists():
            profile.student_id = student_id
        profile.save()

        encrypted_name = encrypt_display_name(name)
        if role == "student":
            student_profile, _ = StudentProfile.objects.get_or_create(
                user=user, defaults={"name": encrypted_name}
            )
            if login == "Иванов_Иван":
                student_profile.name = encrypted_name
                student_profile.university = "Казахский национальный педагогический университет"
                student_profile.major = "История и география"
                student_profile.course = "3"
                student_profile.city = "Astana"
                student_profile.skills = [
                    "Педагогика",
                    "История",
                    "География",
                    "Методика преподавания",
                ]
                student_profile.about = (
                    "Студент педагогического направления, специализация история и география. "
                    "Интересуюсь школьным преподаванием, краеведением и цифровыми технологиями в образовании."
                )
                student_profile.save()
            elif login == "Демо_Алина":
                student_profile.name = encrypted_name
                student_profile.university = "Кокшетауский университет имени Ш. Уалиханова"
                student_profile.major = "Информационные системы"
                student_profile.course = "2"
                student_profile.city = "Kokshetau"
                student_profile.skills = [
                    "Python",
                    "SQL",
                    "Веб-разработка",
                    "Анализ данных",
                ]
                student_profile.about = (
                    "Тестовый студент IT-направления. Интересуюсь разработкой веб-приложений, "
                    "базами данных и применением ИИ в образовании."
                )
                student_profile.save()
            else:
                if not student_profile.name:
                    student_profile.name = encrypted_name
                    student_profile.save(update_fields=["name"])
        elif role == "employer":
            EmployerProfile.objects.get_or_create(
                user=user, defaults={"full_name": encrypted_name}
            )
        elif role == "admin":
            AdminProfile.objects.get_or_create(
                user=user, defaults={"full_name": encrypted_name}
            )

        if was_created:
            created += 1
        else:
            updated += 1

    try:
        from apps.vacancies.seed_data import load_demo_vacancies

        load_demo_vacancies()
    except Exception:
        pass

    return created, updated
