from django.db import models
from django.contrib.auth.models import User
from apps.vacancies.models import Vacancy


class SavedJob(models.Model):
    """Bookmark for internal platform vacancies."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "vacancy"]
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.email} saved {self.vacancy.title}"


class SavedHhVacancy(models.Model):
    """Saved HeadHunter vacancy used as AI personalization context."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_hh_vacancies",
    )
    hh_id = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=120, blank=True)
    salary = models.CharField(max_length=120, blank=True)
    url = models.URLField(blank=True, max_length=500)
    description = models.TextField(blank=True)
    is_selected = models.BooleanField(default=False, db_index=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "saved_hh_vacancies"
        unique_together = ["user", "hh_id"]
        ordering = ["-is_selected", "-saved_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def select_for_user(self):
        """Mark this vacancy as the active AI context; clear others."""
        type(self).objects.filter(user=self.user, is_selected=True).exclude(
            pk=self.pk
        ).update(is_selected=False)
        if not self.is_selected:
            self.is_selected = True
            self.save(update_fields=["is_selected", "updated_at"])
