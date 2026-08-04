from django.urls import path
from .views import ProfileMeView

app_name = 'profiles'

urlpatterns = [
    path('profiles/me/', ProfileMeView.as_view(), name='profile-me'),
]
