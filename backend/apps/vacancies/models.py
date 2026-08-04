from django.db import models
from django.contrib.auth.models import User


class VacancyStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    ARCHIVED = 'archived', 'Archived'
    PENDING = 'pending', 'Pending Moderation'
    REJECTED = 'rejected', 'Rejected'


class Vacancy(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    salary = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    job_type = models.CharField(max_length=50, default='full-time')
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=VacancyStatus.choices,
        default=VacancyStatus.ACTIVE,
    )
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vacancies'
        indexes = [
            models.Index(fields=['status', 'is_approved']),
            models.Index(fields=['employer', 'status']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return self.title
