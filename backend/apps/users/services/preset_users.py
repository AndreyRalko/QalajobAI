from django.contrib.auth.models import User

from apps.profiles.models import AdminProfile, EmployerProfile, StudentProfile
from apps.users.models import UserProfile
from apps.users.preset_accounts import OLD_PRESET_USERNAMES, PRESET_ACCOUNTS


def load_preset_users():
    User.objects.filter(username__in=OLD_PRESET_USERNAMES).delete()
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

        user, was_created = User.objects.get_or_create(
            username=login,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": role == "admin",
                "is_superuser": role == "admin",
            },
        )

        user.first_name = first_name
        user.last_name = last_name
        user.email = ""
        user.is_staff = role == "admin"
        user.is_superuser = role == "admin"
        user.password = password_md5
        user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": role, "email_verified": True},
        )
        profile.role = role
        profile.email_verified = True
        profile.student_id = account.get("student_id") or None
        profile.save()

        if role == "student":
            student_profile, _ = StudentProfile.objects.get_or_create(
                user=user, defaults={"name": name}
            )
            if login == "Иванов_Иван":
                student_profile.name = name
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
        elif role == "employer":
            EmployerProfile.objects.get_or_create(user=user, defaults={"full_name": name})
        elif role == "admin":
            AdminProfile.objects.get_or_create(user=user, defaults={"full_name": name})

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
