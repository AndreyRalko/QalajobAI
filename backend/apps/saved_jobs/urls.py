from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SavedHhVacancyViewSet, SavedJobViewSet

router = DefaultRouter()
router.register(r"saved-jobs", SavedJobViewSet, basename="saved-job")
router.register(r"hh-saved", SavedHhVacancyViewSet, basename="hh-saved")

app_name = "saved_jobs"

urlpatterns = [
    path("", include(router.urls)),
]
