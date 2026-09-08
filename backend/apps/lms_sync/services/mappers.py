import re

_STUDENT_ID_KEYS = ("student_id", "studentid")
_LOGIN_KEYS = ("login",)
_LAST_NAME_KEYS = ("last_name", "lastname", "surname", "familiya")
_FIRST_NAME_KEYS = ("first_name", "firstname", "name", "imya")
_PATRONYMIC_KEYS = ("patronymic", "middlename", "middle_name", "otchestvo")
_PASSWORD_KEYS = ("password_md5", "password", "passwd", "pass")


def _normalize_key(key):
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _pick(row, aliases):
    normalized = {_normalize_key(key): value for key, value in row.items()}
    for alias in aliases:
        value = normalized.get(_normalize_key(alias))
        if value is not None and value != "":
            return value
    return None


def _as_str(value):
    if value is None:
        return ""
    return str(value).strip()


def _as_student_id(value):
    if value is None:
        return None
    return str(value).strip()


def map_student_row(row):
    student_id = _as_student_id(_pick(row, _STUDENT_ID_KEYS))
    login = _as_str(_pick(row, _LOGIN_KEYS))[:150]
    last_name = _as_str(_pick(row, _LAST_NAME_KEYS))
    first_name = _as_str(_pick(row, _FIRST_NAME_KEYS))
    patronymic = _as_str(_pick(row, _PATRONYMIC_KEYS))
    password_md5 = _as_str(_pick(row, _PASSWORD_KEYS)).lower()

    if not student_id or not login or not password_md5:
        return None

    if len(password_md5) != 32 or not re.fullmatch(r"[a-f0-9]{32}", password_md5):
        return None

    return {
        "student_id": student_id,
        "login": login,
        "last_name": last_name,
        "first_name": first_name,
        "patronymic": patronymic,
        "password_md5": password_md5,
    }
