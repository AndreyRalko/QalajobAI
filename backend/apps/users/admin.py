from django.contrib import admin
from .models import UserActivityLog, UserProfile


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user_login", "action", "path", "user")
    list_filter = ("action", "created_at")
    search_fields = ("user_login", "path", "ip_address")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "student_id",
        "language",
        "is_banned",
        "email_verified",
        "created_at",
    )

    list_filter = (
        "role",
        "is_banned",
        "language",
        "email_verified",
    )

    search_fields = (
        "user__username",
        "user__email",
        "student_id",
        "phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "user",
                    "role",
                    "student_id",
                    "language",
                )
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "phone",
                    "photo_url",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_banned",
                    "email_verified",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )