"""
Email service for QalaJob AI.
Handles verification emails, password reset, and notifications.
"""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.users.models import EmailVerificationToken, PasswordResetToken

import logging

logger = logging.getLogger('apps')


def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(48)


def send_verification_email(user):
    """Send email verification link to user."""
    token = generate_token()
    expires_at = timezone.now() + timedelta(hours=24)

    EmailVerificationToken.objects.filter(user=user).delete()
    EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
    )

    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = 'QalaJob AI — Verify your email'
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">QalaJob AI</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">AI Career Platform</p>
        </div>
        <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 16px 16px; border: 1px solid #e2e8f0;">
            <h2 style="color: #1e293b; margin-top: 0;">Verify your email address</h2>
            <p style="color: #475569; line-height: 1.6;">
                Hello <strong>{user.first_name or user.email}</strong>,
            </p>
            <p style="color: #475569; line-height: 1.6;">
                Please click the button below to verify your email address and activate your account.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}"
                   style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 14px 32px;
                          border-radius: 12px; text-decoration: none; font-weight: bold; display: inline-block;">
                    Verify Email
                </a>
            </div>
            <p style="color: #94a3b8; font-size: 13px;">
                This link expires in 24 hours. If you didn't create an account, you can ignore this email.
            </p>
        </div>
    </div>
    """
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def verify_email_token(token):
    """Verify an email verification token."""
    try:
        record = EmailVerificationToken.objects.select_related('user').get(
            token=token,
            is_used=False,
        )
        if record.expires_at < timezone.now():
            return None, 'Token expired'

        record.is_used = True
        record.save(update_fields=['is_used'])

        profile = record.user.profile
        profile.email_verified = True
        profile.save(update_fields=['email_verified', 'updated_at'])

        return record.user, None
    except EmailVerificationToken.DoesNotExist:
        return None, 'Invalid token'


def send_password_reset_email(user):
    """Send password reset link to user."""
    token = generate_token()
    expires_at = timezone.now() + timedelta(hours=1)

    PasswordResetToken.objects.filter(user=user).delete()
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
    )

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    subject = 'QalaJob AI — Reset your password'
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">QalaJob AI</h1>
            <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">Password Reset</p>
        </div>
        <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 16px 16px; border: 1px solid #e2e8f0;">
            <h2 style="color: #1e293b; margin-top: 0;">Reset your password</h2>
            <p style="color: #475569; line-height: 1.6;">
                Hello <strong>{user.first_name or user.email}</strong>,
            </p>
            <p style="color: #475569; line-height: 1.6;">
                We received a request to reset your password. Click the button below to set a new password.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 14px 32px;
                          border-radius: 12px; text-decoration: none; font-weight: bold; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p style="color: #94a3b8; font-size: 13px;">
                This link expires in 1 hour. If you didn't request a password reset, you can ignore this email.
            </p>
        </div>
    </div>
    """
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False


def verify_reset_token(token):
    """Verify a password reset token."""
    try:
        record = PasswordResetToken.objects.select_related('user').get(
            token=token,
            is_used=False,
        )
        if record.expires_at < timezone.now():
            return None, 'Token expired'
        return record, None
    except PasswordResetToken.DoesNotExist:
        return None, 'Invalid token'


def complete_password_reset(token, new_password):
    """Complete password reset with new password."""
    record, error = verify_reset_token(token)
    if error:
        return None, error

    user = record.user
    user.set_password(new_password)
    user.save()

    record.is_used = True
    record.save(update_fields=['is_used'])

    logger.info(f"Password reset completed for {user.email}")
    return user, None
