from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsStudent
from apps.vacancies.models import Vacancy
from .models import SavedJob
from .serializers import SavedJobSerializer


class SavedJobViewSet(viewsets.ModelViewSet):
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related('vacancy')

    def create(self, request, *args, **kwargs):
        vacancy_id = request.data.get('vacancy_id') or request.data.get('vacancyId')
        if not vacancy_id:
            return Response({'message': 'vacancy_id required'}, status=status.HTTP_400_BAD_REQUEST)
        vacancy = Vacancy.objects.filter(pk=vacancy_id).first()
        if not vacancy:
            return Response({'message': 'Vacancy not found'}, status=status.HTTP_404_NOT_FOUND)
        saved, created = SavedJob.objects.get_or_create(user=request.user, vacancy=vacancy)
        return Response(
            {'data': SavedJobSerializer(saved).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
