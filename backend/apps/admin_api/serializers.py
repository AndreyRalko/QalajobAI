from rest_framework import serializers
from django.contrib.auth.models import User
from apps.lms_sync.models import LmsSyncLog
from apps.ai.models import AiActionLog
from .models import UserBan, AuditLog, ModerationQueueItem, SystemSettings

class UserBanSerializer(serializers.ModelSerializer):
    banned_by_username = serializers.CharField(source='banned_by.username', read_only=True)
    is_active_ban = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBan
        fields = [
            'id', 'user', 'reason', 'banned_by', 'banned_by_username',
            'banned_at', 'expires_at', 'is_permanent', 'is_active_ban'
        ]
        read_only_fields = ['id', 'banned_by', 'banned_at']
    
    def get_is_active_ban(self, obj):
        return obj.is_active()

class AuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'admin', 'admin_username', 'action_type', 'target_user',
            'target_username', 'target_id', 'details', 'timestamp',
            'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'admin', 'timestamp', 'ip_address', 'user_agent']

class ModerationQueueItemSerializer(serializers.ModelSerializer):
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = ModerationQueueItem
        fields = [
            'id', 'item_type', 'target_id', 'reason', 'status',
            'submitted_at', 'reviewed_at', 'reviewed_by', 'reviewed_by_username', 'notes'
        ]
        read_only_fields = ['id', 'submitted_at']

class SystemSettingsSerializer(serializers.ModelSerializer):
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = SystemSettings
        fields = [
            'id', 'maintenance_mode', 'max_upload_size', 'default_currency',
            'support_email', 'terms_version', 'privacy_version',
            'updated_at', 'updated_by', 'updated_by_username'
        ]
        read_only_fields = ['id', 'updated_at', 'updated_by']

# Request serializers

class BanUserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)
    is_permanent = serializers.BooleanField(default=False)
    ban_duration_days = serializers.IntegerField(
        required=False,
        help_text="Количество дней на которые банить пользователя (если не перманентный)"
    )

class UnbanUserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=500)

class ModerationReviewRequestSerializer(serializers.Serializer):
    DECISION_CHOICES = [
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    moderation_id = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    notes = serializers.CharField(max_length=1000, required=False)

class DashboardStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики панели"""
    total_users = serializers.IntegerField()
    total_vacancies = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    pending_moderation = serializers.IntegerField()
    banned_users = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_month = serializers.DecimalField(max_digits=10, decimal_places=2)
    system_status = serializers.CharField()


class LmsSyncLogSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = LmsSyncLog
        fields = [
            "id",
            "started_at",
            "finished_at",
            "duration_seconds",
            "status",
            "students_created",
            "students_updated",
            "students_skipped",
            "transcripts_created",
            "transcripts_updated",
            "error_message",
        ]

    def get_duration_seconds(self, obj):
        if not obj.finished_at:
            return None
        delta = obj.finished_at - obj.started_at
        return max(int(delta.total_seconds()), 0)


class LmsSyncScheduleSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    hour = serializers.IntegerField(min_value=0, max_value=23)
    minute = serializers.IntegerField(min_value=0, max_value=59)
    time = serializers.CharField(read_only=True)
    timezone = serializers.CharField(read_only=True)
    last_scheduled_run = serializers.DateTimeField(read_only=True, allow_null=True)
    next_run_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AiActionLogSerializer(serializers.ModelSerializer):
    feature_label = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AiActionLog
        fields = [
            "id",
            "created_at",
            "user_name",
            "user_login",
            "student_id",
            "feature",
            "feature_label",
            "endpoint",
            "status",
            "model_name",
            "provider",
            "duration_ms",
            "request_payload",
            "ai_input",
            "ai_output",
            "error_message",
        ]

    def get_feature_label(self, obj):
        from apps.ai.models import AIFeatureType

        try:
            return AIFeatureType(obj.feature).label
        except ValueError:
            return obj.feature

    def get_user_name(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or obj.user_login or str(obj.user_id)