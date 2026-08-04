from rest_framework import serializers
from .models import Payment, PaymentHistory, Invoice

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'status', 'created_at']

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['id', 'payment', 'changed_at', 'old_status', 'new_status']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'payment', 'invoice_number', 'amount', 'issued_at']