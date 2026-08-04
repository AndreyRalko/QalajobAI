from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AIViewSet
from .api_views import (
    AssistantChatView,
    CareerCoachView,
    CoverLetterFreeView,
    HhAdaptResumeView,
    HhVacancyDetailView,
    HhVacancySearchView,
    ImportResumeView,
    InterviewPrepFreeView,
    ResumeAssistantView,
    ResumeEnhanceView,
)

router = DefaultRouter()
router.register(r'', AIViewSet, basename='ai')

app_name = 'ai'

urlpatterns = [
    path('career-coach/', CareerCoachView.as_view(), name='career-coach'),
    path('resume-assistant/', ResumeAssistantView.as_view(), name='resume-assistant'),
    path('assistant/', AssistantChatView.as_view(), name='assistant'),
    path('resume-enhance/', ResumeEnhanceView.as_view(), name='resume-enhance'),
    path('cover-letter/', CoverLetterFreeView.as_view(), name='cover-letter-free'),
    path('interview-prep/', InterviewPrepFreeView.as_view(), name='interview-prep-free'),
    path('import-resume/', ImportResumeView.as_view(), name='import-resume'),
    path('hh/vacancies/', HhVacancySearchView.as_view(), name='hh-vacancies-search'),
    path(
        'hh/vacancies/<str:vacancy_id>/',
        HhVacancyDetailView.as_view(),
        name='hh-vacancy-detail',
    ),
    path('hh/adapt-resume/', HhAdaptResumeView.as_view(), name='hh-adapt-resume'),
    path('', include(router.urls)),
]
