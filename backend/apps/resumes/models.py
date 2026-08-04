from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume')
    content = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    ai_analysis = models.JSONField(default=dict, blank=True)
    ai_score = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume: {self.user.email}"
