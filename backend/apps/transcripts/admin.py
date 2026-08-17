from django.contrib import admin

from .models import Transcript


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "subject_code",
        "subject_name_ru",
        "credits",
        "alpha_mark",
        "total_mark",
        "course_number",
        "term",
    )
    list_filter = ("course_number", "term", "alpha_mark", "type")
    search_fields = (
        "student_id",
        "subject_code",
        "subject_name_ru",
        "subject_name_kz",
        "subject_name_en",
    )
    ordering = ("student_id", "course_number", "term", "subject_code")
