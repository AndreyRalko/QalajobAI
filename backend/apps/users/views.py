"""
QalaJob AI — Authentication & User API Views

Endpoints:
- POST /auth/login/          — Login (preloaded accounts only)
- POST /auth/logout/         — Logout (blacklist refresh token)
- GET  /auth/me/             — Get current user
- POST /auth/token/refresh/  — Refresh JWT
- POST /auth/change-password/ — Change password
- DELETE /auth/delete-account/ — Delete account
- POST /i18n/set-language/   — Set UI language
- POST /auth/forgot-password/ — Request password reset
- POST /auth/reset-password/  — Complete password reset
- POST /auth/verify-email/    — Verify email token
- POST /auth/resend-verification/ — Resend verification email
- GET  /users/               — List users (admin)
"""

import re
import logging

from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User

from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import UserProfile, LoginHistory
from .serializers import (
    LoginSerializer,
    SetLanguageSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
)

from .services.email_service import (
    send_verification_email,
    verify_email_token,
    send_password_reset_email,
    complete_password_reset,
)

logger = logging.getLogger('apps')
security_logger = logging.getLogger('security')


class AuthRateThrottle(AnonRateThrottle):
    rate = '10/minute'


def _jwt_response(user, profile):
    """Generate JWT token pair and user data response."""
    refresh = RefreshToken.for_user(user)
    return {
        "user": UserProfileSerializer(profile).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _validate_password_strength(password):
    """Validate password meets security requirements."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    return errors


# ── Auth Endpoints ──────────────────────────────────────────────────


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login = serializer.validated_data["login"].strip()
        password = serializer.validated_data["password"]

        user = authenticate(
            username=login,
            password=password,
        )

        if not user:
            # Log failed attempt
            try:
                failed_user = User.objects.get(username=login)
                LoginHistory.objects.create(
                    user=failed_user,
                    ip_address=_get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=False,
                )
            except User.DoesNotExist:
                pass

            security_logger.warning(f"Failed login attempt for {login} from {_get_client_ip(request)}")

            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                role="student",
            )

        if profile.is_banned:
            security_logger.warning(f"Banned user login attempt: {login}")
            return Response(
                {"message": "Account banned"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Log successful login
        LoginHistory.objects.create(
            user=user,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
        )

        return Response({"data": _jwt_response(user, profile)})


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"message": "Logged out"},
                status=status.HTTP_200_OK,
            )


@extend_schema(tags=["Auth"])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": UserProfileSerializer(profile).data}
        )


# ── Email Verification ─────────────────────────────────────────────


@extend_schema(tags=["Auth"])
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        user, error = verify_email_token(token)

        if error:
            return Response(
                {"message": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Email verified successfully"})


@extend_schema(tags=["Auth"])
class ResendVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.profile.email_verified:
            return Response(
                {"message": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_verification_email(request.user)
        return Response({"message": "Verification email sent"})


# ── Password Reset ─────────────────────────────────────────────────


@extend_schema(tags=["Auth"])
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip()

        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response(
            {"message": "If an account exists with that email, a reset link has been sent."}
        )


@extend_schema(tags=["Auth"])
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        password_errors = _validate_password_strength(new_password)
        if password_errors:
            return Response(
                {"message": password_errors[0]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, error = complete_password_reset(token, new_password)
        if error:
            return Response(
                {"message": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Password reset successfully"})


# ── Settings ───────────────────────────────────────────────────────


@extend_schema(tags=["Settings"])
class SetLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetLanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile
        profile.language = serializer.validated_data["language"]
        profile.save(update_fields=["language", "updated_at"])

        return Response(
            {"data": UserProfileSerializer(profile).data}
        )


@extend_schema(
    tags=["Settings"],
    request=ChangePasswordSerializer,
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        if not request.user.check_password(current_password):
            return Response(
                {"message": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password_errors = _validate_password_strength(new_password)
        if password_errors:
            return Response(
                {"message": password_errors[0]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        return Response({"message": "Password changed successfully"})


@extend_schema(tags=["Settings"])
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        try:
            profile = user.profile
            profile.delete()
        except UserProfile.DoesNotExist:
            pass

        logger.info(f"Account deleted: {user.email}")
        user.delete()

        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_200_OK,
        )


# ── Users List (Admin) ─────────────────────────────────────────────


class UsersListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return UserProfile.objects.select_related("user").all()