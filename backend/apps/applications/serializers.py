from rest_framework import serializers
from .models import (
    Application, ApplicationHistory, ApplicationNotification, 
    ApplicationStatistics, ApplicationStatus
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ApplicationHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ApplicationHistory
        fields = ['id', 'status', 'status_display', 'changed_by', 'changed_by_email', 'changed_at', 'notes']
        read_only_fields = ['changed_at']

class ApplicationNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationNotification
        fields = ['id', 'notification_type', 'message', 'is_read', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    history = ApplicationHistorySerializer(read_only=True, many=True)
    notifications = ApplicationNotificationSerializer(read_only=True, many=True)
    can_withdraw = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'candidate_email', 'vacancy_id', 'employer_id', 
            'status', 'status_display', 'cover_letter', 'resume_file', 'notes', 
            'interview_date', 'rejection_reason', 'applied_at', 'updated_at', 
            'withdrawn_at', 'history', 'notifications', 'can_withdraw'
        ]
        read_only_fields = ['id', 'candidate', 'applied_at', 'updated_at', 'withdrawn_at', 'history', 'notifications']
    
    def get_can_withdraw(self, obj):
        return obj.can_withdraw()

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['vacancy_id', 'cover_letter', 'resume_file']

class ApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    interview_date = serializers.DateTimeField(required=False, allow_null=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

class ApplicationStatisticsSerializer(serializers.ModelSerializer):
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationStatistics
        fields = [
            'total_applications', 'pending_count', 'reviewing_count', 
            'interview_count', 'accepted_count', 'rejected_count', 
            'withdrawn_count', 'success_rate', 'updated_at'
        ]
        read_only_fields = '__all__'
    
    def get_success_rate(self, obj):
        if obj.total_applications == 0:
            return 0
        return round((obj.accepted_count / obj.total_applications) * 100, 2)