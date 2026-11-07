"""Read/write helpers for encrypted user identity fields."""

from __future__ import annotations

from django.contrib.auth.models import User

from apps.users.crypto import (
    decrypt_value,
    encrypt_value,
    is_login_digest,
    login_to_username,
    normalize_login,
)
from apps.users.hashers import format_encrypted_md5_password


def set_encrypted_identity(
    user: User,
    *,
    login: str,
    first_name: str = "",
    last_name: str = "",
    password_md5: str | None = None,
):
    plain_login = normalize_login(login)
    user.username = login_to_username(plain_login)
    user.first_name = encrypt_value(first_name or "")
    user.last_name = encrypt_value(last_name or "")
    if password_md5 is not None:
        user.password = format_encrypted_md5_password(password_md5)


def store_encrypted_login(profile, login: str):
    profile.login_encrypted = encrypt_value(normalize_login(login))


def get_user_login(user: User) -> str:
    profile = getattr(user, "profile", None)
    encrypted = getattr(profile, "login_encrypted", "") if profile else ""
    if encrypted:
        return decrypt_value(encrypted)
    if is_login_digest(user.username):
        return ""
    return user.username or ""


def get_user_first_name(user: User) -> str:
    return decrypt_value(user.first_name)


def get_user_last_name(user: User) -> str:
    return decrypt_value(user.last_name)


def get_user_full_name(user: User) -> str:
    parts = [get_user_last_name(user), get_user_first_name(user)]
    return " ".join(part for part in parts if part).strip()


def encrypt_display_name(name: str) -> str:
    return encrypt_value(name or "")


def decrypt_display_name(name: str) -> str:
    return decrypt_value(name or "")
