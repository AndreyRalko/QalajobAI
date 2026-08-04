from django.contrib import admin
from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'city', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'is_approved', 'job_type')
    search_fields = ('title', 'company_name', 'employer__email')
