from django.contrib import admin

from .models import (
    StudentProfile,
    EmployerProfile,
    AdminProfile,
)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "university",
        "city",
        "ai_score",
    )
    search_fields = (
        "user__email",
        "name",
        "university",
    )


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "position",
        "phone",
    )
    search_fields = (
        "user__email",
        "full_name",
        "position",
    )


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
    )
    search_fields = (
        "user__email",
        "full_name",
    )