from django.contrib import admin

from .models import LmsSyncLog, LmsSyncSchedule


@admin.register(LmsSyncSchedule)
class LmsSyncScheduleAdmin(admin.ModelAdmin):
    list_display = ("enabled", "hour", "minute", "last_scheduled_run", "updated_at")
    readonly_fields = ("last_scheduled_run", "updated_at")


@admin.register(LmsSyncLog)
class LmsSyncLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "started_at",
        "finished_at",
        "status",
        "students_created",
        "students_updated",
        "students_skipped",
    )
    readonly_fields = (
        "started_at",
        "finished_at",
        "status",
        "students_created",
        "students_updated",
        "students_skipped",
        "error_message",
    )
