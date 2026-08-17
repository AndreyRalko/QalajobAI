from django.conf import settings as django_settings
from django.db import models


class LmsSyncStatus(models.TextChoices):
    RUNNING = "running", "Running"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class LmsSyncSchedule(models.Model):
    """Singleton with daily LMS sync time configured from admin UI."""

    enabled = models.BooleanField(default=True)
    hour = models.PositiveSmallIntegerField(default=2)
    minute = models.PositiveSmallIntegerField(default=0)
    last_scheduled_run = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lms_sync_schedule"
        verbose_name = "LMS sync schedule"
        verbose_name_plural = "LMS sync schedule"

    def __str__(self):
        return f"LMS sync daily at {self.hour:02d}:{self.minute:02d}"

    @classmethod
    def load(cls):
        schedule, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "enabled": django_settings.LMS_SYNC_ENABLED,
                "hour": django_settings.LMS_SYNC_CRON_HOUR,
                "minute": django_settings.LMS_SYNC_CRON_MINUTE,
            },
        )
        return schedule

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.hour > 23:
            raise ValidationError({"hour": "Hour must be between 0 and 23."})
        if self.minute > 59:
            raise ValidationError({"minute": "Minute must be between 0 and 59."})


class LmsSyncLog(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=LmsSyncStatus.choices,
        default=LmsSyncStatus.RUNNING,
    )
    students_created = models.PositiveIntegerField(default=0)
    students_updated = models.PositiveIntegerField(default=0)
    students_skipped = models.PositiveIntegerField(default=0)
    transcripts_created = models.PositiveIntegerField(default=0)
    transcripts_updated = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "lms_sync_logs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"LMS sync {self.started_at:%Y-%m-%d %H:%M} ({self.status})"
