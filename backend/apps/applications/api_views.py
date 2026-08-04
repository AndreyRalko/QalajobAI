from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsStudent, IsEmployer
from apps.vacancies.models import Vacancy
from .models import Application, ApplicationHistory, ApplicationStatistics, ApplicationStatus
from .serializers import ApplicationCreateSerializer, ApplicationSerializer


class ApplyView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        vacancy_id = request.data.get('vacancyId') or request.data.get('vacancy_id')
        if not vacancy_id:
            return Response({'message': 'vacancyId required'}, status=status.HTTP_400_BAD_REQUEST)

        vacancy = Vacancy.objects.filter(pk=vacancy_id).first()
        if not vacancy:
            return Response({'message': 'Vacancy not found'}, status=status.HTTP_404_NOT_FOUND)

        if vacancy.employer_id == request.user.id:
            return Response({'message': 'Cannot apply to own vacancy'}, status=status.HTTP_400_BAD_REQUEST)

        if Application.objects.filter(candidate=request.user, vacancy_id=str(vacancy_id)).exists():
            return Response({'message': 'Already applied'}, status=status.HTTP_400_BAD_REQUEST)

        application = Application.objects.create(
            candidate=request.user,
            vacancy_id=str(vacancy_id),
            employer_id=str(vacancy.employer_id),
            cover_letter=request.data.get('coverLetter', ''),
            status=ApplicationStatus.PENDING,
        )
        ApplicationHistory.objects.create(
            application=application,
            status=ApplicationStatus.PENDING,
            changed_by=request.user,
            notes='Application submitted',
        )
        stats, _ = ApplicationStatistics.objects.get_or_create(candidate=request.user)
        stats.refresh()

        return Response({'data': ApplicationSerializer(application).data}, status=status.HTTP_201_CREATED)


class StudentApplicationsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        apps = Application.objects.filter(candidate=request.user).order_by('-applied_at')
        return Response({'data': ApplicationSerializer(apps, many=True).data})


class EmployerApplicationsView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request):
        apps = Application.objects.filter(employer_id=str(request.user.id)).order_by('-applied_at')
        return Response({'data': ApplicationSerializer(apps, many=True).data})
