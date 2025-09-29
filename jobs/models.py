
from django.db import models
from django.conf import settings  # תמיד להשתמש ב-AUTH_USER_MODEL

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_posted",
        verbose_name="מפרסם המשרה",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="משרה",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
        verbose_name="מועמד",
    )
    cover_letter = models.TextField(blank=True, verbose_name="מכתב מקדים")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "applicant")  # מונע הגשה כפולה לאותה משרה
        ordering = ["-created_at"]  # ברירת מחדל: הכי חדשות ראשונות

    def __str__(self):
        name = getattr(self.applicant, "email", getattr(self.applicant, "username", "user"))
        return f"{name} → {self.job.title}"

