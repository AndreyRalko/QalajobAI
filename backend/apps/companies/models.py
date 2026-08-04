from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.company_name

    def completion_percent(self):
        fields = [
            self.company_name, self.industry, self.location,
            self.website, self.company_size, self.description, self.logo,
        ]
        filled = sum(1 for f in fields if f)
        return round((filled / len(fields)) * 100)
