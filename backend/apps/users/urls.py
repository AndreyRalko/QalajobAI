from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    MeView,
    SetLanguageView,
    ChangePasswordView,
    DeleteAccountView,
    UsersListView,
    ForgotPasswordView,
    ResetPasswordView,
    VerifyEmailView,
    ResendVerificationView,
)

app_name = "users"

urlpatterns = [
    # Auth
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", MeView.as_view(), name="me"),

    # Email Verification
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("auth/resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),

    # Password Reset
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    # Settings
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/delete-account/", DeleteAccountView.as_view(), name="delete-account"),
    path("i18n/set-language/", SetLanguageView.as_view(), name="set-language"),

    # Users (admin)
    path("users/", UsersListView.as_view(), name="users-list"),
]