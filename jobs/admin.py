# jobs/admin.py
from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "posted_by", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "description", "posted_by__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "applicant", "created_at")
    list_filter = ("created_at", "job")
    search_fields = ("job__title", "applicant__email", "cover_letter")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

