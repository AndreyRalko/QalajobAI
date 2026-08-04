from rest_framework import serializers
from apps.vacancies.serializers import VacancySerializer
from .models import SavedJob


class SavedJobSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SavedJob
        fields = ['id', 'vacancy', 'vacancy_id', 'saved_at']
        read_only_fields = ['id', 'saved_at']
