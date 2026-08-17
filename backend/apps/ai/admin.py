from django.contrib import admin

from .models import AiActionLog


@admin.register(AiActionLog)
class AiActionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "user_login",
        "student_id",
        "feature",
        "endpoint",
        "status",
        "duration_ms",
    )
    list_filter = ("feature", "status", "created_at")
    search_fields = ("user_login", "student_id", "endpoint", "ai_output")
    readonly_fields = (
        "user",
        "student_id",
        "user_login",
        "feature",
        "endpoint",
        "status",
        "model_name",
        "duration_ms",
        "request_payload",
        "ai_input",
        "ai_output",
        "error_message",
        "created_at",
    )
