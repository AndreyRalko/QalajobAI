from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'owner', 'industry', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'industry')
    search_fields = ('company_name', 'owner__email')
