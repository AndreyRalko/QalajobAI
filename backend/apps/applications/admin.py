from django.contrib import admin
from .models import (
    Application,
    ApplicationHistory,
    ApplicationNotification,
    ApplicationStatistics
)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "candidate",
        "vacancy_id",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
        "applied_at",
    )

    search_fields = (
        "candidate__email",
        "vacancy_id",
        "employer_id",
    )

    readonly_fields = (
        "applied_at",
        "updated_at",
    )


@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "status",
        "changed_by",
        "changed_at",
    )

    list_filter = (
        "status",
        "changed_at",
    )

    search_fields = (
        "application__candidate__email",
    )


@admin.register(ApplicationNotification)
class ApplicationNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "recipient",
        "notification_type",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "created_at",
    )

    search_fields = (
        "recipient__email",
    )


@admin.register(ApplicationStatistics)
class ApplicationStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "total_applications",
        "accepted_count",
        "rejected_count",
        "updated_at",
    )

    readonly_fields = (
        "total_applications",
        "pending_count",
        "reviewing_count",
        "interview_count",
        "accepted_count",
        "rejected_count",
        "withdrawn_count",
        "updated_at",
    )