from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class JobManager(models.Manager):
    """Custom manager למשרות"""
    
    def active(self):
        """משרות פתוחות ולא פגות תוקף"""
        return self.filter(
            status='open'
        ).exclude(
            deadline__lt=timezone.now()
        )
    
    def featured(self):
        """משרות מומלצות"""
        return self.filter(status='open')
    
    def for_seeker(self):
        """משרות שאפשר להגיש אליהן"""
        return self.active()


class Job(models.Model):
    """משרה/משימה שמפורסמת על ידי מגייס"""
    
    # Choices
    STATUS_CHOICES = [
        ('draft', _('טיוטה')),
        ('open', _('פתוח')),
        ('closed', _('סגור')),
        ('filled', _('אויש')),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', _('קל')),
        ('medium', _('בינוני')),
        ('hard', _('קשה')),
    ]
    
    # Fields
    title = models.CharField(
        _("כותרת"),
        max_length=200,
        validators=[MinLengthValidator(5, _("כותרת חייבת להיות לפחות 5 תווים"))]
    )
    description = models.TextField(
        _("תיאור"),
        validators=[MinLengthValidator(20, _("תיאור חייב להיות לפחות 20 תווים"))]
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_posted",
        verbose_name=_("מפרסם המשרה"),
    )
    status = models.CharField(
        _("סטטוס"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    difficulty = models.CharField(
        _("רמת קושי"),
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        blank=True
    )
    deadline = models.DateTimeField(
        _("תאריך יעד"),
        null=True,
        blank=True
    )
    max_applicants = models.PositiveIntegerField(
        _("מספר מקסימלי של מועמדים"),
        default=10,
        help_text=_("כמה מועמדים מקסימום יכולים להגיש מועמדות")
    )
    
    # Timestamps
    created_at = models.DateTimeField(_("נוצר ב"), auto_now_add=True)
    updated_at = models.DateTimeField(_("עודכן ב"), auto_now=True)

    objects = JobManager()  # ← עכשיו זה יעבוד!

    class Meta:
        verbose_name = _("משרה")
        verbose_name_plural = _("משרות")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title
    
    def is_expired(self):
        """בדיקה אם המשרה פג תוקפה"""
        if self.deadline:
            return timezone.now() > self.deadline
        return False
    
    def can_apply(self):
        """בדיקה אם אפשר להגיש מועמדות"""
        if self.status != 'open':
            return False
        if self.is_expired():
            return False
        if self.applications.count() >= self.max_applicants:
            return False
        return True
    
    def applications_count(self):
        """מספר המועמדויות למשרה"""
        return self.applications.count()
    applications_count.short_description = _("מספר מועמדויות")


class Application(models.Model):
    """מועמדות למשרה"""
    
    STATUS_CHOICES = [
        ('pending', _('ממתין')),
        ('accepted', _('התקבל')),
        ('rejected', _('נדחה')),
        ('withdrawn', _('משך מועמדות')),
    ]
    
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("משרה"),
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
        verbose_name=_("מועמד"),
    )
    cover_letter = models.TextField(
        _("מכתב מקדים"),
        blank=True,
        help_text=_("למה אתה מתאים למשרה?")
    )
    status = models.CharField(
        _("סטטוס"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_("הוגש ב"), auto_now_add=True)
    reviewed_at = models.DateTimeField(_("נבדק ב"), null=True, blank=True)

    class Meta:
        verbose_name = _("מועמדות")
        verbose_name_plural = _("מועמדויות")
        unique_together = ("job", "applicant")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['applicant', '-created_at']),
            models.Index(fields=['job', 'status']),
        ]

    def __str__(self):
        name = getattr(self.applicant, "email", getattr(self.applicant, "username", "user"))
        return f"{name} → {self.job.title}"