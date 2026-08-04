from django.contrib import admin
from .models import Payment, PaymentHistory, Invoice

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('payment', 'changed_at', 'old_status', 'new_status')
    list_filter = ('changed_at',)
    search_fields = ('payment__user__email',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('payment', 'invoice_number', 'amount', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('invoice_number',)