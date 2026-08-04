from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
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