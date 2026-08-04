"""Audit log API views for admin dashboard."""

import logging
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog

logger = logging.getLogger('apps')


class AuditLogListView(APIView):
    """List audit logs with filtering."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        action_filter = request.query_params.get('action')
        limit = int(request.query_params.get('limit', 50))

        qs = AuditLog.objects.all()

        if action_filter:
            qs = qs.filter(action=action_filter)

        logs = qs[:limit]

        data = [
            {
                'id': log.id,
                'admin': log.admin.email if log.admin else 'system',
                'action': log.action,
                'target_type': log.target_type,
                'target_id': log.target_id,
                'target_label': log.target_label,
                'details': log.details,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat(),
            }
            for log in logs
        ]

        return Response({'results': data, 'count': len(data)})
