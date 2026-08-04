from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class ApplicationStatus(models.TextChoices):
    PENDING = 'pending', 'На рассмотрении'
    REVIEWING = 'reviewing', 'Проверяется'
    INTERVIEW = 'interview', 'Собеседование'
    ACCEPTED = 'accepted', 'Принято'
    REJECTED = 'rejected', 'Отклонено'
    WITHDRAWN = 'withdrawn', 'Отозвано'

class Application(models.Model):
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications_as_candidate'
    )
    vacancy_id = models.CharField(
        max_length=255,
        help_text='Reference to vacancy in Firestore'
    )
    employer_id = models.CharField(
        max_length=255,
        help_text='Reference to employer'
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    cover_letter = models.TextField(
        blank=True,
        null=True,
        max_length=2000
    )
    resume_file = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )
    notes = models.TextField(
        blank=True,
        null=True
    )
    interview_date = models.DateTimeField(
        blank=True,
        null=True
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    withdrawn_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['employer_id', 'status']),
            models.Index(fields=['vacancy_id']),
        ]
        unique_together = ['candidate', 'vacancy_id']
    
    def __str__(self):
        return f"Application #{self.id} - {self.candidate.email} - {self.status}"
    
    def can_withdraw(self):
        return self.status in [
            ApplicationStatus.PENDING,
            ApplicationStatus.REVIEWING
        ]
    
    def withdraw(self):
        if self.can_withdraw():
            self.status = ApplicationStatus.WITHDRAWN
            self.withdrawn_at = timezone.now()
            self.save()
            return True
        return False


class ApplicationHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='history'
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='application_changes'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Application Histories'
    
    def __str__(self):
        return f"Application #{self.application.id} - {self.status} at {self.changed_at}"


class ApplicationNotification(models.Model):
    NotificationType = models.TextChoices(
        'NotificationType',
        'RECEIVED ACCEPTED REJECTED INTERVIEW_SCHEDULED WITHDRAWN'
    )
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='application_notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.email} - {self.notification_type}"


class ApplicationStatistics(models.Model):
    candidate = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='application_stats'
    )
    total_applications = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    reviewing_count = models.IntegerField(default=0)
    interview_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)
    rejected_count = models.IntegerField(default=0)
    withdrawn_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Application Statistics'
    
    def __str__(self):
        return f"Stats for {self.candidate.email}"
    
    def refresh(self):
        self.total_applications = self.candidate.applications_as_candidate.count()
        self.pending_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.PENDING
        ).count()
        self.reviewing_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.REVIEWING
        ).count()
        self.interview_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.INTERVIEW
        ).count()
        self.accepted_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.ACCEPTED
        ).count()
        self.rejected_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.REJECTED
        ).count()
        self.withdrawn_count = self.candidate.applications_as_candidate.filter(
            status=ApplicationStatus.WITHDRAWN
        ).count()
        self.save()