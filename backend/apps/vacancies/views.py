from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.users.permissions import IsEmployer, IsAdminRole
from .models import Vacancy, VacancyStatus
from .serializers import VacancySerializer, VacancyCreateSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city', 'job_type', 'status']
    search_fields = ['title', 'company_name', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsEmployer()]
        if self.action in ['destroy', 'pause', 'archive', 'approve', 'reject']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return VacancyCreateSerializer
        return VacancySerializer

    def get_queryset(self):
        qs = Vacancy.objects.select_related('employer')
        if self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated:
            return qs.filter(status=VacancyStatus.ACTIVE, is_approved=True)
        if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'employer':
            mine = self.request.query_params.get('mine')
            if mine == 'true':
                return qs.filter(employer=self.request.user)
        if self.request.user.is_staff or (
            hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'admin'
        ):
            return qs
        return qs.filter(status=VacancyStatus.ACTIVE, is_approved=True)

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        vacancy = self.get_object()
        if vacancy.employer != request.user and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        vacancy.status = VacancyStatus.PAUSED
        vacancy.save(update_fields=['status', 'updated_at'])
        return Response({'data': VacancySerializer(vacancy).data})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        vacancy = self.get_object()
        if vacancy.employer != request.user and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        vacancy.status = VacancyStatus.ARCHIVED
        vacancy.save(update_fields=['status', 'updated_at'])
        return Response({'data': VacancySerializer(vacancy).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminRole])
    def approve(self, request, pk=None):
        vacancy = self.get_object()
        vacancy.is_approved = True
        vacancy.status = VacancyStatus.ACTIVE
        vacancy.save(update_fields=['is_approved', 'status', 'updated_at'])
        return Response({'data': VacancySerializer(vacancy).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminRole])
    def reject(self, request, pk=None):
        vacancy = self.get_object()
        vacancy.is_approved = False
        vacancy.status = VacancyStatus.REJECTED
        vacancy.save(update_fields=['is_approved', 'status', 'updated_at'])
        return Response({'data': VacancySerializer(vacancy).data})
