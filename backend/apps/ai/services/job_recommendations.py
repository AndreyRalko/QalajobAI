import re

from django.conf import settings

from .hh_client import search_vacancies
from .openai_client import build_hh_search_query as ai_build_hh_search_query
from .openai_client import recommend_jobs as ai_recommend_jobs

DEFAULT_HH_AREA = "40"
HH_AREA_ASTANA = "159"
HH_AREA_ALMATY = "160"


def _hh_vacancy_payload(item: dict) -> dict:
    return {
        "id": str(item.get("id") or ""),
        "title": item.get("name") or "",
        "company": item.get("company") or "",
        "city": item.get("area") or "",
        "salary": item.get("salary") or "",
        "requirements": item.get("requirement") or "",
        "description": item.get("responsibility") or "",
        "url": item.get("url") or "",
    }


def _detect_area(job_interests: str) -> str:
    lower = (job_interests or "").lower()
    if "астана" in lower or "astana" in lower or "нур-султан" in lower:
        return HH_AREA_ASTANA
    if "алмат" in lower or "almaty" in lower:
        return HH_AREA_ALMATY
    if "шымкент" in lower or "shymkent" in lower:
        return "161"
    return str(getattr(settings, "HH_AREA", DEFAULT_HH_AREA) or DEFAULT_HH_AREA)


def _heuristic_hh_search_query(candidate: dict) -> dict:
    interests = (candidate.get("job_interests") or "").strip()
    area = _detect_area(interests)

    stop_words = {
        "ищу",
        "работу",
        "работа",
        "вакансию",
        "вакансия",
        "хочу",
        "нужна",
        "нужен",
        "prefer",
        "looking",
        "for",
        "job",
    }
    tokens = [
        token
        for token in re.split(r"[^\w\u0400-\u04FF]+", interests.lower())
        if len(token) >= 3 and token not in stop_words
    ]

    text = " ".join(dict.fromkeys(tokens[:6]))[:80] or interests[:80]
    return {
        "text": text.strip(),
        "area": area,
        "reasoning": "Поисковый запрос сформирован из ваших интересов.",
    }


def build_hh_search_query(candidate: dict, *, language: str = "ru") -> dict:
    ai_result = ai_build_hh_search_query(candidate, language=language)
    text = (ai_result.get("text") or "").strip() if ai_result else ""
    if text:
        area = str(ai_result.get("area") or _detect_area(candidate.get("job_interests", "")))
        return {
            "text": text[:120],
            "area": area or DEFAULT_HH_AREA,
            "reasoning": ai_result.get("reasoning") or "",
        }
    return _heuristic_hh_search_query(candidate)


def _candidate_keywords(candidate: dict) -> set[str]:
    tokens = set()
    for token in re.split(
        r"[^\w\u0400-\u04FF]+",
        (candidate.get("job_interests") or "").lower(),
    ):
        if len(token) >= 4:
            tokens.add(token)
    return tokens


def _heuristic_recommendations(
    candidate: dict,
    vacancies: list[dict],
    limit: int,
) -> list[dict]:
    keywords = _candidate_keywords(candidate)
    scored = []

    for vacancy in vacancies:
        vacancy_text = " ".join(
            [
                vacancy.get("name") or "",
                vacancy.get("company") or "",
                vacancy.get("requirement") or "",
                vacancy.get("responsibility") or "",
                vacancy.get("area") or "",
            ]
        ).lower()

        matching = sorted(token for token in keywords if token in vacancy_text)
        score = min(35 + len(matching) * 10, 92)

        interests = (candidate.get("job_interests") or "").lower()
        if interests:
            interest_tokens = [
                token
                for token in re.split(r"[^\w\u0400-\u04FF]+", interests)
                if len(token) >= 4 and token in vacancy_text
            ]
            score = min(score + len(interest_tokens) * 8, 98)

        scored.append(
            {
                "vacancy_id": str(vacancy.get("id") or ""),
                "match_score": score,
                "matching_skills": matching[:8],
                "missing_skills": [],
                "explanation": (
                    f"Совпадение по вашему поисковому запросу ({len(matching)})."
                    if matching
                    else "Базовое совпадение по вашему поисковому запросу."
                ),
            }
        )

    scored.sort(key=lambda item: item["match_score"], reverse=True)
    return scored[:limit]


def _rank_hh_vacancies(
    candidate: dict,
    vacancies: list[dict],
    *,
    limit: int,
    language: str,
) -> list[dict]:
    if not vacancies:
        return []

    vacancy_payload = [_hh_vacancy_payload(v) for v in vacancies]
    ai_result = ai_recommend_jobs(
        candidate,
        vacancy_payload,
        limit=limit,
        language=language,
    )

    recommendations = ai_result.get("recommendations") if ai_result else None
    if not recommendations:
        return _heuristic_recommendations(candidate, vacancies, limit)

    valid_ids = {str(v.get("id") or "") for v in vacancies}
    cleaned = []
    for item in recommendations:
        vacancy_id = str(item.get("vacancy_id") or "").strip()
        if vacancy_id not in valid_ids:
            continue
        cleaned.append(
            {
                "vacancy_id": vacancy_id,
                "match_score": max(0, min(int(item.get("match_score", 0)), 100)),
                "matching_skills": item.get("matching_skills") or [],
                "missing_skills": item.get("missing_skills") or [],
                "explanation": item.get("explanation") or "",
            }
        )

    cleaned.sort(key=lambda item: item["match_score"], reverse=True)
    if cleaned:
        return cleaned[:limit]

    return _heuristic_recommendations(candidate, vacancies, limit)


def get_hh_job_recommendations(
    candidate: dict,
    *,
    limit: int = 10,
    language: str = "ru",
) -> dict:
    search = build_hh_search_query(candidate, language=language)
    search_text = search.get("text") or candidate.get("job_interests", "")
    search_area = search.get("area") or DEFAULT_HH_AREA

    hh_result = search_vacancies(
        text=search_text,
        area=search_area,
        page=0,
        per_page=max(limit * 3, 20),
    )
    hh_items = hh_result.get("items") or []

    recommendations = _rank_hh_vacancies(
        candidate,
        hh_items,
        limit=limit,
        language=language,
    )

    vacancy_map = {str(item.get("id") or ""): item for item in hh_items}
    enriched = []
    for item in recommendations:
        vacancy = vacancy_map.get(item["vacancy_id"])
        if not vacancy:
            continue
        enriched.append({**item, "vacancy": vacancy})

    return {
        "recommendations": enriched,
        "hh_search": {
            "text": search_text,
            "area": search_area,
            "reasoning": search.get("reasoning") or "",
            "found": hh_result.get("found") or len(hh_items),
            "demo": bool(hh_result.get("demo")),
            "warning": hh_result.get("warning") or "",
        },
        "vacancies_available": len(hh_items),
    }


# Backward-compatible alias used in tests/imports
get_job_recommendations = get_hh_job_recommendations
