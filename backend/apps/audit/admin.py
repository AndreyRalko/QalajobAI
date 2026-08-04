from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'admin', 'action', 'target_label', 'ip_address']
    list_filter = ['action', 'created_at']
    search_fields = ['target_label', 'admin__email', 'ip_address']
    readonly_fields = ['admin', 'action', 'target_type', 'target_id', 'target_label',
                       'details', 'ip_address', 'user_agent', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
