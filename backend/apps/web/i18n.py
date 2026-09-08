"""Locale catalogs for the Django web UI (kk / ru / en). Default: kk."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

LOCALE_COOKIE = "qalajob-locale"
DEFAULT_LOCALE = "kk"
SUPPORTED_LOCALES = ("kk", "ru", "en")
LOCALE_LABELS = {
    "kk": "Қазақша",
    "ru": "Русский",
    "en": "English",
}

_MESSAGES_DIR = Path(__file__).resolve().parent / "messages"

# Extra UI strings used only by Django templates / JS.
_WEB_EXTRAS = {
    "kk": {
        "web": {
            "cabinet": "Кабинет",
            "workspace": "Жұмыс кеңістігі",
            "settings": "Параметрлер",
            "changePassword": "Құпиясөзді өзгерту",
            "employerTitle": "Жұмыс беруші кабинеті",
            "employerStub": "Жұмыс беруші бөлімі әзірленуде. Студент немесе әкімші ретінде кіріңіз.",
            "notFound": "Бет табылмады",
            "backHome": "Басты бетке",
            "modeMock": "Mock",
            "jobTitlePh": "Лауазым / вакансия",
            "companyPh": "Компания",
            "jobDescPh": "Вакансия сипаттамасы (міндетті емес)",
            "searchUsers": "Логин / email / student_id",
            "yes": "иә",
            "no": "жоқ",
            "ban": "Бан",
            "unban": "Баннан шығару",
            "deleteUserConfirm": "Қолданушыны жою керек пе?",
            "deleteVacancyConfirm": "Жою керек пе?",
            "lmsTitle": "LMS синхрондау",
            "schedule": "Кесте",
            "enabled": "Қосылған",
            "hour": "Сағат",
            "minute": "Минут",
            "runNow": "Қазір іске қосу",
            "lmsTunnelHint": "Іске қосу алдында LMS MySQL-ге SSH туннелі қажет.",
            "recentLogs": "Соңғы журналдар",
            "noLogs": "Журналдар жоқ",
            "start": "Басталуы",
            "error": "Қате",
            "none": "—",
            "platform": "Платформа",
            "maintenance": "Қызмет көрсету режимі",
            "supportEmail": "Support email",
            "updatePassword": "Құпиясөзді жаңарту",
            "djangoAdmin": "Django Admin",
            "aiLogs": "AI журналдар",
            "loginInvalid": "Platonus логині немесе құпиясөзі қате.",
            "accountBanned": "Аккаунт бұғатталған.",
            "loggedOut": "Сіз аккаунттан шықтыңыз.",
            "passwordWrong": "Ағымдағы құпиясөз қате.",
            "passwordShort": "Жаңа құпиясөз кемінде 8 таңбадан тұруы керек.",
            "passwordMismatch": "Құпиясөздер сәйкес келмейді.",
            "passwordUpdated": "Құпиясөз жаңартылды.",
            "settingsSaved": "Параметрлер сақталды.",
            "noUsers": "Қолданушылар жоқ",
            "noVacancies": "Бос орындар жоқ",
            "empty": "Бос",
            "lookingJobs": "Вакансиялар ізделуде…",
            "found": "Табылды",
            "tryOtherQuery": "Ештеңе табылмады. Басқа сұранысты қолданып көріңіз.",
            "openOnHh": "hh.kz ашу",
            "saving": "Сақталуда…",
            "saved": "Сақталды",
            "enhancing": "Жақсартуда…",
            "enhanced": "Жақсартылды",
            "errorPrefix": "Қате",
            "footerTag": "студенттерге арналған мансап",
            "howTitle": "Оқудан өтінішке дейін",
            "contactLead": "Қолдау және кіру сұрақтары:",
            "saveVacancy": "Сақтау",
            "savedVacancy": "Сақталды",
            "unsaveVacancy": "Жою",
            "prepareWithAi": "Осы вакансиямен дайындалу",
            "useForAi": "AI үшін таңдау",
            "selectedForAi": "AI үшін таңдалған",
            "savedSection": "Сақталған вакансиялар",
            "noSaved": "Сақталған вакансиялар жоқ",
            "activeVacancy": "Белсенді вакансия AI үшін",
            "clearVacancy": "Тазалау",
            "adaptResume": "Резюмені бейімдеу",
            "genCover": "Хат жасау",
            "genInterview": "Сұхбат жоспары",
            "selectVacancyHint": "Вакансияны таңдаңыз — AI резюме, хат және сұхбатты соған бейімдейді.",
            "pickSavedVacancy": "Сақталған вакансияны таңдау",
            "pickSavedPlaceholder": "— сақталғандардан таңдаңыз —",
            "goToJobs": "Вакансияларды ашу",
        }
    },
    "ru": {
        "web": {
            "cabinet": "Кабинет",
            "workspace": "Рабочее пространство",
            "settings": "Настройки",
            "changePassword": "Смена пароля",
            "employerTitle": "Кабинет работодателя",
            "employerStub": "Раздел работодателя пока в разработке. Войдите как студент или администратор.",
            "notFound": "Страница не найдена",
            "backHome": "На главную",
            "modeMock": "Mock",
            "jobTitlePh": "Должность / вакансия",
            "companyPh": "Компания",
            "jobDescPh": "Описание вакансии (необязательно)",
            "searchUsers": "Поиск логин / email / student_id",
            "yes": "да",
            "no": "нет",
            "ban": "Бан",
            "unban": "Разбан",
            "deleteUserConfirm": "Удалить пользователя?",
            "deleteVacancyConfirm": "Удалить?",
            "lmsTitle": "Синхронизация LMS",
            "schedule": "Расписание",
            "enabled": "Включено",
            "hour": "Час",
            "minute": "Минута",
            "runNow": "Запустить сейчас",
            "lmsTunnelHint": "Перед запуском нужен ручной SSH-туннель к MySQL LMS.",
            "recentLogs": "Последние логи",
            "noLogs": "Логов пока нет",
            "start": "Старт",
            "error": "Ошибка",
            "none": "—",
            "platform": "Платформа",
            "maintenance": "Режим обслуживания",
            "supportEmail": "Support email",
            "updatePassword": "Обновить пароль",
            "djangoAdmin": "Django Admin",
            "aiLogs": "AI логи",
            "loginInvalid": "Неверный логин или пароль Platonus.",
            "accountBanned": "Аккаунт заблокирован.",
            "loggedOut": "Вы вышли из аккаунта.",
            "passwordWrong": "Текущий пароль неверен.",
            "passwordShort": "Новый пароль должен быть не короче 8 символов.",
            "passwordMismatch": "Пароли не совпадают.",
            "passwordUpdated": "Пароль обновлён.",
            "settingsSaved": "Настройки сохранены.",
            "noUsers": "Нет пользователей",
            "noVacancies": "Нет вакансий",
            "empty": "Пусто",
            "lookingJobs": "Ищем вакансии…",
            "found": "Найдено",
            "tryOtherQuery": "Ничего не найдено. Попробуйте другой запрос.",
            "openOnHh": "Открыть на hh.kz",
            "saving": "Сохранение…",
            "saved": "Сохранено",
            "enhancing": "Улучшение…",
            "enhanced": "Улучшено",
            "errorPrefix": "Ошибка",
            "footerTag": "карьера для студентов",
            "howTitle": "От учёбы к отклику",
            "contactLead": "По вопросам доступа и поддержки:",
            "saveVacancy": "Сохранить",
            "savedVacancy": "Сохранено",
            "unsaveVacancy": "Удалить",
            "prepareWithAi": "Готовиться с AI",
            "useForAi": "Выбрать для AI",
            "selectedForAi": "Выбрано для AI",
            "savedSection": "Сохранённые вакансии",
            "noSaved": "Нет сохранённых вакансий",
            "activeVacancy": "Активная вакансия для AI",
            "clearVacancy": "Очистить",
            "adaptResume": "Адаптировать резюме",
            "genCover": "Сгенерировать письмо",
            "genInterview": "План собеседования",
            "selectVacancyHint": "Выберите вакансию — AI подстроит резюме, письмо и интервью под неё.",
            "pickSavedVacancy": "Выбрать сохранённую вакансию",
            "pickSavedPlaceholder": "— выберите из сохранённых —",
            "goToJobs": "Открыть вакансии",
        }
    },
    "en": {
        "web": {
            "cabinet": "Dashboard",
            "workspace": "Workspace",
            "settings": "Settings",
            "changePassword": "Change password",
            "employerTitle": "Employer dashboard",
            "employerStub": "Employer area is under construction. Sign in as a student or admin.",
            "notFound": "Page not found",
            "backHome": "Back home",
            "modeMock": "Mock",
            "jobTitlePh": "Job title / vacancy",
            "companyPh": "Company",
            "jobDescPh": "Job description (optional)",
            "searchUsers": "Search login / email / student_id",
            "yes": "yes",
            "no": "no",
            "ban": "Ban",
            "unban": "Unban",
            "deleteUserConfirm": "Delete this user?",
            "deleteVacancyConfirm": "Delete?",
            "lmsTitle": "LMS sync",
            "schedule": "Schedule",
            "enabled": "Enabled",
            "hour": "Hour",
            "minute": "Minute",
            "runNow": "Run now",
            "lmsTunnelHint": "Open an SSH tunnel to LMS MySQL before running sync.",
            "recentLogs": "Recent logs",
            "noLogs": "No logs yet",
            "start": "Started",
            "error": "Error",
            "none": "—",
            "platform": "Platform",
            "maintenance": "Maintenance mode",
            "supportEmail": "Support email",
            "updatePassword": "Update password",
            "djangoAdmin": "Django Admin",
            "aiLogs": "AI logs",
            "loginInvalid": "Invalid Platonus login or password.",
            "accountBanned": "Account is banned.",
            "loggedOut": "You have been signed out.",
            "passwordWrong": "Current password is incorrect.",
            "passwordShort": "New password must be at least 8 characters.",
            "passwordMismatch": "Passwords do not match.",
            "passwordUpdated": "Password updated.",
            "settingsSaved": "Settings saved.",
            "noUsers": "No users",
            "noVacancies": "No vacancies",
            "empty": "Empty",
            "lookingJobs": "Searching vacancies…",
            "found": "Found",
            "tryOtherQuery": "Nothing found. Try another query.",
            "openOnHh": "Open on hh.kz",
            "saving": "Saving…",
            "saved": "Saved",
            "enhancing": "Enhancing…",
            "enhanced": "Enhanced",
            "errorPrefix": "Error",
            "footerTag": "careers for students",
            "howTitle": "From studies to applications",
            "contactLead": "For access and support:",
            "saveVacancy": "Save",
            "savedVacancy": "Saved",
            "unsaveVacancy": "Remove",
            "prepareWithAi": "Prepare with AI",
            "useForAi": "Use for AI",
            "selectedForAi": "Selected for AI",
            "savedSection": "Saved vacancies",
            "noSaved": "No saved vacancies",
            "activeVacancy": "Active vacancy for AI",
            "clearVacancy": "Clear",
            "adaptResume": "Adapt resume",
            "genCover": "Generate cover letter",
            "genInterview": "Interview plan",
            "selectVacancyHint": "Pick a vacancy — AI will tailor resume, letter and interview to it.",
            "pickSavedVacancy": "Choose saved vacancy",
            "pickSavedPlaceholder": "— choose from saved —",
            "goToJobs": "Open vacancies",
        }
    },
}


def normalize_locale(value):
    if not value:
        return DEFAULT_LOCALE
    raw = str(value).strip().lower()
    if raw in ("kz", "kk", "kaz", "kk-kz"):
        return "kk"
    if raw in ("ru", "ru-ru", "rus"):
        return "ru"
    if raw in ("en", "en-us", "en-gb", "eng"):
        return "en"
    return DEFAULT_LOCALE


@lru_cache(maxsize=8)
def _load_catalog(locale: str) -> dict:
    path = _MESSAGES_DIR / f"{locale}.json"
    if not path.exists():
        path = _MESSAGES_DIR / f"{DEFAULT_LOCALE}.json"
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    extras = _WEB_EXTRAS.get(locale) or _WEB_EXTRAS[DEFAULT_LOCALE]
    merged = deepcopy(data)
    for key, value in extras.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


def get_messages(locale=None) -> dict:
    return _load_catalog(normalize_locale(locale))


def translate(messages: dict, key: str, default: str = "", **kwargs) -> str:
    node = messages
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            text = default or key
            break
        node = node[part]
    else:
        text = node if isinstance(node, str) else default or key

    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def resolve_request_locale(request) -> str:
    cookie = request.COOKIES.get(LOCALE_COOKIE)
    if cookie:
        return normalize_locale(cookie)

    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        profile = getattr(user, "profile", None)
        if profile is not None and getattr(profile, "language", None):
            return normalize_locale(profile.language)

    session_lang = request.session.get("locale")
    if session_lang:
        return normalize_locale(session_lang)

    return DEFAULT_LOCALE


def apply_locale(request, locale: str) -> str:
    locale = normalize_locale(locale)
    request.session["locale"] = locale
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        profile = getattr(user, "profile", None)
        if profile is not None and hasattr(profile, "language"):
            if profile.language != locale:
                profile.language = locale
                profile.save(update_fields=["language"])
    return locale
