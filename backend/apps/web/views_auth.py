from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.users.models import LoginHistory, UserProfile
from apps.web.access import dashboard_url_for, is_admin_user
from apps.web.i18n import (
    LOCALE_COOKIE,
    apply_locale,
    get_messages,
    normalize_locale,
    resolve_request_locale,
    translate,
)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _tx(request, key, default=""):
    return translate(get_messages(resolve_request_locale(request)), key, default=default)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_url_for(request.user))

    error = ""
    if request.GET.get("banned"):
        error = _tx(request, "web.accountBanned", "Аккаунт бұғатталған.")

    if request.method == "POST":
        username = (request.POST.get("login") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if not user:
            error = _tx(request, "web.loginInvalid")
        else:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, role="student")

            if profile.is_banned:
                error = _tx(request, "web.accountBanned")
            else:
                LoginHistory.objects.create(
                    user=user,
                    ip_address=_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    success=True,
                )
                login(request, user)
                next_url = request.GET.get("next") or request.POST.get("next")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect(dashboard_url_for(user))

    return render(
        request,
        "web/auth/login.html",
        {"error": error, "next": request.GET.get("next", "")},
    )


def logout_view(request):
    logout(request)
    messages.info(request, _tx(request, "web.loggedOut"))
    return redirect("web:login")


@login_required
@require_http_methods(["POST"])
def change_password_view(request):
    current = request.POST.get("current_password") or ""
    new1 = request.POST.get("new_password") or ""
    new2 = request.POST.get("new_password_confirm") or ""
    if not request.user.check_password(current):
        messages.error(request, _tx(request, "web.passwordWrong"))
    elif len(new1) < 8:
        messages.error(request, _tx(request, "web.passwordShort"))
    elif new1 != new2:
        messages.error(request, _tx(request, "web.passwordMismatch"))
    else:
        request.user.set_password(new1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, _tx(request, "web.passwordUpdated"))

    if is_admin_user(request.user):
        return redirect("web:admin-settings")
    return redirect("web:student-settings")


@require_POST
def set_language_view(request):
    locale = apply_locale(request, request.POST.get("locale") or "")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not next_url.startswith("/"):
        next_url = "/"
    response = redirect(next_url)
    response.set_cookie(
        LOCALE_COOKIE,
        locale,
        max_age=365 * 24 * 60 * 60,
        samesite="Lax",
    )
    return response


@require_http_methods(["GET"])
def set_language_get_view(request):
    """Allow ?lang=kk|ru|en links."""
    locale = apply_locale(request, request.GET.get("lang") or "")
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not next_url.startswith("/"):
        next_url = "/"
    response = redirect(next_url)
    response.set_cookie(
        LOCALE_COOKIE,
        locale,
        max_age=365 * 24 * 60 * 60,
        samesite="Lax",
    )
    return response
