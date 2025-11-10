# portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage, ProjectTag


# ---------- Inline לתמונות של פרויקט ----------
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "caption", "thumb")       # thumb לקריאה בלבד
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        if getattr(obj, "image", None) and getattr(obj.image, "url", None):
            return format_html('<img src="{}" style="height:60px;border-radius:8px;" />', obj.image.url)
        return "—"


# ---------- Project ----------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "cover_thumb", "title", "owner", "is_public", "created_at")
    list_display_links = ("id", "title")
    list_filter = ("is_public", "created_at")
    search_fields = ("title", "summary", "owner__email")
    readonly_fields = ("created_at", "cover_thumb")
    inlines = [ProjectImageInline]

    fieldsets = (
        ("מידע כללי", {"fields": ("owner", "title", "summary", "is_public")}),
        ("קישורים", {"fields": ("repo_url", "demo_url")}),
        ("תמונת שער", {"fields": ("cover_image", "cover_thumb")}),  # תצוגה + קובץ
        ("פרטים נוספים", {"fields": ("tech_stack",)}),
        ("תאריך יצירה", {"fields": ("created_at",)}),
    )

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        if getattr(obj, "cover_image", None) and getattr(obj.cover_image, "url", None):
            return format_html('<img src="{}" style="height:48px;border-radius:8px;" />', obj.cover_image.url)
        return "—"


# ---------- ProjectImage ----------
@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "caption", "thumb")
    search_fields = ("caption", "project__title")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        if getattr(obj, "image", None) and getattr(obj.image, "url", None):
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.image.url)
        return "—"


# ---------- Tags ----------
@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

