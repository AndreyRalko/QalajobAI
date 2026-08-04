from django.contrib import admin
from .models import (
    Subscription,
    SubscriptionHistory,
    SubscriptionPricing
)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "billing_period",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = (
        "plan",
        "is_active",
        "billing_period",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "start_date",
        "created_at",
        "updated_at",
    )


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "start_date",
        "end_date",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


@admin.register(SubscriptionPricing)
class SubscriptionPricingAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "monthly_price",
        "yearly_price",
        "currency",
        "updated_at",
    )

    search_fields = (
        "plan",
    )

    readonly_fields = (
        "updated_at",
    )