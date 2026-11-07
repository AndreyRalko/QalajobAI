"""Encrypt existing user identity fields in-place (SECRET_KEY / Fernet)."""

from __future__ import annotations

import hashlib
import re

from django.contrib.auth.models import User
from django.db import transaction

from apps.profiles.models import AdminProfile, EmployerProfile, StudentProfile
from apps.users.crypto import (
    encrypt_value,
    is_encrypted,
    is_login_digest,
    login_to_username,
)
from apps.users.hashers import format_encrypted_md5_password
from apps.users.identity import store_encrypted_login
from apps.users.models import UserProfile

_MD5_RE = re.compile(r"^[a-f0-9]{32}$")


def _normalize_password_payload(password: str) -> str:
    pwd = (password or "").strip()
    if pwd.startswith("unsalted_md5$"):
        pwd = pwd.split("$", 1)[1]
    if pwd.startswith("md5$$"):
        pwd = pwd[5:]
    return pwd


def _password_needs_encrypt(password: str) -> bool:
    pwd = password or ""
    if not pwd:
        return False
    if pwd.startswith("unsalted_md5$"):
        payload = pwd.split("$", 1)[1]
        return not is_encrypted(payload)
    if is_encrypted(pwd):
        return True  # missing hasher prefix
    return True


def _encrypt_password(password: str) -> str:
    payload = _normalize_password_payload(password)
    if is_encrypted(payload):
        return f"unsalted_md5${payload}"
    if _MD5_RE.fullmatch(payload.lower()):
        return format_encrypted_md5_password(payload.lower())
    # Unknown Django hash / plaintext — MD5 then encrypt (matches project hasher).
    md5_hex = hashlib.md5(payload.encode("utf-8")).hexdigest()
    return format_encrypted_md5_password(md5_hex)


def encrypt_existing_users(*, dry_run: bool = False) -> dict:
    """
    Encrypt login / password / FIO for all users and related profile name fields.

    Safe to re-run: already-encrypted values are left as-is.
    """
    stats = {
        "users_scanned": 0,
        "users_updated": 0,
        "logins_encrypted": 0,
        "passwords_encrypted": 0,
        "names_encrypted": 0,
        "profiles_login_encrypted": 0,
        "student_names_encrypted": 0,
        "employer_names_encrypted": 0,
        "admin_names_encrypted": 0,
    }

    for user in User.objects.all().iterator():
        stats["users_scanned"] += 1
        changed_fields: list[str] = []
        plain_login = user.username

        if not is_login_digest(user.username):
            user.username = login_to_username(plain_login)
            changed_fields.append("username")
            stats["logins_encrypted"] += 1
        else:
            plain_login = ""

        if user.first_name and not is_encrypted(user.first_name):
            user.first_name = encrypt_value(user.first_name)
            changed_fields.append("first_name")
            stats["names_encrypted"] += 1

        if user.last_name and not is_encrypted(user.last_name):
            user.last_name = encrypt_value(user.last_name)
            changed_fields.append("last_name")
            stats["names_encrypted"] += 1

        if _password_needs_encrypt(user.password):
            user.password = _encrypt_password(user.password)
            changed_fields.append("password")
            stats["passwords_encrypted"] += 1

        if changed_fields and not dry_run:
            with transaction.atomic():
                user.save(update_fields=changed_fields)
            stats["users_updated"] += 1
        elif changed_fields:
            stats["users_updated"] += 1

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if plain_login and not profile.login_encrypted:
            if not dry_run:
                store_encrypted_login(profile, plain_login)
                profile.save(update_fields=["login_encrypted"])
            stats["profiles_login_encrypted"] += 1
        elif (
            plain_login
            and profile.login_encrypted
            and not is_encrypted(profile.login_encrypted)
        ):
            if not dry_run:
                store_encrypted_login(profile, profile.login_encrypted)
                profile.save(update_fields=["login_encrypted"])
            stats["profiles_login_encrypted"] += 1

    for model, field, key in (
        (StudentProfile, "name", "student_names_encrypted"),
        (EmployerProfile, "full_name", "employer_names_encrypted"),
        (AdminProfile, "full_name", "admin_names_encrypted"),
    ):
        for row in model.objects.all().iterator():
            value = getattr(row, field) or ""
            if value and not is_encrypted(value):
                if not dry_run:
                    setattr(row, field, encrypt_value(value))
                    row.save(update_fields=[field])
                stats[key] += 1
                stats["names_encrypted"] += 1

    return stats
