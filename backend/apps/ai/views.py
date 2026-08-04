"""
QalaJob AI — AI Feature Views

Real AI integration via OpenRouter API.
All endpoints use production LLM calls for:
- Resume analysis
- Vacancy matching
- Cover letter generation
- Interview preparation
- Skill gap analysis
- Career coaching chat
"""

import logging

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .models import (
    ResumeAnalysis,
    VacancyMatching,
    CoverLetterGeneration,
    InterviewPrep,
    SkillGapAnalysis,
    CareerCoachChat,
    AIUsageStatistics,
)
from .services.openai_client import (
    analyze_resume as ai_analyze_resume,
    match_vacancy as ai_match_vacancy,
    generate_cover_letter as ai_generate_cover_letter,
    prepare_interview as ai_prepare_interview,
    analyze_skill_gap as ai_analyze_skill_gap,
    career_coach_chat as ai_career_chat,
)

logger = logging.getLogger('apps')


class AIRateThrottle(UserRateThrottle):
    rate = '30/hour'


def _track_usage(user, feature_type: str):
    """Track AI feature usage for analytics."""
    stats, _ = AIUsageStatistics.objects.get_or_create(user=user)
    usage = stats.feature_usage or {}
    usage[feature_type] = usage.get(feature_type, 0) + 1
    stats.feature_usage = usage
    stats.total_requests += 1
    stats.save(update_fields=['feature_usage', 'total_requests', 'updated_at'])


