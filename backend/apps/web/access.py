"""Role helpers and access mixins for HTML views."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from apps.users.models import UserRole


def user_role(user):
    if not user or not user.is_authenticated:
        return None
    profile = getattr(user, "profile", None)
    if profile is None:
        return None
    return profile.role


def is_admin_user(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user_role(user) == UserRole.ADMIN


def dashboard_url_for(user):
    role = user_role(user)
    if is_admin_user(user) or role == UserRole.ADMIN:
        return "/app/admin/"
    if role == UserRole.EMPLOYER:
        return "/app/employer/"
    return "/app/student/ai/resume/"


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require login + one of allowed roles."""

    allowed_roles = ()
    allow_staff_as_admin = True

    def test_func(self):
        role = user_role(self.request.user)
        if self.allow_staff_as_admin and (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            if UserRole.ADMIN in self.allowed_roles:
                return True
        return role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(f"/login/?next={self.request.path}")
        return redirect(dashboard_url_for(self.request.user))
