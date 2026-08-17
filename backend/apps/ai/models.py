from django.db import models
from django.contrib.auth.models import User

class AIFeatureType(models.TextChoices):
    RESUME_ANALYSIS = 'resume_analysis', 'Анализ резюме'
    RESUME_ENHANCEMENT = 'resume_enhancement', 'Улучшение резюме'
    VACANCY_MATCHING = 'vacancy_matching', 'Подбор вакансий'
    COVER_LETTER = 'cover_letter', 'Письмо'
    INTERVIEW_PREP = 'interview_prep', 'Подготовка'
    SKILL_GAP = 'skill_gap', 'Пробелы в навыках'
    CAREER_COACH = 'career_coach', 'Карьерный коуч'
    JOB_RECOMMENDATIONS = 'job_recommendations', 'Рекомендации'
    ASSISTANT = 'assistant', 'Ассистент'
    RESUME_IMPORT = 'resume_import', 'Импорт резюме'
    HH_ADAPT = 'hh_adapt_resume', 'Адаптация под вакансию'


class AiActionLogStatus(models.TextChoices):
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    DEMO = 'demo', 'Demo mode'


class AiActionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_action_logs',
    )
    student_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    user_login = models.CharField(max_length=150, blank=True, db_index=True)
    feature = models.CharField(max_length=32, db_index=True)
    endpoint = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16,
        choices=AiActionLogStatus.choices,
        default=AiActionLogStatus.SUCCESS,
        db_index=True,
    )
    model_name = models.CharField(max_length=64, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    request_payload = models.JSONField(default=dict, blank=True)
    ai_input = models.JSONField(default=dict, blank=True)
    ai_output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ai_action_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feature', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user_login or self.user_id} {self.feature} ({self.status})"


class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_analyses')
    resume_url = models.URLField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    overall_score = models.IntegerField()
    key_skills = models.JSONField(default=list)
    experience_years = models.IntegerField()
    education_level = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']

class VacancyMatching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancy_matches')
    vacancy_id = models.CharField(max_length=255)
    match_score = models.IntegerField()
    skill_match = models.IntegerField()
    experience_match = models.IntegerField()
    education_match = models.IntegerField()
    location_match = models.IntegerField()
    missing_skills = models.JSONField(default=list)
    matching_skills = models.JSONField(default=list)
    explanation = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        unique_together = ['user', 'vacancy_id']

class CoverLetterGeneration(models.Model):
    TONE_CHOICES = (
        ('professional', 'Профессиональный'),
        ('friendly', 'Дружеский'),
        ('creative', 'Творческий'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letters')
    vacancy_id = models.CharField(max_length=255)
    cover_letter = models.TextField()
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)
    company = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    key_points = models.JSONField(default=list)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']

class InterviewPrep(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_preps')
    vacancy_id = models.CharField(max_length=255)
    questions = models.JSONField(default=list)
    tips = models.JSONField(default=list)
    estimated_duration = models.IntegerField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class SkillGapAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_gaps')
    target_role = models.CharField(max_length=255, null=True, blank=True)
    current_skills = models.JSONField(default=list)
    required_skills = models.JSONField(default=list)
    gap_skills = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    estimated_learning_time = models.IntegerField()
    resources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class CareerCoachChat(models.Model):
    MODE_CHOICES = (
        ('resume', 'Resume'),
        ('cover_letter', 'Cover letter'),
        ('interview', 'Interview prep'),
        ('mock_interview', 'Mock interview'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_coach_chats')
    topic = models.CharField(max_length=255)
    mode = models.CharField(max_length=32, choices=MODE_CHOICES, default='resume', db_index=True)
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class AIUsageStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_usage_stats')
    feature_usage = models.JSONField(default=dict)
    total_requests = models.IntegerField(default=0)
    credit_usage = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'AI Usage Statistics'