import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.utils import timezone

_STUDENT_ID_KEYS = ("student_id", "studentid")
_LOGIN_KEYS = ("login",)
_LAST_NAME_KEYS = ("last_name", "lastname", "surname", "familiya")
_FIRST_NAME_KEYS = ("first_name", "firstname", "name", "imya")
_PATRONYMIC_KEYS = ("patronymic", "middlename", "middle_name", "otchestvo")
_PASSWORD_KEYS = ("password_md5", "password", "passwd", "pass")

_LMS_TRANSCRIPT_ALIASES = {
    "id": "lms_id",
    "studentid": "student_id",
    "code": "subject_code",
    "subjectcode": "subject_code",
    "credits": "credits",
    "alpha": "alpha_mark",
    "alphamark": "alpha_mark",
    "numeral": "numeral_mark",
    "numeralmark": "numeral_mark",
    "total": "total_mark",
    "totalmark": "total_mark",
    "ru": "subject_name_ru",
    "subjectnameru": "subject_name_ru",
    "kz": "subject_name_kz",
    "subjectnamekz": "subject_name_kz",
    "en": "subject_name_en",
    "subjectnameen": "subject_name_en",
    "exam": "exam_mark",
    "exammark": "exam_mark",
    "course": "course_number",
    "coursenumber": "course_number",
    "term": "term",
    "type": "type",
    "markid": "mark_id",
    "queryid": "query_id",
    "modified": "modified",
    "subjectid": "subject_id",
    "grouptypeid": "group_type_id",
    "traditionalmark": "traditional_mark",
    "created": "created",
    "tupsubjectid": "tup_subject_id",
    "deleted": "deleted",
    "codeen": "code_en",
    "coderu": "code_ru",
    "accepted": "accepted",
    "retake": "retake",
    "hash": "hash",
    "ispassed": "is_passed",
    "r1": "r1",
    "r2": "r2",
    "pcp": "pcp",
    "ignoremarks": "ignore_marks",
    "rewritablesubjectnamekz": "rewritable_subject_name_kz",
    "rewritablesubjectnameru": "rewritable_subject_name_ru",
    "rewritablesubjectnameen": "rewritable_subject_name_en",
    "istransfercredit": "is_transfer_credit",
    "continuancesubjectid": "continuance_subject_id",
    "rewritablesubjectcode": "rewritable_subject_code",
    "isgeneralexam": "is_general_exam",
    "ects": "ects",
    "subjectstudylanguage": "subject_study_language",
    "isadditionalsubject": "is_additional_subject",
    "issubjectwithadditionaltype": "is_subject_with_additional_type",
    "iscoursework": "is_course_work",
    "calcasoldmark": "calc_as_old_mark",
    "subjecttype": "subject_type",
    "oldqueryid": "old_query_id",
    "academicdifferencecourse": "academic_difference_course",
    "academicdifferenceterm": "academic_difference_term",
    "notincludedscholarship": "not_included_scholarship",
    "wasretaken": "was_retaken",
    "reexamcount": "re_exam_count",
    "reexamreasontypes": "re_exam_reason_types",
    "previoustype": "previous_type",
    "generalexamtupsubjectid": "general_exam_tup_subject_id",
    "degreeid": "degree_id",
}


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


