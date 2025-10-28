# jobs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "posted_by",
        "status_badge",
        "difficulty",
        "applications_count",
        "deadline",
        "created_at",
        "updated_at"
    )
    
    list_filter = (
        "status",
        "difficulty",
        "created_at",
        "updated_at"
    )
    
    search_fields = ("title", "description", "posted_by__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    
    readonly_fields = (
        "created_at",
        "updated_at",
        "applications_count",
    )
    
    fields = (
        "title",
        "description",
        "posted_by",
        "status",
        "difficulty",
        "deadline",
        "max_applicants",
        "created_at",
        "updated_at",
        "applications_count",
    )
    
    list_per_page = 25
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'open': '#28a745',
            'closed': '#dc3545',
            'filled': '#007bff',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'סטטוס'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "applicant",
        "status_badge",
        "created_at",
        "reviewed_at"
    )
    
    list_filter = (
        "status",
        "created_at",
        "job"
    )
    
    search_fields = ("job__title", "applicant__email", "cover_letter")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    
    readonly_fields = ("created_at",)
    
    fields = (
        "job",
        "applicant",
        "cover_letter",
        "status",
        "created_at",
        "reviewed_at",
    )
    
    list_per_page = 25
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545',
            'withdrawn': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'סטטוס'