from django.contrib import admin
from .models import SavedJob


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'vacancy', 'saved_at')
    search_fields = ('user__email', 'vacancy__title')
