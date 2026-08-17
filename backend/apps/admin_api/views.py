from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import timedelta
from decimal import Decimal
import logging

from .models import UserBan, AuditLog, ModerationQueueItem, SystemSettings, AdminActionType
from .serializers import (
    UserBanSerializer,
    AuditLogSerializer,
    ModerationQueueItemSerializer,
    SystemSettingsSerializer,
    BanUserRequestSerializer,
    UnbanUserRequestSerializer,
    ModerationReviewRequestSerializer,
    DashboardStatsSerializer,
    LmsSyncLogSerializer,
    LmsSyncScheduleSerializer,
    AiActionLogSerializer,
)

logger = logging.getLogger(__name__)

class AdminViewSet(viewsets.ViewSet):
    """
    ViewSet для администраторских функций.
    
    Поддерживает:
    - Dashboard статистика
    - Управление пользователями (бан/разбан)
    - Модерация контента
    - Управление системными настройками
    - Логирование действий
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Получает статистику панели администратора.
        
        GET /api/admin/dashboard/
        """
        try:
            from django.db.models import Count
            from apps.applications.models import Application
            from apps.subscriptions.models import Subscription
            from apps.payments.models import Payment
            from apps.vacancies.models import Vacancy
            
            total_users = User.objects.count()
            banned_users = UserBan.objects.filter(is_permanent=True).count()
            total_applications = Application.objects.count()
            active_subscriptions = Subscription.objects.filter(is_active=True).count()
            pending_moderation = ModerationQueueItem.objects.filter(status='pending').count()
            
            # Получаем статистику вакансий
            total_vacancies = Vacancy.objects.count()
            
            # Получаем доход
            today_revenue = Payment.objects.filter(
                status='completed',
                created_at__date=timezone.now().date()
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0')
            
            month_start = timezone.now().replace(day=1)
            month_revenue = Payment.objects.filter(
                status='completed',
                created_at__gte=month_start
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0')
            
            data = {
                'total_users': total_users,
                'total_vacancies': total_vacancies,
                'total_applications': total_applications,
                'active_subscriptions': active_subscriptions,
                'pending_moderation': pending_moderation,
                'banned_users': banned_users,
                'revenue_today': str(today_revenue),
                'revenue_month': str(month_revenue),
                'system_status': 'operational'
            }
            
            serializer = DashboardStatsSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении статистики'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def ban_user(self, request):
        """
        Банит пользователя.
        
        POST /api/admin/ban-user/
        {
            "user_id": 123,
            "reason": "Violation of terms",
            "is_permanent": false,
            "ban_duration_days": 30
        }
        """
        try:
            serializer = BanUserRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=serializer.validated_data['user_id'])
            
            expires_at = None
            if not serializer.validated_data['is_permanent']:
                duration = serializer.validated_data.get('ban_duration_days', 30)
                expires_at = timezone.now() + timedelta(days=duration)
            
            ban, created = UserBan.objects.update_or_create(
                user=user,
                defaults={
                    'reason': serializer.validated_data['reason'],
                    'banned_by': request.user,
                    'expires_at': expires_at,
                    'is_permanent': serializer.validated_data['is_permanent']
                }
            )
            
            # Логируем действие
            AuditLog.objects.create(
                admin=request.user,
                action_type=AdminActionType.USER_BAN,
                target_user=user,
                details={
                    'reason': serializer.validated_data['reason'],
                    'is_permanent': serializer.validated_data['is_permanent'],
                    'expires_at': expires_at.isoformat() if expires_at else None
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f"Пользователь {user.id} забанен администратором {request.user.id}")
            
            return Response(
                UserBanSerializer(ban).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при бане пользователя: {str(e)}")
            return Response(
                {'error': 'Ошибка при бане пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def unban_user(self, request):
        """
        Разбанивает пользователя.
        
        POST /api/admin/unban-user/
        {
            "user_id": 123,
            "reason": "Appeal accepted"
        }
        """
        try:
            serializer = UnbanUserRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=serializer.validated_data['user_id'])
            ban = get_object_or_404(UserBan, user=user)
            
            # Логируем действие
            AuditLog.objects.create(
                admin=request.user,
                action_type=AdminActionType.USER_UNBAN,
                target_user=user,
                details={'reason': serializer.validated_data['reason']},
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Удаляем бан
            ban.delete()
            
            logger.info(f"Пользователь {user.id} разбанен администратором {request.user.id}")
            
            return Response(
                {'status': 'User unbanned successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при разбане пользователя: {str(e)}")
            return Response(
                {'error': 'Ошибка при разбане пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def moderation_queue(self, request):
        """
        Получает очередь модерации.
        
        GET /api/admin/moderation-queue/
        ?status=pending&item_type=vacancy
        """
        try:
            status_filter = request.query_params.get('status', 'pending')
            item_type = request.query_params.get('item_type')
            
            queue = ModerationQueueItem.objects.filter(status=status_filter)
            
            if item_type:
                queue = queue.filter(item_type=item_type)
            
            serializer = ModerationQueueItemSerializer(queue, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Ошибка при получении очереди модерации: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении очереди'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def review_moderation(self, request):
        """
        Рассматривает элемент модерации.
        
        POST /api/admin/review-moderation/
        {
            "moderation_id": 123,
            "decision": "approved",
            "notes": "Looks good"
        }
        """
        try:
            serializer = ModerationReviewRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            item = get_object_or_404(
                ModerationQueueItem,
                id=serializer.validated_data['moderation_id']
            )
            
            item.status = serializer.validated_data['decision']
            item.reviewed_at = timezone.now()
            item.reviewed_by = request.user
            item.notes = serializer.validated_data.get('notes', '')
            item.save()
            
            # Логируем действие
            action_type = AdminActionType.VACANCY_APPROVE if item.item_type == 'vacancy' else AdminActionType.VACANCY_REMOVE
            
            AuditLog.objects.create(
                admin=request.user,
                action_type=action_type,
                target_id=item.target_id,
                details={'decision': serializer.validated_data['decision']},
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f"Модерация {item.id} рассмотрена администратором {request.user.id}")
            
            return Response(
                ModerationQueueItemSerializer(item).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Ошибка при рассмотрении модерации: {str(e)}")
            return Response(
                {'error': 'Ошибка при рассмотрении модерации'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """
        Получает логи действий.
        
        GET /api/admin/audit-logs/
        ?action_type=user_ban&days=7
        """
        try:
            days = int(request.query_params.get('days', 30))
            action_type = request.query_params.get('action_type')
            admin_id = request.query_params.get('admin_id')
            
            start_date = timezone.now() - timedelta(days=days)
            logs = AuditLog.objects.filter(timestamp__gte=start_date)
            
            if action_type:
                logs = logs.filter(action_type=action_type)
            
            if admin_id:
                logs = logs.filter(admin_id=admin_id)
            
            serializer = AuditLogSerializer(logs.order_by('-timestamp'), many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Ошибка при получении логов: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении логов'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get', 'patch'])
    def system_settings(self, request):
        """
        Получает или обновляет системные настройки.
        
        GET /api/admin/system-settings/
        
        PATCH /api/admin/system-settings/
        {
            "maintenance_mode": true,
            "support_email": "support@example.com"
        }
        """
        try:
            settings, created = SystemSettings.objects.get_or_create(pk=1)
            
            if request.method == 'GET':
                serializer = SystemSettingsSerializer(settings)
                return Response(serializer.data)
            
            elif request.method == 'PATCH':
                serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    settings.updated_by = request.user
                    serializer.save()
                    
                    # Логируем изменение
                    AuditLog.objects.create(
                        admin=request.user,
                        action_type=AdminActionType.SYSTEM_SETTING_CHANGE,
                        details=request.data,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    logger.info(f"Системные настройки обновлены администратором {request.user.id}")
                    
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Ошибка при работе с системными настройками: {str(e)}")
            return Response(
                {'error': 'Ошибка при работе с настройками'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='lms-sync-logs')
    def lms_sync_logs(self, request):
        """
        Получает журнал ежедневных обновлений из LMS.

        GET /api/v1/admin-api/lms-sync-logs/?status=success&limit=50
        """
        try:
            from apps.lms_sync.models import LmsSyncLog

            status_filter = request.query_params.get('status')
            limit = min(int(request.query_params.get('limit', 50)), 200)

            logs = LmsSyncLog.objects.all()
            if status_filter:
                logs = logs.filter(status=status_filter)

            serializer = LmsSyncLogSerializer(logs[:limit], many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Ошибка при получении LMS sync logs: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении журнала LMS синхронизации'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='lms-sync-run')
    def lms_sync_run(self, request):
        """
        Запускает синхронизацию студентов и транскриптов из LMS.

        POST /api/v1/admin-api/lms-sync-run/
        { "full": false }
        """
        try:
            from apps.lms_sync.models import LmsSyncLog, LmsSyncStatus
            from apps.lms_sync.services.sync import run_lms_sync

            if LmsSyncLog.objects.filter(status=LmsSyncStatus.RUNNING).exists():
                return Response(
                    {'error': 'Синхронизация уже выполняется'},
                    status=status.HTTP_409_CONFLICT,
                )

            full = bool(request.data.get('full', False))
            log, stats = run_lms_sync(incremental=not full)
            serializer = LmsSyncLogSerializer(log)
            return Response({**serializer.data, **stats}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Ошибка при запуске LMS sync")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['get', 'put'], url_path='lms-sync-schedule')
    def lms_sync_schedule(self, request):
        """
        GET/PUT /api/v1/admin-api/lms-sync-schedule/
        """
        from apps.lms_sync.services.schedule import get_schedule_payload, update_schedule

        if request.method == 'GET':
            payload = get_schedule_payload()
            serializer = LmsSyncScheduleSerializer(instance=payload)
            return Response(serializer.data)

        serializer = LmsSyncScheduleSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        if 'enabled' not in data and 'hour' not in data and 'minute' not in data:
            return Response(
                {'error': 'Укажите enabled, hour и/или minute'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current = get_schedule_payload()
        try:
            payload = update_schedule(
                enabled=data.get('enabled', current['enabled']),
                hour=data.get('hour', current['hour']),
                minute=data.get('minute', current['minute']),
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LmsSyncScheduleSerializer(instance=payload).data)

    @action(detail=False, methods=['get'], url_path='ai-action-logs')
    def ai_action_logs(self, request):
        """
        GET /api/v1/admin-api/ai-action-logs/
        ?feature=resume_analysis&status=success&student_id=48958&login=ivan&days=7&limit=100
        """
        from apps.ai.models import AiActionLog

        try:
            logs = AiActionLog.objects.select_related('user').all()

            feature = request.query_params.get('feature')
            status_filter = request.query_params.get('status')
            student_id = request.query_params.get('student_id')
            login = request.query_params.get('login')
            days = request.query_params.get('days')

            if feature:
                logs = logs.filter(feature=feature)
            if status_filter:
                logs = logs.filter(status=status_filter)
            if student_id:
                logs = logs.filter(student_id=student_id)
            if login:
                logs = logs.filter(user_login__icontains=login)
            if days:
                try:
                    days_int = max(int(days), 1)
                    logs = logs.filter(created_at__gte=timezone.now() - timedelta(days=days_int))
                except ValueError:
                    pass

            limit = min(int(request.query_params.get('limit', 100)), 200)
            serializer = AiActionLogSerializer(logs[:limit], many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Ошибка при получении AI action logs: {str(e)}")
            return Response(
                {'error': 'Ошибка при получении журнала действий ИИ'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def _get_client_ip(self, request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip