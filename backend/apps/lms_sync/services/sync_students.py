import logging

from django.contrib.auth.models import User
from django.db import transaction

from apps.profiles.models import StudentProfile
from apps.users.identity import (
    encrypt_display_name,
    set_encrypted_identity,
    store_encrypted_login,
)
from apps.users.models import UserProfile, UserRole
from apps.users.crypto import login_to_username

from .mappers import map_student_row

logger = logging.getLogger(__name__)


def sync_students_from_rows(rows):
    created = 0
    updated = 0
    skipped = 0

    for row in rows:
        student = map_student_row(row)
        if not student:
            skipped += 1
            continue

        result = _upsert_student(student)
        if result is None:
            skipped += 1
        elif result:
            created += 1
        else:
            updated += 1

    return {
        "students_created": created,
        "students_updated": updated,
        "students_skipped": skipped,
    }


@transaction.atomic
def _upsert_student(student):
    student_id = student["student_id"]
    login = student["login"]
    name_parts = [
        student.get("last_name", ""),
        student.get("first_name", ""),
        student.get("patronymic", ""),
    ]
    full_name = " ".join(part for part in name_parts if part).strip() or login

    profile = (
        UserProfile.objects.select_related("user")
        .filter(student_id=student_id, role=UserRole.STUDENT)
        .first()
    )
    user = profile.user if profile else None

    if user is None:
        username = login_to_username(login)
        user = User.objects.filter(username=username).first()
        if user and hasattr(user, "profile") and user.profile.role != UserRole.STUDENT:
            logger.warning(
                "Skip student_id=%s: login belongs to role=%s",
                student_id,
                user.profile.role,
            )
            return None

    was_created = user is None
    if was_created:
        user = User()

    set_encrypted_identity(
        user,
        login=login,
        first_name=student["first_name"],
        last_name=student["last_name"],
        password_md5=student["password_md5"],
    )
    user.email = ""
    user.is_staff = False
    user.is_superuser = False
    user.save()

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": UserRole.STUDENT,
            "email_verified": True,
            "student_id": student_id,
        },
    )
    profile.role = UserRole.STUDENT
    profile.email_verified = True
    profile.student_id = student_id
    store_encrypted_login(profile, login)
    profile.save()

    student_profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={"name": encrypt_display_name(full_name)},
    )
    if not student_profile.name:
        student_profile.name = encrypt_display_name(full_name)
        student_profile.save(update_fields=["name"])
    else:
        # Keep FIO in sync with LMS on updates.
        student_profile.name = encrypt_display_name(full_name)
        student_profile.save(update_fields=["name"])

    return was_created
