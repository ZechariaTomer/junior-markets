from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.core.validators import MinValueValidator, RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

phone_validator = RegexValidator(
    regex=r"^[0-9+\-() ]{7,20}$",
    message=_("מספר טלפון לא תקין")
)

class Roles(models.TextChoices):
    NONE = "NONE", _("לא נבחר")
    SEEKER = "SEEKER", _("מחפש עבודה")
    RECRUITER = "RECRUITER", _("מגייס")

# --- מנהל מותאם שעובד עם אימייל בלבד ---
class CustomUserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        # נגזור username אם לא סופק (משמש לתאימות פנימית של Django Admin)
        username = extra_fields.pop("username", None) or email[:150]
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(_("אימייל"), unique=True)
    role = models.CharField(_("תפקיד"), max_length=16, choices=Roles.choices, default=Roles.NONE)

    USERNAME_FIELD = "email"   # התחברות עם אימייל
    REQUIRED_FIELDS = []       # לא נבקש username בעת יצירה

    # מחליפים את המנהל לברירת מחדל המותאמת
    objects = CustomUserManager()

    # fallback: אם משום מה נוצר בלי username, נמלא מהאימייל
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email[:150]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username

# -------- מחפש עבודה --------
class SeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seeker_profile")
    full_name = models.CharField(_("שם מלא"), max_length=120, blank=True)
    phone = models.CharField(_("טלפון"), max_length=30, validators=[phone_validator], blank=True)
    location = models.CharField(_("אזור מגורים"), max_length=120, blank=True)
    linkedin = models.URLField(_("LinkedIn"), blank=True)
    github = models.URLField(_("GitHub"), blank=True)
    portfolio = models.URLField(_("Portfolio / Site"), blank=True)
    headline = models.CharField(_("כותרת מקצועית"), max_length=160, blank=True, help_text=_("למשל: Full-Stack Developer (Python/React)"))
    years_experience = models.PositiveIntegerField(_("שנות ניסיון"), default=0, validators=[MinValueValidator(0)])
    skills = models.TextField(_("מיומנויות (מופרדות בפסיק)"), blank=True)
    languages = models.TextField(_("שפות (מופרדות בפסיק)"), blank=True)
    about = models.TextField(_("על עצמי"), blank=True)
    resume = models.FileField(_("קורות חיים (PDF)"), upload_to="resumes/", blank=True, null=True)
    ROLE_LEVELS = [("JUNIOR", "Junior"), ("MID", "Mid"), ("SENIOR", "Senior"), ("INTERN", "Intern")]
    desired_level = models.CharField(_("רמה רצויה"), max_length=16, choices=ROLE_LEVELS, blank=True)
    is_open_to_remote = models.BooleanField(_("פתוח לעבודה מרחוק"), default=True)
    desired_salary_nis = models.PositiveIntegerField(_("שכר מבוקש (₪)"), null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SeekerProfile<{self.user.email}>"

class SeekerExperience(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE, related_name="experiences")
    company = models.CharField(_("חברה"), max_length=160)
    title = models.CharField(_("תפקיד"), max_length=160)
    start_date = models.DateField(_("תאריך התחלה"))
    end_date = models.DateField(_("תאריך סיום"), null=True, blank=True)
    is_current = models.BooleanField(_("משרה נוכחית"), default=False)
    description = models.TextField(_("תיאור/הישגים"), blank=True)
    tech_stack = models.CharField(_("סטאק טכנולוגי (פסיקים)"), max_length=300, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        if self.end_date:
            return f"{self.title} @ {self.company} ({self.start_date:%Y}-{self.end_date:%Y})"
        return f"{self.title} @ {self.company} ({self.start_date:%Y}-Present)"

class SeekerEducation(models.Model):
    seeker = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE, related_name="education")
    school = models.CharField(_("מוסד לימודים"), max_length=160)
    degree = models.CharField(_("תואר/מסלול"), max_length=160)
    start_year = models.PositiveIntegerField(_("שנת התחלה"), null=True, blank=True)
    end_year = models.PositiveIntegerField(_("שנת סיום"), null=True, blank=True)
    notes = models.CharField(_("הערות"), max_length=300, blank=True)

    class Meta:
        ordering = ["-end_year", "-start_year"]

    def __str__(self):
        return f"{self.degree} - {self.school}"

# -------- מגייס/ת --------
class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recruiter_profile")
    contact_name = models.CharField(_("שם איש קשר"), max_length=120, blank=True)
    phone = models.CharField(_("טלפון"), max_length=30, validators=[phone_validator], blank=True)
    company_name = models.CharField(_("שם חברה"), max_length=160, blank=True)
    company_website = models.URLField(_("אתר חברה"), blank=True, validators=[URLValidator()])
    company_size = models.CharField(_("גודל חברה (טקסט חופשי)"), max_length=80, blank=True)
    company_location = models.CharField(_("מיקום חברה"), max_length=120, blank=True)
    company_logo = models.ImageField(_("לוגו חברה"), upload_to="company_logos/", blank=True, null=True)
    about_company = models.TextField(_("אודות החברה"), blank=True)
    notes = models.TextField(_("העדפות/הערות גיוס"), blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RecruiterProfile<{self.user.email}>"
