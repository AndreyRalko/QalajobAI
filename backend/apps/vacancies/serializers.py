from rest_framework import serializers
from .models import Vacancy


class VacancySerializer(serializers.ModelSerializer):
    employer_id = serializers.IntegerField(source='employer.id', read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            'id', 'employer_id', 'title', 'company_name', 'salary', 'city',
            'location', 'phone', 'job_type', 'description', 'requirements',
            'benefits', 'status', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employer_id', 'is_approved', 'created_at', 'updated_at']


class VacancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'company_name', 'salary', 'city', 'location', 'phone',
            'job_type', 'description', 'requirements', 'benefits',
        ]
