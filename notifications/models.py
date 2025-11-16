from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Types(models.TextChoices):
        APPLICATION_RECEIVED = "APPLICATION_RECEIVED", "Application received"
        APPLICATION_STATUS   = "APPLICATION_STATUS",   "Application status update"
        GENERAL              = "GENERAL",              "General"

    to_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type      = models.CharField(max_length=40, choices=Types.choices)
    title     = models.CharField(max_length=120)
    message   = models.TextField(blank=True)
    payload   = models.JSONField(default=dict, blank=True)  # לדוגמה: {"job_id":1,"application_id":10,"status":"PENDING"}
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.to_user_id} · {self.type} · {self.title[:30]}"