def _as_decimal(value):
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _as_int(value, default=None):
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_datetime(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        dt = None
        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(text[:26], fmt)
                break
            except ValueError:
                continue
        if dt is None:
            return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


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


def map_transcript_row(row):
    normalized = {_normalize_key(key): value for key, value in row.items()}
    mapped = {}

    for raw_key, raw_value in normalized.items():
        field_name = _LMS_TRANSCRIPT_ALIASES.get(raw_key, raw_key)
        mapped[field_name] = raw_value

    lms_id = _as_int(mapped.get("lms_id"))
    student_id = _as_student_id(mapped.get("student_id"))
    subject_code = _as_str(mapped.get("subject_code"))

    if lms_id is None or not student_id or not subject_code:
        return None

    defaults = {
        "student_id": student_id,
        "subject_code": subject_code,
        "credits": _as_decimal(mapped.get("credits")),
        "alpha_mark": _as_str(mapped.get("alpha_mark")),
        "numeral_mark": _as_decimal(mapped.get("numeral_mark")),
        "total_mark": _as_decimal(mapped.get("total_mark")),
        "subject_name_ru": _as_str(mapped.get("subject_name_ru")),
        "subject_name_kz": _as_str(mapped.get("subject_name_kz")),
        "subject_name_en": _as_str(mapped.get("subject_name_en")),
        "accepted": _as_int(mapped.get("accepted"), 0),
        "exam_mark": _as_decimal(mapped.get("exam_mark")),
        "retake": _as_int(mapped.get("retake"), 0),
        "course_number": _as_int(mapped.get("course_number")),
        "term": _as_int(mapped.get("term")),
        "type": _as_int(mapped.get("type"), 0),
        "hash": _as_str(mapped.get("hash")),
        "mark_id": _as_int(mapped.get("mark_id")),
        "is_passed": _as_bool(mapped.get("is_passed")),
        "r1": _as_str(mapped.get("r1")),
        "r2": _as_str(mapped.get("r2")),
        "pcp": _as_str(mapped.get("pcp")),
        "code_en": _as_str(mapped.get("code_en")) or subject_code,
        "code_ru": _as_str(mapped.get("code_ru")) or subject_code,
        "ignore_marks": _as_int(mapped.get("ignore_marks"), 0),
        "query_id": _as_int(mapped.get("query_id")),
        "deleted": _as_int(mapped.get("deleted"), 0),
        "rewritable_subject_name_kz": _as_str(mapped.get("rewritable_subject_name_kz")),
        "rewritable_subject_name_ru": _as_str(mapped.get("rewritable_subject_name_ru")),
        "rewritable_subject_name_en": _as_str(mapped.get("rewritable_subject_name_en")),
        "is_transfer_credit": _as_int(mapped.get("is_transfer_credit"), 0),
        "modified": _as_datetime(mapped.get("modified")),
        "continuance_subject_id": _as_int(mapped.get("continuance_subject_id")),
        "subject_id": _as_int(mapped.get("subject_id")),
        "rewritable_subject_code": _as_str(mapped.get("rewritable_subject_code")),
        "is_general_exam": _as_int(mapped.get("is_general_exam"), 0),
        "ects": _as_decimal(mapped.get("ects")),
        "group_type_id": _as_int(mapped.get("group_type_id")),
        "subject_study_language": _as_int(mapped.get("subject_study_language")),
        "is_additional_subject": _as_int(mapped.get("is_additional_subject"), 0),
        "is_subject_with_additional_type": _as_int(
            mapped.get("is_subject_with_additional_type"), 0
        ),
        "is_course_work": _as_int(mapped.get("is_course_work"), 0),
        "traditional_mark": _as_int(mapped.get("traditional_mark")),
        "calc_as_old_mark": _as_int(mapped.get("calc_as_old_mark"), 0),
        "created": _as_datetime(mapped.get("created")),
        "subject_type": _as_int(mapped.get("subject_type")),
        "tup_subject_id": _as_int(mapped.get("tup_subject_id")),
        "old_query_id": _as_int(mapped.get("old_query_id")),
        "academic_difference_course": _as_int(mapped.get("academic_difference_course"), 0),
        "academic_difference_term": _as_int(mapped.get("academic_difference_term"), 0),
        "not_included_scholarship": _as_int(mapped.get("not_included_scholarship"), 0),
        "was_retaken": _as_int(mapped.get("was_retaken"), 0),
        "re_exam_count": _as_int(mapped.get("re_exam_count"), 0),
        "re_exam_reason_types": _as_str(mapped.get("re_exam_reason_types")),
        "previous_type": _as_int(mapped.get("previous_type")),
        "general_exam_tup_subject_id": _as_int(mapped.get("general_exam_tup_subject_id")),
        "degree_id": _as_int(mapped.get("degree_id"), 0),
    }

    if defaults["subject_study_language"] is None:
        defaults["subject_study_language"] = 2
    if defaults["subject_type"] is None:
        defaults["subject_type"] = 7

    return lms_id, defaults
