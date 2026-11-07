"""Field encryption for user login / password / FIO using Django SECRET_KEY."""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging

from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

LOGIN_USERNAME_PREFIX = "u$"
_FERNET = None


def _fernet() -> Fernet:
    global _FERNET
    if _FERNET is None:
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        _FERNET = Fernet(base64.urlsafe_b64encode(digest))
    return _FERNET


def reset_crypto_cache():
    """Test helper: drop cached Fernet after SECRET_KEY override."""
    global _FERNET
    _FERNET = None


def is_encrypted(value: str | None) -> bool:
    if not value:
        return False
    return value.startswith("gAAAAA")


def is_login_digest(username: str | None) -> bool:
    return bool(username) and username.startswith(LOGIN_USERNAME_PREFIX)


def normalize_login(login: str) -> str:
    return (login or "").strip()


def login_to_username(login: str) -> str:
    """Deterministic auth username (HMAC). Not reversible without brute force."""
    normalized = normalize_login(login)
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        normalized.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{LOGIN_USERNAME_PREFIX}{digest}"


def encrypt_value(plain: str | None) -> str:
    if plain is None or plain == "":
        return ""
    if is_encrypted(plain):
        return plain
    return _fernet().encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_value(token: str | None) -> str:
    if token is None or token == "":
        return ""
    if not is_encrypted(token):
        return token
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError) as exc:
        logger.warning("Failed to decrypt field: %s", exc)
        return ""


def encrypt_password_hash(password_md5: str) -> str:
    return encrypt_value((password_md5 or "").strip().lower())


def decrypt_password_hash(stored: str) -> str:
    return decrypt_value(stored).strip().lower()
