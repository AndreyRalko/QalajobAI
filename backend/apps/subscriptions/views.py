from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Subscription, SubscriptionHistory, SubscriptionPricing, SubscriptionPlan
from .serializers import (
    SubscriptionSerializer,
    SubscriptionHistorySerializer,
    SubscriptionPricingSerializer,
    SubscriptionUpgradeSerializer,
    SubscriptionDowngradeSerializer,
    SubscriptionCancelSerializer
)

logger = logging.getLogger(__name__)

class SubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet для управления подписками.
    
    Поддерживает:
    - Получение текущей подписки
    - Апгрейд/даунгрейд
    - Просмотр истории
    - Управление автопродлением
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Получает текущую подписку пользователя.
        
        GET /api/subscriptions/current/
        """
        try:
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Ошибка при получении подписки: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении подписки'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def plans(self, request):
        """
        Получает список доступных тарифов.
        
        GET /api/subscriptions/plans/
        """
        try:
            plans = SubscriptionPricing.objects.all()
            serializer = SubscriptionPricingSerializer(plans, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Ошибка при получении планов: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении планов'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """POST /api/v1/subscriptions/subscribe/ { plan, billing }"""
        try:
            plan = request.data.get('plan', 'premium')
            billing = request.data.get('billing', 'monthly')
            subscription, _ = Subscription.objects.get_or_create(user=request.user)
            subscription.plan = plan
            subscription.billing_period = billing
            subscription.is_active = True
            subscription.start_date = timezone.now()
            subscription.end_date = timezone.now() + (
                timedelta(days=365) if billing == 'yearly' else timedelta(days=30)
            )
            subscription.save()
            return Response({'data': SubscriptionSerializer(subscription).data})
        except Exception as e:
            logger.error(f"Subscribe error: {e}")
            return Response({'error': 'Subscription failed'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """
        Апгрейдит подписку на более высокий тариф.
        
        POST /api/subscriptions/upgrade/
        {
            "new_plan": "premium",
            "billing_period": "monthly"
        }
        """
        try:
            serializer = SubscriptionUpgradeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            new_plan = serializer.validated_data['new_plan']
            billing_period = serializer.validated_data.get('billing_period', 'monthly')
            
            # Проверяем что это действительно апгрейд
            plan_order = {SubscriptionPlan.FREE: 0, SubscriptionPlan.PREMIUM: 1, SubscriptionPlan.BUSINESS: 2}
            current_plan_level = plan_order.get(subscription.plan, 0)
            new_plan_level = plan_order.get(new_plan, 0)
            
            if new_plan_level <= current_plan_level:
                return Response(
                    {'error': 'Это не апгрейд. Используйте endpoint даунгрейда для снижения тарифа'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Сохраняем старый план в историю
            SubscriptionHistory.objects.create(
                user=request.user,
                plan=subscription.plan,
                status='expired',
                start_date=subscription.start_date,
                end_date=timezone.now()
            )
            
            # Обновляем подписку
            old_plan = subscription.plan
            subscription.plan = new_plan
            subscription.billing_period = billing_period
            subscription.start_date = timezone.now()
            
            # Устанавливаем конец периода
            if billing_period == 'yearly':
                subscription.end_date = timezone.now() + timedelta(days=365)
            else:
                subscription.end_date = timezone.now() + timedelta(days=30)
            
            subscription.is_active = True
            subscription.save()
            
            logger.info(f"Пользователь {request.user.id} апгрейдил подписку с {old_plan} на {new_plan}")
            
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при апгрейде подписки: {str(e)}")
            return Response(
                {'error': 'Ошибка при апгрейде подписки'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def downgrade(self, request):
        """
        Даунгрейдит подписку на более низкий тариф.
        
        POST /api/subscriptions/downgrade/
        {
            "new_plan": "free",
            "immediate": false
        }
        """
        try:
            serializer = SubscriptionDowngradeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            subscription, created = Subscription.objects.get_or_create(user=request.user)
            new_plan = serializer.validated_data['new_plan']
            immediate = serializer.validated_data.get('immediate', False)
            
            if immediate:
                # Немедленный даунгрейд
                SubscriptionHistory.objects.create(
                    user=request.user,
                    plan=subscription.plan,
                    status='cancelled',
                    start_date=subscription.start_date,
                    end_date=timezone.now()
                )
                
                subscription.plan = new_plan
                subscription.is_active = True
                subscription.start_date = timezone.now()
                subscription.end_date = timezone.now() + timedelta(days=30)
                subscription.save()
                
                logger.info(f"Пользователь {request.user.id} немедленно даунгрейдил подписку на {new_plan}")
            else:
                # Даунгрейд в конце периода
                subscription.plan = new_plan
                subscription.save()
                
                logger.info(f"Пользователь {request.user.id} запланировал даунгрейд на {new_plan} в конце периода")
            
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при даунгрейде подписки: {str(e)}")
            return Response(
                {'error': 'Ошибка при даунгрейде подписки'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """
        Отменяет подписку.
        
        POST /api/subscriptions/cancel/
        {
            "reason": "Не нужна больше",
            "feedback": "Спасибо"
        }
        """
        try:
            serializer = SubscriptionCancelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            subscription = get_object_or_404(Subscription, user=request.user)
            
            # Сохраняем в историю
            SubscriptionHistory.objects.create(
                user=request.user,
                plan=subscription.plan,
                status='cancelled',
                start_date=subscription.start_date,
                end_date=timezone.now()
            )
            
            # Переводим на free plan
            subscription.plan = SubscriptionPlan.FREE
            subscription.is_active = False
            subscription.auto_renew = False
            subscription.save()
            
            logger.info(f"Пользователь {request.user.id} отменил подписку")
            
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отмене подписки: {str(e)}")
            return Response(
                {'error': 'Ошибка при отмене подписки'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Получает историю подписок пользователя.
        
        GET /api/subscriptions/history/
        """
        try:
            history = SubscriptionHistory.objects.filter(user=request.user).order_by('-created_at')
            serializer = SubscriptionHistorySerializer(history, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Ошибка при получении истории подписок: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении истории'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def toggle_auto_renew(self, request):
        """
        Включает/отключает автопродление.
        
        POST /api/subscriptions/toggle_auto_renew/
        {
            "auto_renew": true
        }
        """
        try:
            subscription = get_object_or_404(Subscription, user=request.user)
            auto_renew = request.data.get('auto_renew', True)
            
            subscription.auto_renew = auto_renew
            subscription.save()
            
            status_text = "включено" if auto_renew else "отключено"
            logger.info(f"Автопродление {status_text} для пользователя {request.user.id}")
            
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при изменении автопродления: {str(e)}")
            return Response(
                {'error': 'Ошибка при изменении автопродления'},
                status=status.HTTP_400_BAD_REQUEST
            )