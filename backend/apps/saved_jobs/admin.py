from django.contrib import admin

from .models import SavedHhVacancy, SavedJob


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "vacancy", "saved_at")
    search_fields = ("user__email", "user__username", "vacancy__title")


@admin.register(SavedHhVacancy)
class SavedHhVacancyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "company",
        "hh_id",
        "is_selected",
        "saved_at",
    )
    list_filter = ("is_selected",)
    search_fields = ("user__username", "title", "company", "hh_id")
