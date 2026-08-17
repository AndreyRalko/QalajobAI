"""Shared helpers for AI API views."""


def request_language(request) -> str:
    lang = ""
    if hasattr(request, "data") and request.data is not None:
        try:
            lang = (
                request.data.get("language")
                or request.data.get("locale")
                or ""
            )
        except Exception:
            lang = ""
    if not lang:
        header = request.headers.get("Accept-Language", "")
        if header:
            lang = header.split(",")[0].strip()
    if not lang:
        try:
            profile = request.user.profile
            lang = getattr(profile, "language", None) or "kk"
        except Exception:
            lang = "kk"
    return str(lang).strip() or "kk"
