from rest_framework import serializers
from .models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    completion = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            'name', 'university', 'major', 'course', 'city', 'phone',
            'github', 'linkedin', 'skills', 'about', 'resume_text',
            'ai_score', 'completion', 'updated_at',
        ]

    def get_completion(self, obj):
        return obj.completion_percent()
