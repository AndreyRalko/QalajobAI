from django.db import models
from django.contrib.auth.models import User
from apps.vacancies.models import Vacancy


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'vacancy']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.email} saved {self.vacancy.title}"
