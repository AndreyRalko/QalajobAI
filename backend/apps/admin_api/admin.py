from django.contrib import admin
from .models import UserBan, AuditLog, ModerationQueueItem, SystemSettings

@admin.register(UserBan)
class UserBanAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason', 'banned_by', 'banned_at', 'is_permanent')
    list_filter = ('is_permanent', 'banned_at')
    search_fields = ('user__email', 'reason')
    readonly_fields = ('banned_at',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action_type', 'target_user', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('admin__email', 'target_user__email')
    readonly_fields = ('timestamp',)

@admin.register(ModerationQueueItem)
class ModerationQueueItemAdmin(admin.ModelAdmin):
    list_display = ('item_type', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('status', 'item_type', 'submitted_at')
    search_fields = ('target_id', 'reason')
    readonly_fields = ('submitted_at', 'reviewed_at')

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('maintenance_mode', 'default_currency', 'updated_at')
    readonly_fields = ('updated_at',)