from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class AdminActionType(models.TextChoices):
    USER_BAN = 'user_ban', 'Бан пользователя'
    USER_UNBAN = 'user_unban', 'Разбан пользователя'
    VACANCY_REMOVE = 'vacancy_remove', 'Удаление вакансии'
    VACANCY_APPROVE = 'vacancy_approve', 'Одобрение вакансии'
    COMPANY_BAN = 'company_ban', 'Бан компании'
    COMPANY_UNBAN = 'company_unban', 'Разбан компании'
    PREMIUM_GRANT = 'premium_grant', 'Выдача премиума'
    PREMIUM_REVOKE = 'premium_revoke', 'Отзыв премиума'
    SYSTEM_SETTING_CHANGE = 'system_setting_change', 'Изменение настроек'

class UserBan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban')
    reason = models.TextField()
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bans_issued')
    banned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    
    def is_active(self):
        if self.is_permanent:
            return True
        if self.expires_at:
            return timezone.now() < self.expires_at
        return False
    
    class Meta:
        ordering = ['-banned_at']

class AuditLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=50, choices=AdminActionType.choices)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs_target')
    target_id = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]

class ModerationQueueItem(models.Model):
    ITEM_TYPES = (
        ('vacancy', 'Вакансия'),
        ('company', 'Компания'),
        ('profile', 'Профиль'),
        ('content', 'Контент'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    )
    
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    target_id = models.CharField(max_length=255)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderation_reviews')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'item_type']),
        ]

class SystemSettings(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    max_upload_size = models.IntegerField(default=52428800)  # 50MB
    default_currency = models.CharField(max_length=3, default='KZT')
    support_email = models.EmailField(default='support@qalajob.ai')
    terms_version = models.CharField(max_length=50, default='1.0.0')
    privacy_version = models.CharField(max_length=50, default='1.0.0')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return 'System Settings'