from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, SeekerProfile, SeekerExperience, SeekerEducation, RecruiterProfile
)

# ---------- Inlines למחפש עבודה ----------
class SeekerExperienceInline(admin.TabularInline):
    model = SeekerExperience
    extra = 1


class SeekerEducationInline(admin.TabularInline):
    model = SeekerEducation
    extra = 1


# ---------- משתמש ----------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "username", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Profile", {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )


# ---------- פרופיל מחפש עבודה ----------
@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "headline", "years_experience", "updated_at")
    search_fields = ("user__email", "full_name", "skills", "headline")
    list_filter = ("years_experience", "desired_level", "is_open_to_remote")
    inlines = [SeekerExperienceInline, SeekerEducationInline]


# ---------- פרופיל מגייס ----------
@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company_name", "contact_name", "company_location", "updated_at")
    search_fields = ("user__email", "company_name", "contact_name")
    list_filter = ("company_location", "company_size")
