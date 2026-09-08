def web_context(request):
    """Common template context for the monolith UI."""
    from apps.web.i18n import (
        LOCALE_LABELS,
        SUPPORTED_LOCALES,
        get_messages,
        resolve_request_locale,
        translate,
    )

    locale = resolve_request_locale(request)
    messages = get_messages(locale)
    user = getattr(request, "user", None)
    role = None
    display_name = ""
    if user and user.is_authenticated:
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)
        display_name = (user.get_full_name() or "").strip() or user.username
    return {
        "web_role": role,
        "web_display_name": display_name,
        "api_base": "/api/v1",
        "locale": locale,
        "html_lang": "kk" if locale == "kk" else locale,
        "i18n": messages,
        "locale_labels": LOCALE_LABELS,
        "supported_locales": SUPPORTED_LOCALES,
        "t": lambda key, default="": translate(messages, key, default=default),
    }