class AIViewSet(viewsets.ViewSet):
    """
    AI-powered features for QalaJob AI.
    All endpoints require authentication and are rate-limited.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    @action(detail=False, methods=['post'], url_path='analyze-resume')
    def analyze_resume(self, request):
        """
        Analyze a resume with AI.

        POST /api/v1/ai/analyze-resume/
        {
            "resume_text": "...",
            "target_role": "Frontend Developer"
        }
        """
        resume_text = request.data.get('resume_text', '')
        target_role = request.data.get('target_role', '')

        if not resume_text:
            # Try to get from user profile
            try:
                from apps.profiles.models import StudentProfile
                profile = StudentProfile.objects.get(user=request.user)
                resume_text = profile.resume_text or ''
            except Exception:
                pass

        if not resume_text:
            return Response(
                {'message': 'Resume text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = ai_analyze_resume(resume_text, target_role)

            if not result:
                return Response(
                    {'message': 'AI service is temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Save analysis
            analysis = ResumeAnalysis.objects.create(
                user=request.user,
                resume_url='',
                strengths=result.get('strengths', []),
                weaknesses=result.get('weaknesses', []),
                suggestions=result.get('suggestions', []),
                overall_score=result.get('overall_score', 0),
                key_skills=result.get('key_skills', []),
                experience_years=result.get('experience_years', 0),
                education_level=result.get('education_level', ''),
            )

            _track_usage(request.user, 'resume_analysis')

            return Response({
                'id': analysis.id,
                'overall_score': result.get('overall_score', 0),
                'strengths': result.get('strengths', []),
                'weaknesses': result.get('weaknesses', []),
                'suggestions': result.get('suggestions', []),
                'key_skills': result.get('key_skills', []),
                'experience_years': result.get('experience_years', 0),
                'education_level': result.get('education_level', ''),
                'grammar_score': result.get('grammar_score', 0),
                'keywords_found': result.get('keywords_found', []),
                'missing_keywords': result.get('missing_keywords', []),
            })

        except Exception as e:
            logger.error(f"Resume analysis error: {e}")
            return Response(
                {'message': 'Error analyzing resume'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='match-vacancies')
    def match_vacancies(self, request):
        """
        Match user profile to a vacancy.

        POST /api/v1/ai/match-vacancies/
        {
            "vacancy_id": "123"
        }
        """
        vacancy_id = request.data.get('vacancy_id')

        if not vacancy_id:
            return Response(
                {'message': 'vacancy_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.vacancies.models import Vacancy
            from apps.profiles.models import StudentProfile

            vacancy = Vacancy.objects.get(id=vacancy_id)
            profile = StudentProfile.objects.get(user=request.user)

            candidate_data = {
                'skills': profile.skills or '',
                'experience': profile.resume_text or '',
                'education': f"{profile.university} - {profile.major}",
                'location': profile.city or '',
            }

            vacancy_data = {
                'title': vacancy.title,
                'requirements': vacancy.requirements or vacancy.description,
                'skills': vacancy.skills or '',
                'location': vacancy.city or '',
                'type': vacancy.job_type or '',
            }

            result = ai_match_vacancy(candidate_data, vacancy_data)

            if not result:
                return Response(
                    {'message': 'AI service is temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Save match
            match_obj, _ = VacancyMatching.objects.update_or_create(
                user=request.user,
                vacancy_id=str(vacancy_id),
                defaults={
                    'match_score': result.get('match_score', 0),
                    'skill_match': result.get('skill_match', 0),
                    'experience_match': result.get('experience_match', 0),
                    'education_match': result.get('education_match', 0),
                    'location_match': result.get('location_match', 0),
                    'missing_skills': result.get('missing_skills', []),
                    'matching_skills': result.get('matching_skills', []),
                    'explanation': result.get('explanation', ''),
                },
            )

            _track_usage(request.user, 'vacancy_matching')

            return Response({
                'id': match_obj.id,
                **result,
            })

        except Vacancy.DoesNotExist:
            return Response(
                {'message': 'Vacancy not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {'message': 'Please complete your profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Vacancy matching error: {e}")
            return Response(
                {'message': 'Error matching vacancy'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='generate-cover-letter')
    def generate_cover_letter(self, request):
        """
        Generate a cover letter with AI.

        POST /api/v1/ai/generate-cover-letter/
        {
            "vacancy_id": "123",
            "tone": "professional"
        }
        """
        vacancy_id = request.data.get('vacancy_id')
        tone = request.data.get('tone', 'professional')

        if not vacancy_id:
            return Response(
                {'message': 'vacancy_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.vacancies.models import Vacancy
            from apps.profiles.models import StudentProfile

            vacancy = Vacancy.objects.get(id=vacancy_id)
            profile = StudentProfile.objects.get(user=request.user)

            candidate_data = {
                'name': profile.name or request.user.first_name,
                'skills': profile.skills or '',
                'experience': profile.resume_text or '',
            }

            vacancy_data = {
                'title': vacancy.title,
                'company': vacancy.company_name,
                'description': vacancy.description,
            }

            result = ai_generate_cover_letter(candidate_data, vacancy_data, tone)

            if not result:
                return Response(
                    {'message': 'AI service is temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Save
            cover = CoverLetterGeneration.objects.create(
                user=request.user,
                vacancy_id=str(vacancy_id),
                cover_letter=result.get('cover_letter', ''),
                tone=tone,
                company=vacancy.company_name,
                position=vacancy.title,
                key_points=result.get('key_points', []),
            )

            _track_usage(request.user, 'cover_letter')

            return Response({
                'id': cover.id,
                'cover_letter': result.get('cover_letter', ''),
                'key_points': result.get('key_points', []),
            })

        except Exception as e:
            logger.error(f"Cover letter generation error: {e}")
            return Response(
                {'message': 'Error generating cover letter'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='interview-preparation')
    def interview_preparation(self, request):
        """
        Generate interview prep materials.

        POST /api/v1/ai/interview-preparation/
        {
            "vacancy_id": "123",
            "difficulty": "medium"
        }
        """
        vacancy_id = request.data.get('vacancy_id')
        difficulty = request.data.get('difficulty', 'medium')

        if not vacancy_id:
            return Response(
                {'message': 'vacancy_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.vacancies.models import Vacancy
            vacancy = Vacancy.objects.get(id=vacancy_id)

            vacancy_data = {
                'title': vacancy.title,
                'company': vacancy.company_name,
                'requirements': vacancy.requirements or vacancy.description,
            }

            result = ai_prepare_interview(vacancy_data, difficulty)

            if not result:
                return Response(
                    {'message': 'AI service is temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Save
            prep = InterviewPrep.objects.create(
                user=request.user,
                vacancy_id=str(vacancy_id),
                questions=result.get('questions', []),
                tips=result.get('tips', []),
                estimated_duration=result.get('estimated_duration', 45),
                difficulty=difficulty,
            )

            _track_usage(request.user, 'interview_prep')

            return Response({
                'id': prep.id,
                'questions': result.get('questions', []),
                'tips': result.get('tips', []),
                'estimated_duration': result.get('estimated_duration', 45),
            })

        except Exception as e:
            logger.error(f"Interview prep error: {e}")
            return Response(
                {'message': 'Error generating interview prep'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='analyze-skill-gap')
    def analyze_skill_gap(self, request):
        """
        Analyze skill gap for a target role.

        POST /api/v1/ai/analyze-skill-gap/
        {
            "target_role": "Frontend Developer"
        }
        """
        target_role = request.data.get('target_role', '')

        if not target_role:
            return Response(
                {'message': 'target_role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.profiles.models import StudentProfile
            profile = StudentProfile.objects.get(user=request.user)

            skills_raw = profile.skills or ''
            current_skills = [s.strip() for s in skills_raw.split(',') if s.strip()]

            result = ai_analyze_skill_gap(current_skills, target_role)

            if not result:
                return Response(
                    {'message': 'AI service is temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Save
            gap = SkillGapAnalysis.objects.create(
                user=request.user,
                target_role=target_role,
                current_skills=result.get('current_skills', current_skills),
                required_skills=result.get('required_skills', []),
                gap_skills=result.get('gap_skills', []),
                recommendations=result.get('recommendations', []),
                estimated_learning_time=result.get('estimated_learning_time', 0),
                resources=result.get('priority_order', []),
            )

            _track_usage(request.user, 'skill_gap')

            return Response({
                'id': gap.id,
                **result,
            })

        except StudentProfile.DoesNotExist:
            return Response(
                {'message': 'Please complete your profile first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Skill gap analysis error: {e}")
            return Response(
                {'message': 'Error analyzing skill gap'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='career-coach-chat')
    def career_coach(self, request):
        """
        Start or continue a career coaching chat (legacy ViewSet path).
        Prefer POST /api/v1/ai/career-coach/ instead.
        """
        message = request.data.get('message', '')
        chat_id = request.data.get('chat_id')
        language = (
            request.data.get('language')
            or request.headers.get('Accept-Language', 'kk').split(',')[0].strip()
            or 'kk'
        )

        if not message:
            return Response(
                {'message': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if chat_id:
                chat = CareerCoachChat.objects.get(id=chat_id, user=request.user)
            else:
                chat = CareerCoachChat.objects.create(
                    user=request.user,
                    topic=message[:100],
                    messages=[],
                )

            messages = chat.messages or []
            messages.append({
                'role': 'user',
                'content': message,
                'timestamp': timezone.now().isoformat(),
            })

            reply = ai_career_chat(message, messages, language=language)

            if not reply:
                reply = "I'm sorry, I'm temporarily unavailable. Please try again in a moment."

            messages.append({
                'role': 'assistant',
                'content': reply,
                'timestamp': timezone.now().isoformat(),
            })

            chat.messages = messages
            chat.save(update_fields=['messages', 'updated_at'])

            _track_usage(request.user, 'career_coach')

            return Response({
                'chat_id': chat.id,
                'reply': reply,
                'messages': messages,
            })

        except CareerCoachChat.DoesNotExist:
            return Response(
                {'message': 'Chat not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Career coach error: {e}")
            return Response(
                {'message': 'Error in career coach'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='usage-stats')
    def usage_stats(self, request):
        """Get user's AI usage statistics."""
        try:
            stats, _ = AIUsageStatistics.objects.get_or_create(user=request.user)
            return Response({
                'feature_usage': stats.feature_usage,
                'total_requests': stats.total_requests,
                'credit_usage': stats.credit_usage,
            })
        except Exception as e:
            logger.error(f"Usage stats error: {e}")
            return Response(
                {'message': 'Error fetching usage stats'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """Get AI analysis history."""
        feature = request.query_params.get('feature', 'all')

        try:
            data = {}

            if feature in ('all', 'resume'):
                analyses = ResumeAnalysis.objects.filter(user=request.user)[:5]
                data['resume_analyses'] = [
                    {
                        'id': a.id,
                        'overall_score': a.overall_score,
                        'generated_at': a.generated_at,
                    }
                    for a in analyses
                ]

            if feature in ('all', 'matching'):
                matches = VacancyMatching.objects.filter(user=request.user)[:10]
                data['vacancy_matches'] = [
                    {
                        'id': m.id,
                        'vacancy_id': m.vacancy_id,
                        'match_score': m.match_score,
                        'generated_at': m.generated_at,
                    }
                    for m in matches
                ]

            if feature in ('all', 'chats'):
                chats = CareerCoachChat.objects.filter(user=request.user)[:10]
                data['career_chats'] = [
                    {
                        'id': c.id,
                        'topic': c.topic,
                        'message_count': len(c.messages or []),
                        'created_at': c.created_at,
                    }
                    for c in chats
                ]

            return Response(data)

        except Exception as e:
            logger.error(f"AI history error: {e}")
            return Response(
                {'message': 'Error fetching history'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )