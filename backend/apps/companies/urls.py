from django.urls import path
from .views import CompanyMeView

app_name = 'companies'

urlpatterns = [
    path('companies/me/', CompanyMeView.as_view(), name='company-me'),
]
