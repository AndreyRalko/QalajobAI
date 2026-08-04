from django.urls import path
from .views import ResumeMeView

app_name = 'resumes'

urlpatterns = [
    path('resumes/me/', ResumeMeView.as_view(), name='resume-me'),
]
