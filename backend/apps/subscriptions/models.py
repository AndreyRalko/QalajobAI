from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.TextChoices):
    FREE = 'free', 'Бесплатный'
    PREMIUM = 'premium', 'Премиум'
    BUSINESS = 'business', 'Бизнес'

class Subscription(models.Model):
    BILLING_PERIODS = (
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.FREE)
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIODS, default='monthly')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_expired(self):
        if not self.end_date:
            return False
        return timezone.now() > self.end_date
    
    def get_features(self):
        # All features are free — no paid plan gates.
        return {
            'max_applications_per_month': 999999,
            'max_saved_vacancies': 999999,
            'ai_matching_enabled': True,
            'resume_analysis_enabled': True,
            'interview_prep_enabled': True,
            'advanced_filters_enabled': True,
            'profile_badge_enabled': True,
            'priority_support_enabled': True,
        }
    
    class Meta:
        ordering = ['-created_at']

class SubscriptionHistory(models.Model):
    STATUS_CHOICES = (
        ('active', 'Активная'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_history')
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class SubscriptionPricing(models.Model):
    BILLING_PERIODS = (
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно'),
    )
    
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KZT')
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Subscription Pricing'