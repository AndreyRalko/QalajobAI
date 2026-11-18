from django.db import models
from django.contrib.auth.models import User


class UserRole(models.TextChoices):
    STUDENT = "student", "Student"
    EMPLOYER = "employer", "Employer"
    ADMIN = "admin", "Admin"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    language = models.CharField(
        max_length=5,
        default="kk",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    photo_url = models.URLField(
        blank=True,
    )

    is_banned = models.BooleanField(
        default=False,
    )

    email_verified = models.BooleanField(
        default=False,
    )

    student_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        help_text="LMS StudentID from Platonus",
    )

    login_encrypted = models.TextField(
        blank=True,
        default="",
        help_text="Fernet-encrypted login (SECRET_KEY)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "user_profiles"

        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_banned"]),
        ]

    def __str__(self):
        from apps.users.identity import get_user_login

        login = get_user_login(self.user) or self.user_id
        return f"{login} ({self.role})"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )
    token = models.CharField(max_length=128, unique=True, db_index=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_verification_tokens"

    def __str__(self):
        return f"Verification for {self.user.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.CharField(max_length=128, unique=True, db_index=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_reset_tokens"

    def __str__(self):
        return f"Reset for {self.user.email}"


class LoginHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_history"
        ordering = ["-created_at"]

    def __str__(self):
        status = "success" if self.success else "failed"
        return f"{self.user.email} - {status} - {self.created_at}"


class UserActivityAction(models.TextChoices):
    VISIT = "visit", "Visit"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"


class UserActivityLog(models.Model):
    """User activity / visits for admin analytics."""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    user_login = models.CharField(max_length=150, blank=True, db_index=True)
    action = models.CharField(
        max_length=20,
        choices=UserActivityAction.choices,
        default=UserActivityAction.VISIT,
        db_index=True,
    )
    path = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "user_activity_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at", "action"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user_login or self.user_id} {self.action} @ {self.created_at}"