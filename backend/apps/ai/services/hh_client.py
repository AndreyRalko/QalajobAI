"""
HeadHunter (hh.ru / hh.kz) API client.

GET /vacancies and GET /vacancies/{id} currently require an approved app
and a Bearer token (HH_APP_TOKEN or OAuth client_credentials).
GET /areas remains available without a token.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger("apps")

HH_API_BASE = "https://api.hh.ru"
HH_OAUTH_TOKEN_URL = "https://hh.ru/oauth/token"
TOKEN_FILE = Path(__file__).resolve().parents[3] / ".hh_app_token.json"

_token_cache: dict[str, Any] = {"access_token": "", "expires_at": 0.0}
VACANCY_URL_RE = re.compile(
    r"(?:https?://)?(?:[\w.-]*\.)?hh\.(?:ru|kz|uz|by)/(?:vacancy|vacancies)/(\d+)",
    re.IGNORECASE,
)

# Kazakhstan
DEFAULT_AREA = "40"

DEMO_VACANCIES = [
    {
        "id": "demo-php-1",
        "name": "PHP Developer (Laravel)",
        "employer": {"name": "TechNova KZ"},
        "area": {"name": "Алматы"},
        "salary": {"from": 600000, "to": 900000, "currency": "KZT"},
        "snippet": {
            "requirement": "PHP 8, Laravel, MySQL, REST API",
            "responsibility": "Разработка backend-сервисов и интеграций",
        },
        "alternate_url": "https://hh.kz/vacancy/demo-php-1",
        "published_at": "2026-08-01T10:00:00+0500",
    },
    {
        "id": "demo-js-1",
        "name": "Frontend Developer (React)",
        "employer": {"name": "Digital Astana"},
        "area": {"name": "Астана"},
        "salary": {"from": 700000, "to": 1100000, "currency": "KZT"},
        "snippet": {
            "requirement": "React, TypeScript, Next.js",
            "responsibility": "UI продуктов и админ-панелей",
        },
        "alternate_url": "https://hh.kz/vacancy/demo-js-1",
        "published_at": "2026-08-02T12:00:00+0500",
    },
    {
        "id": "demo-py-1",
        "name": "Python Backend Developer",
        "employer": {"name": "FinSoft"},
        "area": {"name": "Алматы"},
        "salary": {"from": 800000, "to": 1300000, "currency": "KZT"},
        "snippet": {
            "requirement": "Python, Django/FastAPI, PostgreSQL",
            "responsibility": "API и бизнес-логика fintech-сервисов",
        },
        "alternate_url": "https://hh.kz/vacancy/demo-py-1",
        "published_at": "2026-08-03T09:00:00+0500",
    },
]

DEMO_DETAILS = {
    "demo-php-1": {
        **DEMO_VACANCIES[0],
        "description": (
            "<p>Ищем PHP-разработчика в продуктовую команду.</p>"
            "<p><b>Требования:</b> PHP 8+, Laravel, MySQL/PostgreSQL, Git, REST.</p>"
            "<p><b>Будет плюсом:</b> Docker, Redis, очереди, английский B1+.</p>"
            "<p><b>Обязанности:</b> разработка фич, код-ревью, интеграции с внешними API.</p>"
        ),
        "key_skills": [
            {"name": "PHP"},
            {"name": "Laravel"},
            {"name": "MySQL"},
            {"name": "REST"},
        ],
        "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"},
        "employment": {"id": "full", "name": "Полная занятость"},
    },
    "demo-js-1": {
        **DEMO_VACANCIES[1],
        "description": (
            "<p>Frontend developer для веб-продуктов.</p>"
            "<p><b>Требования:</b> React, TypeScript, Next.js, CSS/Tailwind.</p>"
            "<p><b>Обязанности:</b> интерфейсы, оптимизация, работа с дизайном.</p>"
        ),
        "key_skills": [
            {"name": "React"},
            {"name": "TypeScript"},
            {"name": "Next.js"},
        ],
        "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"},
        "employment": {"id": "full", "name": "Полная занятость"},
    },
    "demo-py-1": {
        **DEMO_VACANCIES[2],
        "description": (
            "<p>Python backend в fintech.</p>"
            "<p><b>Требования:</b> Python 3.11+, Django или FastAPI, PostgreSQL, SQL.</p>"
            "<p><b>Обязанности:</b> сервисы, API, тесты, code review.</p>"
        ),
        "key_skills": [
            {"name": "Python"},
            {"name": "Django"},
            {"name": "PostgreSQL"},
        ],
        "experience": {"id": "between3And6", "name": "От 3 до 6 лет"},
        "employment": {"id": "full", "name": "Полная занятость"},
    },
}


def _user_agent() -> str:
    return getattr(
        settings,
        "HH_USER_AGENT",
        "QalaJobAI/1.0 (noreply@qalajob.kz)",
    )


def _load_token_file() -> tuple[str, float]:
    try:
        if not TOKEN_FILE.exists():
            return "", 0.0
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        return str(data.get("access_token") or "").strip(), float(data.get("expires_at") or 0)
    except Exception:
        return "", 0.0


def _save_token_file(token: str, expires_at: float) -> None:
    try:
        TOKEN_FILE.write_text(
            json.dumps({"access_token": token, "expires_at": expires_at}),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning("Could not persist HH app token: %s", e)


def _cached_token() -> str:
    now = time.time()
    mem = str(_token_cache.get("access_token") or "")
    mem_exp = float(_token_cache.get("expires_at") or 0)
    if mem and now < mem_exp - 60:
        return mem

    file_token, file_exp = _load_token_file()
    if file_token and now < file_exp - 60:
        _token_cache["access_token"] = file_token
        _token_cache["expires_at"] = file_exp
        return file_token

    if file_token:
        # Expired or HH refused a refresh — still better than no token
        _token_cache["access_token"] = file_token
        _token_cache["expires_at"] = file_exp
        return file_token
    return ""


def _store_token(token: str, ttl: int) -> str:
    expires_at = time.time() + max(int(ttl or 1209600), 60)
    _token_cache["access_token"] = token
    _token_cache["expires_at"] = expires_at
    _save_token_file(token, expires_at)
    return token


def _app_token() -> str:
    static = str(getattr(settings, "HH_APP_TOKEN", "") or "").strip()
    if static:
        return static
    return _oauth_app_token()


def _oauth_app_token() -> str:
    client_id = str(getattr(settings, "HH_CLIENT_ID", "") or "").strip()
    client_secret = str(getattr(settings, "HH_CLIENT_SECRET", "") or "").strip()
    if not client_id or not client_secret:
        return ""

    cached = _cached_token()
    now = time.time()
    expires_at = float(_token_cache.get("expires_at") or 0)
    if cached and now < expires_at - 60:
        return cached

    try:
        response = requests.post(
            HH_OAUTH_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={
                "User-Agent": _user_agent(),
                "HH-User-Agent": _user_agent(),
            },
            timeout=25,
        )
    except requests.RequestException as e:
        logger.error("HH OAuth token request failed: %s", e)
        return cached

    if not response.ok:
        body = response.text[:300]
        logger.error("HH OAuth error %s: %s", response.status_code, body)
        # HH issues one app token at a time and rejects frequent refresh.
        if "refresh too early" in body.lower() and cached:
            logger.warning("HH token refresh too early — reusing cached app token")
            return cached
        return cached

    data = response.json()
    token = str(data.get("access_token") or "").strip()
    ttl = int(data.get("expires_in") or 1209600)
    if token:
        return _store_token(token, ttl)
    return cached


def _use_demo() -> bool:
    return bool(getattr(settings, "HH_USE_DEMO", False))


def extract_vacancy_id(value: str) -> Optional[str]:
    raw = (value or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return raw
    if raw.startswith("demo-"):
        return raw
    m = VACANCY_URL_RE.search(raw)
    if m:
        return m.group(1)
    return None


def _headers() -> dict[str, str]:
    headers = {
        "User-Agent": _user_agent(),
        "HH-User-Agent": _user_agent(),
        "Accept": "application/json",
    }
    token = _app_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(path: str, params: Optional[dict] = None) -> dict[str, Any]:
    url = f"{HH_API_BASE}{path}"
    try:
        response = requests.get(
            url,
            params=params or {},
            headers=_headers(),
            timeout=25,
        )
    except requests.RequestException as e:
        logger.error("HH request failed: %s", e)
        raise RuntimeError("HeadHunter API unavailable") from e

    if response.status_code == 403:
        raise PermissionError(
            "HeadHunter API forbidden. Register an app at https://dev.hh.ru "
            "and set HH_CLIENT_ID / HH_CLIENT_SECRET (or HH_APP_TOKEN) in backend/.env"
        )
    if response.status_code == 400 and "bad_user_agent" in (response.text or "").lower():
        raise PermissionError(
            "HeadHunter rejected User-Agent. Use format AppName/1.0 (email@domain) "
            "matching the registered application."
        )
    if response.status_code == 404:
        raise LookupError("Vacancy not found")
    if not response.ok:
        logger.error("HH API error %s: %s", response.status_code, response.text[:300])
        raise RuntimeError(f"HeadHunter API error ({response.status_code})")

    return response.json()


def strip_html(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html or "", flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_salary(salary: Optional[dict]) -> str:
    if not salary:
        return ""
    currency = salary.get("currency") or ""
    frm = salary.get("from")
    to = salary.get("to")
    if frm and to:
        return f"{frm}–{to} {currency}".strip()
    if frm:
        return f"от {frm} {currency}".strip()
    if to:
        return f"до {to} {currency}".strip()
    return ""


def normalize_list_item(item: dict) -> dict:
    employer = item.get("employer") or {}
    area = item.get("area") or {}
    snippet = item.get("snippet") or {}
    return {
        "id": str(item.get("id")),
        "name": item.get("name") or "",
        "company": employer.get("name") or "",
        "area": area.get("name") or "",
        "salary": format_salary(item.get("salary")),
        "requirement": strip_html(snippet.get("requirement") or ""),
        "responsibility": strip_html(snippet.get("responsibility") or ""),
        "url": item.get("alternate_url") or "",
        "published_at": item.get("published_at") or "",
        "source": "hh",
    }


def normalize_detail(item: dict) -> dict:
    base = normalize_list_item(item)
    skills = [s.get("name") for s in (item.get("key_skills") or []) if s.get("name")]
    experience = (item.get("experience") or {}).get("name") or ""
    employment = (item.get("employment") or {}).get("name") or ""
    description = strip_html(item.get("description") or "")
    base.update(
        {
            "description": description,
            "skills": skills,
            "experience": experience,
            "employment": employment,
            "raw_description_html": item.get("description") or "",
        }
    )
    return base


def vacancy_to_prompt_text(vacancy: dict) -> str:
    parts = [
        f"Title: {vacancy.get('name') or ''}",
        f"Company: {vacancy.get('company') or ''}",
        f"Location: {vacancy.get('area') or ''}",
        f"Salary: {vacancy.get('salary') or 'n/a'}",
        f"Experience: {vacancy.get('experience') or 'n/a'}",
        f"Employment: {vacancy.get('employment') or 'n/a'}",
        f"Skills: {', '.join(vacancy.get('skills') or []) or 'n/a'}",
        f"Requirements: {vacancy.get('requirement') or ''}",
        f"Responsibilities: {vacancy.get('responsibility') or ''}",
        f"Description:\n{vacancy.get('description') or ''}",
    ]
    return "\n".join(p for p in parts if p and not p.endswith(": "))


def search_vacancies(
    text: str,
    area: Optional[str] = None,
    page: int = 0,
    per_page: int = 20,
) -> dict:
    query = (text or "").strip()
    area_id = str(area or getattr(settings, "HH_AREA", DEFAULT_AREA) or DEFAULT_AREA)
    per_page = max(1, min(int(per_page or 20), 50))
    page = max(0, int(page or 0))

    if _use_demo():
        filtered = [
            v
            for v in DEMO_VACANCIES
            if not query
            or query.lower() in (v.get("name") or "").lower()
            or query.lower() in ((v.get("employer") or {}).get("name") or "").lower()
            or query.lower() in ((v.get("snippet") or {}).get("requirement") or "").lower()
        ] or DEMO_VACANCIES
        items = [normalize_list_item(v) for v in filtered]
        return {
            "items": items,
            "found": len(items),
            "page": 0,
            "pages": 1,
            "per_page": per_page,
            "demo": True,
        }

    try:
        data = _request(
            "/vacancies",
            {
                "text": query,
                "area": area_id,
                "page": page,
                "per_page": per_page,
                "order_by": "relevance",
            },
        )
        items = [normalize_list_item(i) for i in (data.get("items") or [])]
        return {
            "items": items,
            "found": data.get("found") or len(items),
            "page": data.get("page") or page,
            "pages": data.get("pages") or 1,
            "per_page": data.get("per_page") or per_page,
            "demo": False,
        }
    except PermissionError as e:
        # Graceful fallback so product remains usable while token is configured
        logger.warning("HH vacancies forbidden — serving demo results")
        items = [normalize_list_item(v) for v in DEMO_VACANCIES]
        has_creds = bool(
            str(getattr(settings, "HH_CLIENT_ID", "") or "").strip()
            and str(getattr(settings, "HH_CLIENT_SECRET", "") or "").strip()
        )
        warning = str(e)
        if has_creds and not _app_token():
            warning = (
                "HH отказал в новом токене приложения (refresh too early). "
                "Скопируйте текущий access token с https://dev.hh.ru "
                "в HH_APP_TOKEN в backend/.env и перезапустите сервер."
            )
        elif has_creds:
            warning = (
                "HeadHunter API вернул 403 даже с токеном. "
                "Проверьте User-Agent — он должен совпадать с названием приложения на dev.hh.ru."
            )
        return {
            "items": items,
            "found": len(items),
            "page": 0,
            "pages": 1,
            "per_page": per_page,
            "demo": True,
            "warning": warning,
        }


def get_vacancy(vacancy_id: str) -> dict:
    vid = extract_vacancy_id(vacancy_id) or (vacancy_id or "").strip()
    if not vid:
        raise ValueError("vacancy_id is required")

    if vid in DEMO_DETAILS or _use_demo():
        detail = DEMO_DETAILS.get(vid) or DEMO_DETAILS["demo-php-1"]
        return {**normalize_detail(detail), "demo": True}

    try:
        data = _request(f"/vacancies/{vid}")
        return {**normalize_detail(data), "demo": False}
    except PermissionError:
        if vid in DEMO_DETAILS:
            return {**normalize_detail(DEMO_DETAILS[vid]), "demo": True}
        raise
