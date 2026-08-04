from rest_framework import serializers
from .models import Subscription, SubscriptionHistory, SubscriptionPricing

class SubscriptionSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'billing_period', 
            'start_date', 'end_date', 'is_active', 
            'auto_renew', 'features', 'is_expired', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_features(self, obj):
        return obj.get_features()
    
    def get_is_expired(self, obj):
        return obj.is_expired()

class SubscriptionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = [
            'id', 'user', 'plan', 'status', 
            'start_date', 'end_date', 'payment_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SubscriptionPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPricing
        fields = [
            'id', 'plan', 'monthly_price', 'yearly_price', 
            'currency', 'description', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

class SubscriptionUpgradeSerializer(serializers.Serializer):
    new_plan = serializers.CharField(
        max_length=20,
        help_text="Новый тариф (free, premium, business)"
    )
    billing_period = serializers.CharField(
        max_length=20,
        default='monthly',
        help_text="Период биллинга (monthly, yearly)"
    )

class SubscriptionDowngradeSerializer(serializers.Serializer):
    new_plan = serializers.CharField(
        max_length=20,
        help_text="Новый тариф (free, premium, business)"
    )
    immediate = serializers.BooleanField(
        default=False,
        help_text="Применить немедленно или с конца текущего периода"
    )

class SubscriptionCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Причина отмены"
    )
    feedback = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Обратная связь"
    )