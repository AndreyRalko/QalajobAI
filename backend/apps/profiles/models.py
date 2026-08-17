from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    name = models.CharField(max_length=150, blank=True)
    university = models.CharField(max_length=200, blank=True)
    major = models.CharField(max_length=200, blank=True)
    course = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    skills = models.JSONField(default=list, blank=True)
    about = models.TextField(blank=True)

    resume_text = models.TextField(blank=True)

    ai_score = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def completion_percent(self) -> int:
        fields = [
            self.name,
            self.university,
            self.major,
            self.city,
            self.skills,
            self.about,
        ]
        filled = sum(
            1
            for value in fields
            if value and (len(value) > 0 if isinstance(value, list) else True)
        )
        return round(filled / len(fields) * 100)

    def __str__(self):
        return self.name or self.user.email


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employer_profile"
    )

    full_name = models.CharField(max_length=150, blank=True)

    position = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    about = models.TextField(blank=True)

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name or self.user.email


class AdminProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )

    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    department = models.CharField(
        max_length=150,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name or self.user.email