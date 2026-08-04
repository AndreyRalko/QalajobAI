from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'ai_score', 'updated_at')
    search_fields = ('user__email',)
