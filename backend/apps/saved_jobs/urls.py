from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SavedJobViewSet

router = DefaultRouter()
router.register(r'saved-jobs', SavedJobViewSet, basename='saved-job')

app_name = 'saved_jobs'

urlpatterns = [
    path('', include(router.urls)),
]
