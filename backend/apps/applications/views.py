from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import Application, ApplicationHistory, ApplicationStatistics, ApplicationStatus
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer, 
    ApplicationStatusUpdateSerializer, ApplicationStatisticsSerializer,
    ApplicationHistorySerializer
)
from .permissions import IsApplicationCandidate, IsApplicationEmployer

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'vacancy_id', 'employer_id']
    search_fields = ['candidate__email', 'cover_letter', 'notes']
    ordering_fields = ['applied_at', 'updated_at', 'status']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        user = self.request.user
        is_employer = self.request.query_params.get('as_employer', False)
        
        if is_employer:
            return Application.objects.filter(employer_id=user.id)
        return Application.objects.filter(candidate=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        employer_id = self.request.data.get('employer_id', '')
        
        # Check if already applied
        if Application.objects.filter(
            candidate=user,
            vacancy_id=serializer.validated_data['vacancy_id']
        ).exists():
            raise serializers.ValidationError('Вы уже подали заявку на эту вакансию')
        
        application = serializer.save(candidate=user, employer_id=employer_id)
        
        # Create initial history entry
        ApplicationHistory.objects.create(
            application=application,
            status=ApplicationStatus.PENDING,
            changed_by=user,
            notes='Заявка подана'
        )
        
        # Update or create statistics
        stats, _ = ApplicationStatistics.objects.get_or_create(candidate=user)
        stats.refresh()
    
    @action(detail=True, methods=['post'], permission_classes=[IsApplicationCandidate])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        
        if application.candidate != request.user:
            return Response(
                {'error': 'Вы не можете отозвать эту заявку'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if application.withdraw():
            ApplicationHistory.objects.create(
                application=application,
                status=ApplicationStatus.WITHDRAWN,
                changed_by=request.user,
                notes='Заявка отозвана кандидатом'
            )
            
            stats = ApplicationStatistics.objects.get(candidate=request.user)
            stats.refresh()
            
            return Response(
                {'status': 'withdrawn', 'message': 'Заявка успешно отозвана'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Невозможно отозвать заявку в текущем статусе'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsApplicationEmployer])
    def update_status(self, request, pk=None):
        application = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = application.status
        new_status = serializer.validated_data['status']
        
        application.status = new_status
        
        if new_status == ApplicationStatus.INTERVIEW:
            application.interview_date = serializer.validated_data.get('interview_date')
        elif new_status == ApplicationStatus.REJECTED:
            application.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        
        application.save()
        
        # Create history entry
        ApplicationHistory.objects.create(
            application=application,
            status=new_status,
            changed_by=request.user,
            notes=serializer.validated_data.get('notes', f'Статус изменён с {old_status} на {new_status}')
        )
        
        # Update candidate statistics
        stats = ApplicationStatistics.objects.get(candidate=application.candidate)
        stats.refresh()
        
        return Response(
            ApplicationSerializer(application).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        stats, _ = ApplicationStatistics.objects.get_or_create(candidate=user)
        stats.refresh()
        serializer = ApplicationStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        application = self.get_object()
        history = application.history.all()
        serializer = ApplicationHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def employer_applications(self, request):
        employer_id = request.query_params.get('employer_id')
        if not employer_id:
            return Response(
                {'error': 'employer_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = Application.objects.filter(employer_id=employer_id)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vacancy_applications(self, request):
        vacancy_id = request.query_params.get('vacancy_id')
        if not vacancy_id:
            return Response(
                {'error': 'vacancy_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = Application.objects.filter(vacancy_id=vacancy_id)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)