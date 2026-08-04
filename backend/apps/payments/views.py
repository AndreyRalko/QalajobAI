from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
import stripe
import logging

from .models import Payment, PaymentHistory, Invoice
from .serializers import PaymentSerializer, PaymentHistorySerializer, InvoiceSerializer
from ..subscriptions.models import Subscription, SubscriptionPricing

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.
    
    Поддерживает:
    - Создание платежей через Stripe, Kaspi, Halyk
    - Подтверждение платежей
    - Историю платежей
    - Управление счетами
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователь видит только свои платежи"""
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """
        Создает intent для платежа.
        
        POST /api/payments/create-intent/
        {
            "amount": 9999,
            "currency": "KZT",
            "subscription_plan": "premium",
            "payment_provider": "stripe"
        }
        """
        try:
            amount = Decimal(str(request.data.get('amount')))
            currency = request.data.get('currency', 'KZT')
            subscription_plan = request.data.get('subscription_plan')
            payment_provider = request.data.get('payment_provider', 'stripe')
            
            if amount <= 0:
                return Response(
                    {'error': 'Сумма должна быть больше 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем платеж в БД
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                status='pending',
                payment_provider=payment_provider,
                subscription_plan=subscription_plan
            )
            
            # В зависимости от провайдера
            if payment_provider == 'stripe':
                intent_data = self._create_stripe_intent(payment, amount, currency)
            elif payment_provider == 'kaspi':
                intent_data = self._create_kaspi_intent(payment, amount, currency)
            elif payment_provider == 'halyk':
                intent_data = self._create_halyk_intent(payment, amount, currency)
            else:
                return Response(
                    {'error': 'Неподдерживаемый провайдер платежей'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'payment_id': payment.id,
                **intent_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Ошибка при создании intent: {str(e)}")
            return Response(
                {'error': 'Ошибка при создании платежа'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Подтверждает платеж.
        
        POST /api/payments/confirm/
        {
            "payment_id": 123,
            "stripe_payment_intent_id": "pi_xxx"
        }
        """
        try:
            payment_id = request.data.get('payment_id')
            payment = get_object_or_404(Payment, id=payment_id, user=request.user)
            
            if payment.status != 'pending':
                return Response(
                    {'error': 'Платеж не в статусе pending'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Подтверждаем платеж в зависимости от провайдера
            if payment.payment_provider == 'stripe':
                success = self._confirm_stripe_payment(payment, request.data)
            elif payment.payment_provider == 'kaspi':
                success = self._confirm_kaspi_payment(payment, request.data)
            elif payment.payment_provider == 'halyk':
                success = self._confirm_halyk_payment(payment, request.data)
            else:
                return Response(
                    {'error': 'Неподдерживаемый провайдер'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if success:
                # Обновляем статус платежа
                old_status = payment.status
                payment.status = 'completed'
                payment.save()
                
                # Создаем запись в истории
                PaymentHistory.objects.create(
                    payment=payment,
                    old_status=old_status,
                    new_status='completed'
                )
                
                # Активируем подписку если это платеж за подписку
                if payment.subscription_plan:
                    self._activate_subscription(request.user, payment.subscription_plan)
                
                # Создаем счет
                invoice = self._create_invoice(payment)
                
                return Response({
                    'payment': PaymentSerializer(payment).data,
                    'invoice': InvoiceSerializer(invoice).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Ошибка при подтверждении платежа'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Ошибка при подтверждении платежа: {str(e)}")
            return Response(
                {'error': 'Ошибка при подтверждении платежа'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Получает историю платежей пользователя.
        
        GET /api/payments/history/
        """
        payments = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def invoices(self, request):
        """
        Получает счета пользователя.
        
        GET /api/payments/invoices/
        """
        payments = self.get_queryset()
        invoices = Invoice.objects.filter(payment__in=payments)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    def _create_stripe_intent(self, payment, amount, currency):
        """Создает Stripe PaymentIntent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # В центах
                currency=currency.lower(),
                metadata={
                    'payment_id': payment.id,
                    'user_id': payment.user.id
                }
            )
            
            payment.stripe_payment_intent_id = intent.id
            payment.save()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise
    
    def _create_kaspi_intent(self, payment, amount, currency):
        """Создает Kaspi платеж"""
        # TODO: Реализовать интеграцию с Kaspi
        return {
            'kaspi_url': f'https://kaspi.kz/pay/{payment.id}',
            'payment_id': payment.id
        }
    
    def _create_halyk_intent(self, payment, amount, currency):
        """Создает Halyk платеж"""
        # TODO: Реализовать интеграцию с Halyk
        return {
            'halyk_url': f'https://halyk.kz/pay/{payment.id}',
            'payment_id': payment.id
        }
    
    def _confirm_stripe_payment(self, payment, data):
        """Подтверждает платеж Stripe"""
        try:
            intent_id = data.get('stripe_payment_intent_id')
            if not intent_id:
                return False
            
            intent = stripe.PaymentIntent.retrieve(intent_id)
            
            if intent.status == 'succeeded':
                return True
            return False
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return False
    
    def _confirm_kaspi_payment(self, payment, data):
        """Подтверждает платеж Kaspi"""
        # TODO: Реализовать проверку статуса Kaspi
        return True
    
    def _confirm_halyk_payment(self, payment, data):
        """Подтверждает платеж Halyk"""
        # TODO: Реализовать проверку статуса Halyk
        return True
    
    def _activate_subscription(self, user, plan_name):
        """Активирует подписку пользователя"""
        try:
            pricing = SubscriptionPricing.objects.get(plan=plan_name)
            subscription, created = Subscription.objects.get_or_create(user=user)
            
            subscription.plan = plan_name
            subscription.started_at = timezone.now()
            subscription.expires_at = timezone.now() + timezone.timedelta(days=pricing.billing_cycle_days)
            subscription.is_active = True
            subscription.save()
            
            logger.info(f"Подписка активирована для пользователя {user.id}")
        except Exception as e:
            logger.error(f"Ошибка при активации подписки: {str(e)}")
    
    def _create_invoice(self, payment):
        """Создает счет для платежа"""
        import uuid
        
        invoice_number = f"INV-{payment.id}-{uuid.uuid4().hex[:8].upper()}"
        
        invoice = Invoice.objects.create(
            payment=payment,
            invoice_number=invoice_number,
            amount=payment.amount
        )
        
        return invoice