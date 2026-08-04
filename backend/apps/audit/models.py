"""
QalaJob AI — Audit Log Models
Track admin and security-sensitive actions.
"""

from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """Record of admin and security-sensitive actions."""

    ACTION_TYPES = [
        ('user_ban', 'User Banned'),
        ('user_unban', 'User Unbanned'),
        ('user_delete', 'User Deleted'),
        ('vacancy_delete', 'Vacancy Deleted'),
        ('vacancy_approve', 'Vacancy Approved'),
        ('vacancy_reject', 'Vacancy Rejected'),
        ('subscription_update', 'Subscription Updated'),
        ('application_status', 'Application Status Changed'),
        ('settings_change', 'Settings Changed'),
        ('login', 'Login'),
        ('login_failed', 'Login Failed'),
        ('password_reset', 'Password Reset'),
        ('account_delete', 'Account Deleted'),
    ]

    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions',
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['admin', 'created_at']),
        ]

    def __str__(self):
        admin_name = self.admin.email if self.admin else 'system'
        return f"[{self.created_at}] {admin_name} → {self.action} {self.target_label}"

    @classmethod
    def log(cls, admin=None, action='', target_type='', target_id='',
            target_label='', details=None, request=None):
        """Create an audit log entry."""
        ip = ''
        user_agent = ''

        if request:
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        return cls.objects.create(
            admin=admin,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            target_label=target_label[:255] if target_label else '',
            details=details or {},
            ip_address=ip or None,
            user_agent=user_agent,
        )
