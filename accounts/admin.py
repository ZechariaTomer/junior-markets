from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, SeekerProfile, SeekerExperience, SeekerEducation, RecruiterProfile
)


class SeekerExperienceInline(admin.TabularInline):
    model = SeekerExperience
    extra = 0
    fields = ("company", "title", "start_date", "end_date", "is_current")


class SeekerEducationInline(admin.TabularInline):
    model = SeekerEducation
    extra = 0
    fields = ("school", "degree", "start_year", "end_year")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "role_badge",
        "is_staff",
        "is_active",
        "date_joined"
    )
    
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
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
    
    readonly_fields = ("date_joined", "last_login")
    
    def role_badge(self, obj):
        colors = {
            'NONE': '#6c757d',
            'SEEKER': '#28a745',
            'RECRUITER': '#007bff',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'תפקיד'


@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "headline",
        "years_experience",
        "desired_level",
        "is_open_to_remote",
        "updated_at"
    )
    
    search_fields = ("user__email", "full_name", "skills", "headline")
    list_filter = ("years_experience", "desired_level", "is_open_to_remote", "updated_at")
    inlines = [SeekerExperienceInline, SeekerEducationInline]
    
    readonly_fields = ("updated_at",)
    
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Personal Info", {"fields": ("full_name", "phone", "location")}),
        ("Links", {"fields": ("linkedin", "github", "portfolio")}),
        ("Professional", {"fields": ("headline", "years_experience", "skills", "languages", "about")}),
        ("Resume", {"fields": ("resume",)}),
        ("Preferences", {"fields": ("desired_level", "is_open_to_remote", "desired_salary_nis")}),
        ("Meta", {"fields": ("updated_at",)}),
    )


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "company_name",
        "contact_name",
        "phone",
        "company_location",
        "updated_at"
    )
    
    search_fields = ("user__email", "company_name", "contact_name", "company_location")
    list_filter = ("company_size", "company_location", "updated_at")
    
    readonly_fields = ("updated_at",)
    
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Contact", {"fields": ("contact_name", "phone")}),
        ("Company", {"fields": ("company_name", "company_website", "company_size", "company_location", "company_logo")}),
        ("About", {"fields": ("about_company", "notes")}),
        ("Meta", {"fields": ("updated_at",)}),
    )