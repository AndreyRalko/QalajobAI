from django.db import models
from django.contrib.auth.models import User


class DailyMetric(models.Model):
    """Daily platform metrics for analytics dashboard."""
    date = models.DateField(unique=True, db_index=True)
    new_users = models.IntegerField(default=0)
    new_students = models.IntegerField(default=0)
    new_employers = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_vacancies = models.IntegerField(default=0)
    new_applications = models.IntegerField(default=0)
    new_subscriptions = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ai_requests = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_daily_metrics'
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"


class PageView(models.Model):
    """Page view tracking."""
    path = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_page_views'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['path', 'created_at']),
        ]
