"""
Analytics Views — Platform statistics and chart data for admin dashboard.
"""

import logging
from datetime import timedelta, date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.vacancies.models import Vacancy
from apps.subscriptions.models import Subscription
from apps.payments.models import Payment
from apps.users.models import UserProfile
from .models import DailyMetric

logger = logging.getLogger('apps')


class DashboardStatsView(APIView):
    """Get overview stats for admin dashboard."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            today = timezone.now().date()
            month_start = today.replace(day=1)

            total_users = User.objects.count()
            students = UserProfile.objects.filter(role='student').count()
            employers = UserProfile.objects.filter(role='employer').count()
            total_vacancies = Vacancy.objects.count()
            total_applications = Application.objects.count()
            active_subscriptions = Subscription.objects.filter(is_active=True).count()

            today_revenue = Payment.objects.filter(
                status='completed',
                created_at__date=today,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            month_revenue = Payment.objects.filter(
                status='completed',
                created_at__date__gte=month_start,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            new_today = User.objects.filter(date_joined__date=today).count()

            return Response({
                'total_users': total_users,
                'students': students,
                'employers': employers,
                'total_vacancies': total_vacancies,
                'total_applications': total_applications,
                'active_subscriptions': active_subscriptions,
                'today_revenue': str(today_revenue),
                'month_revenue': str(month_revenue),
                'new_users_today': new_today,
                'system_status': 'operational',
            })
        except Exception as e:
            logger.error(f"Dashboard stats error: {e}")
            return Response({'message': 'Error fetching stats'}, status=500)


class ChartDataView(APIView):
    """Get chart data for analytics page."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        chart_type = request.query_params.get('type', 'users')

        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            labels = []
            data = []

            current = start_date
            while current <= end_date:
                labels.append(current.isoformat())

                if chart_type == 'users':
                    count = User.objects.filter(date_joined__date=current).count()
                elif chart_type == 'applications':
                    count = Application.objects.filter(applied_at__date=current).count()
                elif chart_type == 'vacancies':
                    count = Vacancy.objects.filter(created_at__date=current).count()
                elif chart_type == 'revenue':
                    total = Payment.objects.filter(
                        status='completed',
                        created_at__date=current,
                    ).aggregate(total=Sum('amount'))['total']
                    count = float(total or 0)
                else:
                    count = 0

                data.append(count)
                current += timedelta(days=1)

            return Response({
                'labels': labels,
                'data': data,
                'chart_type': chart_type,
            })
        except Exception as e:
            logger.error(f"Chart data error: {e}")
            return Response({'message': 'Error fetching chart data'}, status=500)


class GrowthMetricsView(APIView):
    """Get growth metrics: daily/monthly active users, growth rates."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            today = date.today()
            last_week = today - timedelta(days=7)
            last_month = today - timedelta(days=30)
            prev_month = today - timedelta(days=60)

            this_month_users = User.objects.filter(
                date_joined__date__gte=last_month,
            ).count()

            prev_month_users = User.objects.filter(
                date_joined__date__gte=prev_month,
                date_joined__date__lt=last_month,
            ).count()

            growth_rate = 0
            if prev_month_users > 0:
                growth_rate = round(
                    ((this_month_users - prev_month_users) / prev_month_users) * 100, 1
                )

            return Response({
                'this_month_users': this_month_users,
                'prev_month_users': prev_month_users,
                'growth_rate': growth_rate,
                'weekly_signups': User.objects.filter(
                    date_joined__date__gte=last_week
                ).count(),
                'total_users': User.objects.count(),
            })
        except Exception as e:
            logger.error(f"Growth metrics error: {e}")
            return Response({'message': 'Error fetching growth metrics'}, status=500)
