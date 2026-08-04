from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet
from .api_views import ApplyView, StudentApplicationsView, EmployerApplicationsView

router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')

app_name = 'applications'

urlpatterns = [
    path('applications/apply/', ApplyView.as_view(), name='apply'),
    path('applications/student/', StudentApplicationsView.as_view(), name='student-applications'),
    path('applications/employer/', EmployerApplicationsView.as_view(), name='employer-applications'),
    path('', include(router.urls)),
]
