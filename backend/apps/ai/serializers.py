from rest_framework import serializers
from .models import (
    ResumeAnalysis,
    VacancyMatching,
    CoverLetterGeneration,
    InterviewPrep,
    SkillGapAnalysis,
    CareerCoachChat,
    AIUsageStatistics
)

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = [
            'id', 'user', 'resume_url', 'strengths', 'weaknesses',
            'suggestions', 'overall_score', 'key_skills',
            'experience_years', 'education_level', 'generated_at', 'expires_at'
        ]
        read_only_fields = ['id', 'user', 'generated_at']

class VacancyMatchingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyMatching
        fields = [
            'id', 'user', 'vacancy_id', 'match_score', 'skill_match',
            'experience_match', 'education_match', 'location_match',
            'missing_skills', 'matching_skills', 'explanation', 'generated_at'
        ]
        read_only_fields = ['id', 'user', 'generated_at']

class CoverLetterGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetterGeneration
        fields = [
            'id', 'user', 'vacancy_id', 'cover_letter', 'tone',
            'company', 'position', 'key_points', 'generated_at'
        ]
        read_only_fields = ['id', 'user', 'generated_at']

class InterviewPrepSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewPrep
        fields = [
            'id', 'user', 'vacancy_id', 'questions', 'tips',
            'estimated_duration', 'difficulty', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class SkillGapAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillGapAnalysis
        fields = [
            'id', 'user', 'target_role', 'current_skills', 'required_skills',
            'gap_skills', 'recommendations', 'estimated_learning_time',
            'resources', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class CareerCoachChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerCoachChat
        fields = [
            'id', 'user', 'topic', 'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class AIUsageStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageStatistics
        fields = [
            'id', 'user', 'feature_usage', 'total_requests',
            'credit_usage', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'updated_at']

# Request serializers for API endpoints

class ResumeAnalysisRequestSerializer(serializers.Serializer):
    resume_url = serializers.URLField(
        help_text="URL к файлу резюме"
    )
    
    class Meta:
        fields = ['resume_url']

class VacancyMatchingRequestSerializer(serializers.Serializer):
    vacancy_id = serializers.CharField(
        max_length=255,
        help_text="ID вакансии для сравнения"
    )
    
    class Meta:
        fields = ['vacancy_id']

class CoverLetterRequestSerializer(serializers.Serializer):
    TONE_CHOICES = [
        ('professional', 'Профессиональный'),
        ('friendly', 'Дружеский'),
        ('creative', 'Творческий'),
    ]
    
    vacancy_id = serializers.CharField(max_length=255)
    tone = serializers.ChoiceField(choices=TONE_CHOICES, default='professional')
    company = serializers.CharField(max_length=255, required=False)
    position = serializers.CharField(max_length=255, required=False)

class InterviewPrepRequestSerializer(serializers.Serializer):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]
    
    vacancy_id = serializers.CharField(max_length=255)
    difficulty = serializers.ChoiceField(choices=DIFFICULTY_CHOICES, default='medium')

class SkillGapAnalysisRequestSerializer(serializers.Serializer):
    target_role = serializers.CharField(
        max_length=255,
        help_text="Целевая должность"
    )

class CareerCoachChatRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(
        max_length=255,
        help_text="Тема для обсуждения с AI коучем"
    )
    message = serializers.CharField(
        help_text="Первое сообщение или вопрос"
    )

class CareerCoachMessageSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    message = serializers.CharField(
        help_text="Сообщение для AI коуча"
    )